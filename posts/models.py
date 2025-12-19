from django.db import models
from django.conf import settings

class Post(models.Model):

    class PrivacyChoices(models.TextChoices):
        PUBLIC = "public", "Public"
        AUTHENTICATED = "authenticated", "Authenticated users only"
        TEAM = "team", "Team members only"
        AUTHOR = "author", "Only the author"

    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,   # Use CustomUser
        on_delete=models.CASCADE,   # Delete posts if the user is deleted
        related_name="posts"        # user.posts → all posts by this user
    )
    
    title = models.CharField(max_length=100)

    content = models.TextField()

    created_at = models.DateTimeField(auto_now_add=True)

    updated_at = models.DateTimeField(auto_now=True)

    privacy_read = models.CharField(
        max_length=20,
        choices=PrivacyChoices.choices,
        default=PrivacyChoices.PUBLIC
        )
    
    privacy_write = models.CharField(
        max_length=20,
        choices=PrivacyChoices.choices,
        default=PrivacyChoices.AUTHOR
        )

    @property
    def excerpt(self):
        return self.content[:200]

    def can_user_read(self, user):

        if getattr(user, "is_superuser", False):
            return True
        
        if self.privacy_read == self.PrivacyChoices.PUBLIC:
            return True

        if self.privacy_read == self.PrivacyChoices.AUTHENTICATED:
            return user.is_authenticated

        if self.privacy_read == self.PrivacyChoices.TEAM:
            return (
                getattr(user, "is_authenticated", False)
                and user.team == self.author.team
                and self.author.team.name != "Default"
            )

        if self.privacy_read == self.PrivacyChoices.AUTHOR:
            return getattr(user, "is_authenticated", False) and user == self.author

        return False


    def can_user_edit(self, user):

        if not getattr(user, "is_authenticated", False):
            return False

        if getattr(user, "is_superuser", False):
            return True
        
        if self.privacy_write == self.PrivacyChoices.AUTHENTICATED:
            return user.is_authenticated
        
        if self.privacy_write == self.PrivacyChoices.TEAM:

            if self.author.team.name == "Default":
                return False
            
            if not user.is_authenticated:
                return False

            return user.team == self.author.team or user.is_superuser

        if self.privacy_write == self.PrivacyChoices.AUTHOR:
            return user.is_authenticated and user == self.author

        return False
    
    def __str__(self):
        return self.title

