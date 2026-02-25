from django.db import models
from django.conf import settings

class Post(models.Model):

    class PrivacyChoices(models.TextChoices):
        PUBLIC = "public", "Public"
        AUTHENTICATED = "authenticated", "Authenticated users only"
        TEAM = "team", "Team members only"
        AUTHOR = "author", "Only the author"

    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="posts"
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

        mapping = {
            self.PrivacyChoices.PUBLIC: lambda u: True,
            self.PrivacyChoices.AUTHENTICATED: lambda u: u.is_authenticated,
            self.PrivacyChoices.TEAM: lambda u: (
                getattr(u, "is_authenticated", False)
                and u.team == self.author.team
                and self.author.team.name != "Default"
            ),
            self.PrivacyChoices.AUTHOR: lambda u: getattr(u, "is_authenticated", False) and u == self.author
        }

        return mapping.get(self.privacy_read, lambda u: False)(user)

    def can_user_edit(self, user):
        if not getattr(user, "is_authenticated", False):
            return False

        if getattr(user, "is_superuser", False):
            return True
        
        mapping = {
            self.PrivacyChoices.AUTHENTICATED: lambda u: u.is_authenticated,
            self.PrivacyChoices.TEAM: lambda u: (
                self.author.team.name != "Default" and u.team == self.author.team
            ),
            self.PrivacyChoices.AUTHOR: lambda u: u == self.author
        }

        return mapping.get(self.privacy_write, lambda u: False)(user)

    def __str__(self):
        return self.title
