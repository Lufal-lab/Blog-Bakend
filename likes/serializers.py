from rest_framework import serializers
from likes.models import Like
from posts.models import Post


class LikeSerializer(serializers.ModelSerializer):

    # Mostrar el email del usuario sin permitir cambios
    user_email = serializers.EmailField(source="user.email", read_only=True)
    post = serializers.PrimaryKeyRelatedField(read_only=True)

    class Meta:
        model = Like
        fields = ["id", "post", "user_email", "created_at"]
        read_only_fields = ["id", "user_email", "created_at"]
