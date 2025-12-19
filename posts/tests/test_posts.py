import pytest
from django.contrib.auth import get_user_model
from posts.models import Post

# ============================================================
# ALL TESTS REQUIRE DATABASE
# ============================================================
@pytest.mark.django_db
class TestPostsModel:
    """
    Tests for the Post model:
    - Basic creation
    - Default values
    - Related fields
    - Cascade delete behavior
    """

    # ========================================================
    # setup_method → runs BEFORE each test
    # Store reference to the User model
    # ========================================================
    def setup_method(self):
        self.User = get_user_model()

    # ========================================================
    # 1. Basic Post creation
    # ========================================================
    def test_create_post(self):
        """
        Verifies that:
        - A Post can be created
        - The author is correctly assigned
        - All fields are stored
        """
        user = self.User.objects.create_user(
            email="author@example.com",
            password="123456"
        )

        post = Post.objects.create(
            author=user,
            title="My first post",
            content="Post content"
        )

        assert post.author == user
        assert post.title == "My first post"
        assert post.content == "Post content"

    # ========================================================
    # 2. Automatic date assignment
    # ========================================================
    def test_auto_dates(self):
        user = self.User.objects.create_user(
            email="dates@example.com",
            password="123"
        )

        post = Post.objects.create(
            author=user,
            title="With dates",
            content="Testing dates"
        )

        assert post.created_at is not None
        assert post.updated_at is not None

    # ========================================================
    # 3. Default privacy values
    # ========================================================
    def test_default_privacy(self):
        user = self.User.objects.create_user(
            email="priv@example.com",
            password="123"
        )

        post = Post.objects.create(
            author=user,
            title="Private?",
            content="..."
        )

        assert post.privacy_read == "public"
        assert post.privacy_write == "author"

    # ========================================================
    # 4. Manually changing privacy
    # ========================================================
    def test_change_privacy(self):
        user = self.User.objects.create_user(
            email="priv2@example.com",
            password="123"
        )

        post = Post.objects.create(
            author=user,
            title="Changes",
            content="Editing privacy",
            privacy_read="team",
            privacy_write="authenticated"
        )

        assert post.privacy_read == "team"
        assert post.privacy_write == "authenticated"

    # ========================================================
    # 5. __str__ returns the title
    # ========================================================
    def test_str(self):
        user = self.User.objects.create_user(
            email="str@example.com",
            password="123"
        )

        post = Post.objects.create(
            author=user,
            title="Beautiful Title",
            content="..."
        )

        assert str(post) == "Beautiful Title"

    # ========================================================
    # 6. A user can have multiple posts
    # ========================================================
    def test_user_multiple_posts(self):
        user = self.User.objects.create_user(
            email="multi@example.com",
            password="123"
        )

        p1 = Post.objects.create(author=user, title="P1", content="...")
        p2 = Post.objects.create(author=user, title="P2", content="...")
        p3 = Post.objects.create(author=user, title="P3", content="...")

        # user.posts → related_name
        assert user.posts.count() == 3
        assert p1 in user.posts.all()
        assert p2 in user.posts.all()
        assert p3 in user.posts.all()

    # ========================================================
    # 7. Deleting a user cascades to posts
    # ========================================================
    def test_delete_user_cascades_posts(self):
        user = self.User.objects.create_user(
            email="delete@example.com",
            password="123"
        )

        Post.objects.create(author=user, title="X", content="...")
        Post.objects.create(author=user, title="Y", content="...")

        user.delete()

        # All posts should be removed
        assert Post.objects.count() == 0

    # ========================================================
    # 8. updated_at changes when saving
    # ========================================================
    def test_updated_at_changes(self):
        user = self.User.objects.create_user(
            email="update@example.com",
            password="123"
        )

        post = Post.objects.create(
            author=user,
            title="Update me",
            content="x"
        )

        old_updated = post.updated_at

        post.content = "new content"
        post.save()

        assert post.updated_at > old_updated
