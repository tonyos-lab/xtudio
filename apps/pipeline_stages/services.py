import logging

from django.db import transaction
from django.utils import timezone

from apps.pipeline_stages.exceptions import StageGateError, StageLockedError

logger = logging.getLogger("pipeline_stages")


class StageService:
    @staticmethod
    def create_instance(pipeline_code: str, object_type: str, object_id: str):
        """Create a new pipeline instance with all stage instances."""
        from apps.pipeline_stages.models import PipelineDefinition, PipelineInstance, StageInstance

        pipeline = PipelineDefinition.objects.get(code=pipeline_code)
        instance, _ = PipelineInstance.objects.get_or_create(
            pipeline=pipeline,
            object_type=object_type,
            object_id=object_id,
        )
        for stage_def in pipeline.stages.order_by("order"):
            StageInstance.objects.get_or_create(
                pipeline_instance=instance,
                stage_definition=stage_def,
                defaults={"status": StageInstance.STATUS_PENDING},
            )
        return instance

    @staticmethod
    def start_stage(pipeline_instance, stage_code: str):
        """Start a stage. Raises StageGateError if prerequisites not met."""
        from apps.pipeline_stages.models import StageInstance

        with transaction.atomic():
            stage_inst = StageInstance.objects.select_for_update().get(
                pipeline_instance=pipeline_instance,
                stage_definition__code=stage_code,
            )
            if stage_inst.status in (StageInstance.STATUS_LOCKED, StageInstance.STATUS_COMPLETE):
                raise StageLockedError(f"Stage '{stage_code}' is already complete.")

            stage_def = stage_inst.stage_definition
            if stage_def.is_hard_gate and stage_def.order > 1:
                prev = StageInstance.objects.filter(
                    pipeline_instance=pipeline_instance,
                    stage_definition__order=stage_def.order - 1,
                ).first()
                if prev and prev.status not in (
                    StageInstance.STATUS_LOCKED,
                    StageInstance.STATUS_COMPLETE,
                ):
                    raise StageGateError(
                        f"Stage '{stage_code}' requires previous stage to be complete. "
                        f"Current status: {prev.status}"
                    )

            stage_inst.status = StageInstance.STATUS_RUNNING
            stage_inst.started_at = timezone.now()
            stage_inst.save()
            return stage_inst

    @staticmethod
    def complete_stage(stage_instance, notes: str = ""):
        """Mark stage complete or awaiting approval."""
        from apps.pipeline_stages.models import StageInstance

        if stage_instance.status == StageInstance.STATUS_LOCKED:
            raise StageLockedError("Stage is already locked.")

        if stage_instance.stage_definition.requires_human_approval:
            stage_instance.status = StageInstance.STATUS_AWAITING_APPROVAL
        else:
            stage_instance.status = StageInstance.STATUS_LOCKED
            stage_instance.completed_at = timezone.now()

        stage_instance.notes = notes
        stage_instance.save()
        return stage_instance

    @staticmethod
    def fail_stage(stage_instance, notes: str = ""):
        """Mark stage as failed."""
        from apps.pipeline_stages.models import StageInstance

        stage_instance.status = StageInstance.STATUS_FAILED
        stage_instance.notes = notes
        stage_instance.save()
        return stage_instance

    @staticmethod
    def approve_stage(stage_instance, approved_by):
        """Human approves a stage awaiting approval."""
        from apps.pipeline_stages.models import StageInstance

        if stage_instance.status != StageInstance.STATUS_AWAITING_APPROVAL:
            raise StageGateError(
                f"Stage is not awaiting approval. Current status: {stage_instance.status}"
            )
        stage_instance.status = StageInstance.STATUS_LOCKED
        stage_instance.completed_at = timezone.now()
        stage_instance.approved_by = approved_by
        stage_instance.approved_at = timezone.now()
        stage_instance.save()
        return stage_instance

    @staticmethod
    def get_current_stage(pipeline_instance):
        """Return the current active stage instance."""
        from apps.pipeline_stages.models import StageInstance

        return StageInstance.objects.filter(
            pipeline_instance=pipeline_instance,
            status=StageInstance.STATUS_RUNNING,
        ).first()

    @staticmethod
    def get_stage(pipeline_instance, stage_code: str):
        """Return a specific stage instance by code."""
        from apps.pipeline_stages.models import StageInstance

        return StageInstance.objects.filter(
            pipeline_instance=pipeline_instance,
            stage_definition__code=stage_code,
        ).first()

    @staticmethod
    def is_stage_accessible(pipeline_instance, stage_code: str) -> bool:
        """Check if a stage can be started without raising."""
        try:
            StageService.start_stage(pipeline_instance, stage_code)
            return True
        except (StageGateError, StageLockedError):
            return False

    @staticmethod
    def get_pipeline_status(pipeline_instance) -> dict:
        """Return full status dict of all stages."""
        from apps.pipeline_stages.models import StageInstance

        stages = (
            StageInstance.objects.filter(pipeline_instance=pipeline_instance)
            .select_related("stage_definition")
            .order_by("stage_definition__order")
        )

        return {
            "pipeline_code": pipeline_instance.pipeline.code,
            "object_id": pipeline_instance.object_id,
            "is_complete": pipeline_instance.is_complete,
            "stages": [
                {
                    "code": s.stage_definition.code,
                    "label": s.stage_definition.label,
                    "order": s.stage_definition.order,
                    "status": s.status,
                    "requires_approval": s.stage_definition.requires_human_approval,
                }
                for s in stages
            ],
        }


class PipelineService:
    """
    High-level service for managing pipeline state from Phase 2+ code.
    Wraps StageService with project-ref-based lookups.
    """

    @staticmethod
    def advance(
        pipeline_code: str,
        stage_code: str,
        ref_id: str,
        ref_type: str = "project",
        user=None,
    ) -> None:
        """
        Advance the pipeline for the given ref to the specified stage.
        Creates the pipeline instance if it does not exist.
        Idempotent — safe to call even if stage already reached.
        Never raises — logs warnings on failure.
        """
        try:
            instance = StageService.create_instance(
                pipeline_code=pipeline_code,
                object_type=ref_type,
                object_id=str(ref_id),
            )
            stage_inst = StageService.get_stage(instance, stage_code)
            if stage_inst is None:
                logger.warning(
                    "PipelineService.advance: stage %s not found in %s", stage_code, pipeline_code
                )
                return
            from apps.pipeline_stages.models import StageInstance

            if stage_inst.status in (
                StageInstance.STATUS_LOCKED,
                StageInstance.STATUS_COMPLETE,
                StageInstance.STATUS_AWAITING_APPROVAL,
            ):
                return  # Already at or past this stage

            # Start then complete
            try:
                StageService.start_stage(instance, stage_code)
                stage_inst.refresh_from_db()
            except Exception:
                pass  # May already be running

            stage_inst.refresh_from_db()
            StageService.complete_stage(stage_inst)

            if user and stage_inst.stage_definition.requires_human_approval:
                stage_inst.refresh_from_db()
                StageService.approve_stage(stage_inst, approved_by=user)

        except Exception as exc:
            logger.warning(
                "PipelineService.advance failed for %s/%s: %s", pipeline_code, stage_code, exc
            )

    @staticmethod
    def is_stage_reached(
        pipeline_code: str, stage_code: str, ref_id: str, ref_type: str = "project"
    ) -> bool:
        """Return True if the given stage is locked/complete/awaiting approval."""
        try:
            from apps.pipeline_stages.models import (
                PipelineDefinition,
                PipelineInstance,
                StageInstance,
            )

            pipeline = PipelineDefinition.objects.filter(code=pipeline_code).first()
            if not pipeline:
                return False
            instance = PipelineInstance.objects.filter(
                pipeline=pipeline,
                object_type=ref_type,
                object_id=str(ref_id),
            ).first()
            if not instance:
                return False
            stage_inst = StageInstance.objects.filter(
                pipeline_instance=instance,
                stage_definition__code=stage_code,
            ).first()
            if not stage_inst:
                return False
            return stage_inst.status in (
                StageInstance.STATUS_LOCKED,
                StageInstance.STATUS_COMPLETE,
                StageInstance.STATUS_AWAITING_APPROVAL,
            )
        except Exception as exc:
            logger.warning("PipelineService.is_stage_reached failed: %s", exc)
            return False

    @staticmethod
    def get_current_stage(pipeline_code: str, ref_id: str, ref_type: str = "project") -> str:
        """Return the code of the most advanced reached stage, or '' if none."""
        try:
            from apps.pipeline_stages.models import (
                PipelineDefinition,
                PipelineInstance,
                StageInstance,
            )

            pipeline = PipelineDefinition.objects.filter(code=pipeline_code).first()
            if not pipeline:
                return ""
            instance = PipelineInstance.objects.filter(
                pipeline=pipeline,
                object_type=ref_type,
                object_id=str(ref_id),
            ).first()
            if not instance:
                return ""
            reached = (
                StageInstance.objects.filter(
                    pipeline_instance=instance,
                    status__in=[
                        StageInstance.STATUS_LOCKED,
                        StageInstance.STATUS_COMPLETE,
                        StageInstance.STATUS_AWAITING_APPROVAL,
                        StageInstance.STATUS_RUNNING,
                    ],
                )
                .select_related("stage_definition")
                .order_by("-stage_definition__order")
                .first()
            )
            if reached:
                return reached.stage_definition.code
            return ""
        except Exception as exc:
            logger.warning("PipelineService.get_current_stage failed: %s", exc)
            return ""
