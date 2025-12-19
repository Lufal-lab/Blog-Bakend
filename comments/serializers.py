from rest_framework import serializers
from .models import Comment

class CommentSerializer(serializers.ModelSerializer):

    user_email = serializers.EmailField(source="user.email", read_only=True)

    class Meta:
        model = Comment
        fields = ["id", "content", "created_at", "user_email"]
        read_only_fields = ["id", "created_at", "user_email"]

    def validate(self, attrs):

        request = self.context.get("request")
        post = self.context.get("post")

        if request is None or post is None:
            raise serializers.ValidationError(
                "Request and post must be provided in serializer context."
            )

        if not post.can_user_read(request.user):
            raise serializers.ValidationError(
                "You do not have permission to comment on this post."
            )

        return attrs

    def create(self, validated_data):

        request = self.context.get("request")
        post = self.context.get("post")

        return Comment.objects.create(
            user=request.user,
            post=post,
            content=validated_data["content"]
        )
