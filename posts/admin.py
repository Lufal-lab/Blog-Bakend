from django.contrib import admin
from django.core.exceptions import ValidationError
from .models import Post

@admin.register(Post)
class PostAdmin(admin.ModelAdmin):

    list_display = [
        'id',
        'title',           # Post title
        'author',          # Post author (FK to CustomUser)
        'author_team',
        'privacy_read',    # Read permission level
        'privacy_write',   # Write/edit permission level
        'num_comments',   # ← agregado
        'num_likes', 
        'created_at',      # Timestamp when post was created
        'updated_at'       # Timestamp when post was last updated
    ]

    list_display_links = ['title']

    search_fields = [
        'id',
        'title',           # Search posts by title
        'author__email',    # Search posts by author's email
        'author__team__name'
    ]

    list_filter = [
        'privacy_read',    # Filter by read permissions: Public, Authenticated, Team, Author
        'privacy_write',   # Filter by write/edit permissions
        'author',          # Filter by author
        'author__team',
        ('created_at', admin.DateFieldListFilter),  # Filter by creation date
        ('updated_at', admin.DateFieldListFilter),  # Filter by last update
    ]

    readonly_fields = ['created_at', 'updated_at']

    ordering = ['-created_at']  # Newest posts appear first

    def author_team(self, obj):
        return obj.author.team.name
    author_team.short_description = "Team"

    def num_comments(self, obj):
        return obj.comments.count()   # usa related_name='comments'
    num_comments.short_description = "Comments"

    def num_likes(self, obj):
        return obj.likes.count()      # usa related_name='likes'
    num_likes.short_description = "Likes"

    def save_model(self, request, obj, form, change):
        if obj.privacy_write == Post.PrivacyChoices.PUBLIC:
            raise ValidationError({
                "privacy_write": "Write permission cannot be 'public'."
            })

        if not obj.author_id:
            obj.author = request.user
        super().save_model(request, obj, form, change)