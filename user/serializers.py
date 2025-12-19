from django.contrib.auth.password_validation import validate_password
from rest_framework import serializers
from django.core.exceptions import ValidationError
from rest_framework.validators import UniqueValidator
from django.contrib.auth import get_user_model
from .models import CustomUser, Team

class UserSerializer(serializers.ModelSerializer):
    """
    Serializer for the CustomUser model.

    Used primarily for:
    - Creating new users
    - Returning user information in API responses
    """

    # Password field is write-only: never returned in API responses
    password = serializers.CharField(
        write_only=True, # Prevents password from being sent to frontend
        required=True, # Required when creating a user
        min_length=8)  # Minimum length for security

    class Meta:
        """
        Internal configuration for the serializer
        """
        model = CustomUser # Model to serialize
        fields = ['id', 'email', 'password'] # Fields to accept / return
        read_only_fields = ['id', 'team'] # Automatically generated fields, cannot be set manually

    def validate_email(self, value):
        """
        Ensure the email is always stored in lowercase.

        Args:
            value (str): The email to validate

        Returns:
            str: Lowercased email
        """
        return value.lower()
    
    def create(self, validated_data):
        """
        Creates a new CustomUser instance with an encrypted password.

        Args:
            validated_data (dict): Validated data from the serializer (from JSON request)

        Returns:
            CustomUser: The newly created user instance
        """

        # Extract password from the validated data to process separately
        password = validated_data.pop('password')
        # Get or create the default team
        default_team = Team.objects.filter(name="Default").first()
        if not default_team:
            default_team = Team.objects.create(name="Default")

        # Create user instance with remaining validated data    
        user = CustomUser(team=default_team, **validated_data)

        # Ensure email is lowercase
        user.email = user.email.lower()

        # Encrypt the password
        user.set_password(password)
        
        # Save user to the database
        user.save()

        return user
    
class LoginSerializer(serializers.ModelSerializer):
    """
    Serializer for user login.

    Only requires email and password fields.
    """
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)

class RegisterSerializer(serializers.ModelSerializer):
    """
    Serializer for user registration.

    Only requires email and password fields.
    """
    
    email = serializers.EmailField(
        validators=[UniqueValidator(
            queryset=CustomUser.objects.all(),
            message="Email already registered."
        )]
    )
    password = serializers.CharField(write_only=True, min_length=8)

    class Meta:
        model = CustomUser
        fields = ['id', 'email', 'password']
        read_only_fields = ['id']

    def validate_email(self, value):
        """Force email to lowercase and check uniqueness ignoring case."""
        value = value.lower()
        if CustomUser.objects.filter(email__iexact=value).exists():
            raise serializers.ValidationError("Email already registered.")
        return value

    def validate_password(self, value):
        # Validar con los validators activos en settings.py
        validate_password(value)  # ya no necesitamos pasar `user`
        return value

    def create(self, validated_data):
        """Create user with hashed password and default team."""
        email = validated_data.pop('email').lower()
        password = validated_data.pop('password')

        # Get or create default team
        default_team, _ = Team.objects.get_or_create(name="Default")

        user = CustomUser(email=email, team=default_team)
        user.set_password(password)
        user.save()
        return user