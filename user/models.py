from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.db import models
from django.utils.translation import gettext_lazy as _

def get_default_team():
    """
    Returns the default team instance.
    If the "Default" team does not exist, it creates it.
    
    Returns:
        int: The ID of the default team.
    """

    team, created = Team.objects.get_or_create(name="Default")
    return team.id

class Team(models.Model):
    """
    Represents a team of users in the blogging platform.
    
    Teams are used to manage access permissions for blog posts.
    Each user belongs to exactly one team.
    """

    name = models.CharField(max_length=100)

    def __str__(self):
        """
        String representation of the Team.
        
        Returns:
            str: The team name.
        """
        return self.name

class CustomUserManager(BaseUserManager):
    """
    Custom manager for the CustomUser model.
    
    Provides methods for creating standard users and superusers.
    """

    def create_user(self, email, password=None, **extra_fields):
        """
        Creates and saves a standard user with the given email and password.
        
        Args:
            email (str): The user's email address.
            password (str, optional): The user's password.
            **extra_fields: Additional fields to set on the user.
        
        Returns:
            CustomUser: The created user instance.
        
        Raises:
            ValueError: If the email is not provided.
        """

        if not email:
            raise ValueError(_('The Email must be set'))
        email = self.normalize_email(email).lower()
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        """
        Creates and saves a superuser with the given email and password.
        
        Args:
            email (str): The superuser's email address.
            password (str, optional): The superuser's password.
            **extra_fields: Additional fields to set on the superuser.
        
        Returns:
            CustomUser: The created superuser instance.
        
        Raises:
            ValueError: If is_staff or is_superuser are not True.
        """

        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError(_('Superuser must have is_staff=True.'))
        if extra_fields.get('is_superuser') is not True:
            raise ValueError(_('Superuser must have is_superuser=True.'))

        return self.create_user(email=email, password=password, **extra_fields)

class CustomUser(AbstractBaseUser, PermissionsMixin):
    """
    Custom user model using email as the username field.
    
    Attributes:
        email (str): The unique email of the user.
        is_staff (bool): Whether the user can access the admin site.
        is_active (bool): Whether the user account is active.
        team (Team): ForeignKey to the team the user belongs to.
    """

    email = models.EmailField(_('email address'), unique=True)
    ##SE AGREGO USER NAME
    #username = models.CharField(_('username', max_length=50)) #ESTO ES NUEVO
    is_staff = models.BooleanField(_('staff status'), default=False)
    is_active = models.BooleanField(_('active'), default=True)

    # Link to the team
    team = models.ForeignKey(
        Team, 
        on_delete=models.PROTECT,
        default=get_default_team
    )
    
    objects = CustomUserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    def __str__(self):
        """
        String representation of the user.
        
        Returns:
            str: The user's email.
        """
        
        return self.email

