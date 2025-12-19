from django.contrib import admin
from .models import Comment

@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):

    list_display = [
        "id",
        "post",
        "user",
        "user_team",
        "content",
        "created_at",
    ]

    list_display_links = ["content"]

    search_fields = [
        "content",
        "user__email",
        "post__title",
        "user__team__name",
    ]

    list_filter = [
        "post",
        "user",
        "user__team",
        ("created_at", admin.DateFieldListFilter),
    ]

    readonly_fields = ["created_at"]

    ordering = ["-created_at"]

    def user_team(self, obj):
        return obj.user.team.name if obj.user.team else None
    user_team.short_description = "Team"

    def save_model(self, request, obj, form, change):
        
        if not obj.user_id:
            obj.user = request.user
        super().save_model(request, obj, form, change)
