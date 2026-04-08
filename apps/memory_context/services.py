import logging

from apps.memory_context.constants import MemoryTier

logger = logging.getLogger("memory_context")


def _estimate_tokens(text: str) -> int:
    return max(1, len(text) // 4)


class MemoryContext:
    @staticmethod
    def write(
        tier: str,
        block_type: str,
        title: str,
        content: dict,
        ref_id=None,
        source: str = "system",
        priority: int = 5,
        uri: str = "",
        content_text: str = "",
    ):
        """Write a memory block. Never raises."""
        from apps.memory_context.models import MemoryBlock

        try:
            text = content_text or str(content)
            token_est = _estimate_tokens(text)
            # Platform tier always has ref_id=None
            if tier == MemoryTier.PLATFORM:
                ref_id = None
            return MemoryBlock.objects.create(
                tier=tier,
                ref_id=ref_id,
                block_type=block_type,
                title=title,
                content=content,
                content_text=content_text,
                token_estimate=token_est,
                source=source,
                priority=priority,
                uri=uri,
            )
        except Exception as exc:
            logger.warning("MemoryContext.write failed: %s", exc)
            return None

    @staticmethod
    def get(
        tier: str,
        ref_id=None,
        block_types: list | None = None,
        token_budget: int = 4000,
        priority_threshold: int = 10,
    ) -> list:
        """Retrieve memory blocks respecting token budget."""
        from apps.memory_context.models import MemoryBlock

        filters: dict = {"tier": tier, "is_active": True, "priority__lte": priority_threshold}
        if tier == MemoryTier.PLATFORM:
            filters["ref_id__isnull"] = True
        else:
            filters["ref_id"] = ref_id

        if block_types:
            filters["block_type__in"] = block_types

        blocks = MemoryBlock.objects.filter(**filters).order_by("priority", "-created_at")

        result, tokens_used = [], 0
        for block in blocks:
            if tokens_used + block.token_estimate > token_budget:
                break
            result.append(block)
            tokens_used += block.token_estimate
        return result

    @staticmethod
    def get_all_tiers(project_ref_id=None, session_ref_id=None, token_budget: int = 6000) -> dict:
        """Retrieve memory from all three tiers with budget split 20/50/30."""
        platform_budget = int(token_budget * 0.20)
        project_budget = int(token_budget * 0.50)
        session_budget = int(token_budget * 0.30)

        return {
            MemoryTier.PLATFORM: MemoryContext.get(
                MemoryTier.PLATFORM, token_budget=platform_budget
            ),
            MemoryTier.PROJECT: MemoryContext.get(
                MemoryTier.PROJECT, ref_id=project_ref_id, token_budget=project_budget
            ),
            MemoryTier.SESSION: (
                MemoryContext.get(
                    MemoryTier.SESSION, ref_id=session_ref_id, token_budget=session_budget
                )
                if session_ref_id
                else []
            ),
        }

    @staticmethod
    def promote(block, target_tier: str, new_ref_id=None):
        """Promote a block to a higher tier. Raises ValueError for invalid direction."""
        if MemoryTier.RANK.get(target_tier, 99) >= MemoryTier.RANK.get(block.tier, 0):
            raise ValueError(
                f"Cannot promote from '{block.tier}' to '{target_tier}'. "
                "Target must be a higher tier (lower rank number)."
            )
        return MemoryContext.write(
            tier=target_tier,
            block_type=block.block_type,
            title=f"[Promoted] {block.title}",
            content=block.content,
            content_text=block.content_text,
            ref_id=new_ref_id,
            source="promotion",
            priority=block.priority,
        )

    @staticmethod
    def deactivate(block) -> bool:
        """Soft-delete a memory block."""
        try:
            block.is_active = False
            block.save(update_fields=["is_active"])
            return True
        except Exception as exc:
            logger.warning("MemoryContext.deactivate failed: %s", exc)
            return False

    @staticmethod
    def clear_session(session_ref_id) -> int:
        """Deactivate all blocks for a session."""
        from apps.memory_context.models import MemoryBlock

        try:
            return MemoryBlock.objects.filter(
                tier=MemoryTier.SESSION, ref_id=session_ref_id, is_active=True
            ).update(is_active=False)
        except Exception as exc:
            logger.warning("MemoryContext.clear_session failed: %s", exc)
            return 0


class MemoryAssembler:
    @staticmethod
    def estimate_tokens(text: str) -> int:
        return _estimate_tokens(text)

    @staticmethod
    def assemble(blocks: dict, base_template: str = "", token_budget: int = 6000) -> str:
        """Assemble memory blocks into a CLAUDE.md string."""
        parts = []
        if base_template:
            parts.append(base_template)
            parts.append("\n\n---\n")

        tier_labels = {
            MemoryTier.PLATFORM: "## Platform Context (Tier 1)",
            MemoryTier.PROJECT: "## Project Memory (Tier 2)",
            MemoryTier.SESSION: "## Session Memory (Tier 3)",
        }

        tokens_used = _estimate_tokens(base_template)

        for tier in [MemoryTier.PLATFORM, MemoryTier.PROJECT, MemoryTier.SESSION]:
            tier_blocks = blocks.get(tier, [])
            if not tier_blocks:
                continue
            parts.append(tier_labels[tier])
            for block in tier_blocks:
                block_text = f"\n### {block.title}\n{block.content_text}"
                est = _estimate_tokens(block_text)
                if tokens_used + est > token_budget:
                    break
                parts.append(block_text)
                tokens_used += est

        return "\n".join(parts)
