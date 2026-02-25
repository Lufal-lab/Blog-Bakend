from rest_framework import serializers
from .models import Post

PRIVACY_CHOICES = ["public", "authenticated", "team", "author"]


class PostSerializer(serializers.ModelSerializer):
    author_email = serializers.EmailField(
        source="author.email",
        read_only=True
    )
    author_team = serializers.CharField(
        source="author.team.name",
        read_only=True
    )
    excerpt = serializers.SerializerMethodField()
    likes_count = serializers.SerializerMethodField()
    comments_count = serializers.SerializerMethodField()
    is_liked = serializers.SerializerMethodField()

    class Meta:
        model = Post
        fields = [
            "id",
            "author",
            "author_email",
            "author_team",
            "title",
            "content",
            "excerpt",
            "likes_count",
            "comments_count",
            "is_liked",
            "created_at",
            "updated_at",
            "privacy_read",
            "privacy_write",
        ]
        read_only_fields = fields

    def get_excerpt(self, obj):
        return obj.content[:200]

    def get_likes_count(self, obj):
        return obj.likes.count()
    
    def get_is_liked(self, obj):
        request = self.context.get("request")
        
        if request and request.user.is_authenticated:
            return obj.likes.filter(user=request.user).exists()
        
        return False

    def get_comments_count(self, obj):
        return obj.comments.count()

class PostWriteSerializer(serializers.ModelSerializer):
    privacy_read = serializers.ChoiceField(choices=PRIVACY_CHOICES)
    privacy_write = serializers.ChoiceField(choices=PRIVACY_CHOICES)

    class Meta:
        model = Post
        fields = [
            "title",
            "content",
            "privacy_read",
            "privacy_write",
        ]

    def validate(self, data):
        if data.get("privacy_write") == "public":
            raise serializers.ValidationError({
                "privacy_write": "Write permission cannot be 'public'."
            })
        return data

    def validate_title(self, value):
        if len(value.strip()) < 3:
            raise serializers.ValidationError("Title must have at least 3 characters.")
        return value

    def validate_content(self, value):
        if not value.strip():
            raise serializers.ValidationError("Content cannot be empty.")
        return value

class PostValidationErrorSerializer(serializers.Serializer):

    title = serializers.ListField(
        child=serializers.CharField(),
        required=False
    )
    content = serializers.ListField(
        child=serializers.CharField(),
        required=False
    )
    privacy_read = serializers.ListField(
        child=serializers.CharField(),
        required=False
    )
    privacy_write = serializers.ListField(
        child=serializers.CharField(),
        required=False
    )