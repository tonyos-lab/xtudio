from django.contrib import admin

from apps.memory_context.models import MemoryBlock


@admin.register(MemoryBlock)
class MemoryBlockAdmin(admin.ModelAdmin):
    list_display = ["title", "tier", "block_type", "source", "priority", "is_active", "created_at"]
    list_filter = ["tier", "block_type", "source", "is_active"]
    search_fields = ["title", "content_text"]
    readonly_fields = ["id", "token_estimate", "created_at", "updated_at"]
    list_editable = ["is_active"]
