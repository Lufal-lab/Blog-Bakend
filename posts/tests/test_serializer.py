import pytest
from django.contrib.auth import get_user_model
from posts.models import Post
from posts.serializers import PostSerializer, PostWriteSerializer


@pytest.mark.django_db
class TestPostSerializerRead:

    def setup_method(self):
        self.User = get_user_model()
        self.user = self.User.objects.create_user(email="a@a.com", password="123")

    def test_serialize_post_to_json(self):

        post = Post.objects.create(
            author=self.user,
            title="Hello",
            content="Content"
        )

        serializer = PostSerializer(post)
        data = serializer.data

        assert data["title"] == "Hello"
        assert data["content"] == "Content"
        assert data["author"] == self.user.id
        assert data["author_email"] == self.user.email

    def test_all_fields_are_read_only(self):

        serializer = PostSerializer()

        for field in serializer.fields.values():
            assert field.read_only is True


@pytest.mark.django_db
class TestPostWriteSerializer:

    def setup_method(self):
        self.User = get_user_model()
        self.user = self.User.objects.create_user(email="b@b.com", password="123")

    def test_create_post_successfully(self):

        json_data = {
            "title": "New Post",
            "content": "Post text",
            "privacy_read": Post.PrivacyChoices.PUBLIC,
            "privacy_write": Post.PrivacyChoices.AUTHOR,
        }

        serializer = PostWriteSerializer(data=json_data)
        assert serializer.is_valid(), serializer.errors

        post = serializer.save(author=self.user)

        assert post.title == "New Post"
        assert post.author == self.user
        assert post.privacy_read == Post.PrivacyChoices.PUBLIC

    def test_validate_short_title(self):
        serializer = PostWriteSerializer(data={
            "title": "a",
            "content": "Something"
        })

        assert serializer.is_valid() is False
        assert "title" in serializer.errors

    def test_validate_empty_content(self):
        serializer = PostWriteSerializer(data={
            "title": "Title",
            "content": "    "  # empty after stripping
        })

        assert serializer.is_valid() is False
        assert "content" in serializer.errors

    def test_read_only_fields_are_not_modified(self):

        post = Post.objects.create(
            author=self.user,
            title="Old",
            content="Old content"
        )

        serializer = PostWriteSerializer(
            instance=post,
            data={
                "title": "New",
                "content": "New content",
                "author": 999999,  # attempt to override
            },
            partial=True,
        )

        assert serializer.is_valid(), serializer.errors
        updated = serializer.save()

        # author must not have changed
        assert updated.author == self.user
        assert updated.title == "New"

    def test_update_post_successfully(self):
        post = Post.objects.create(
            author=self.user,
            title="Old",
            content="Old content"
        )

        serializer = PostWriteSerializer(
            instance=post,
            data={"content": "Updated"},
            partial=True
        )

        assert serializer.is_valid(), serializer.errors
        updated_post = serializer.save()

        assert updated_post.content == "Updated"
