from django.db import models
from django.conf import settings
from posts.models import Post
from django.core.exceptions import ValidationError

class Comment(models.Model):

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,  # Use the CustomUser model
        on_delete=models.CASCADE,  # Delete comments if user is deleted
        related_name="comments"    # user.comments → all comments by this user
    )

    post = models.ForeignKey(
        Post,                      # Reference to Post model
        on_delete=models.CASCADE,  # Delete comments if post is deleted
        related_name="comments"    # post.comments → all comments for this post
    )

    content = models.TextField(
        blank=False,
        null=False,
        help_text="Text content of the comment"
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
        help_text="Timestamp when the comment was created"
    )

    def clean(self):

        if not self.content or not self.content.strip():
            raise ValidationError("Comment content cannot be empty.")

    def __str__(self):

        return f"Comment #{self.id}"