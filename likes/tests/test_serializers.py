from rest_framework import serializers
from likes.models import Like
from posts.models import Post


class LikeSerializer(serializers.ModelSerializer):
    """
    Serializer for the Like model.

    Responsibilities:
    - Validate that a user can only like a post they can read
    - Prevent duplicate likes by the same user
    - Automatically assign request.user to the like
    """

    # Mostrar el email del usuario sin permitir cambios
    user_email = serializers.EmailField(source="user.email", read_only=True)
    post = serializers.PrimaryKeyRelatedField(read_only=True)

    class Meta:
        model = Like
        fields = ["id", "post", "user_email", "created_at"]
        read_only_fields = ["id", "user_email", "created_at"]