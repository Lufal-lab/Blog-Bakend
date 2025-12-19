from django.contrib import admin
from .models import Like
from posts.models import Post
from django.contrib.auth import get_user_model

User = get_user_model()

@admin.register(Like)
class LikeAdmin(admin.ModelAdmin):

    list_display = ("id", "user", "post", "created_at")
    list_filter = ("post", "user", "post__author__team")
    search_fields = ("user__email", "post__title")
    readonly_fields = ("created_at",)

    autocomplete_fields = ("user", "post")

    def save_model(self, request, obj, form, change):

        if not obj.user_id:
            obj.user = request.user  # fallback to admin
        super().save_model(request, obj, form, change)

    def get_queryset(self, request):

        qs = super().get_queryset(request)
        return qs.select_related("user", "post", "post__author", "post__author__team")
