from django.contrib.auth.password_validation import validate_password
from rest_framework import serializers
from django.core.exceptions import ValidationError
from rest_framework.validators import UniqueValidator
from django.contrib.auth import get_user_model
from .models import CustomUser, Team

class UserSerializer(serializers.ModelSerializer):

    # Password field is write-only: never returned in API responses
    password = serializers.CharField(
        write_only=True, # Prevents password from being sent to frontend
        required=True, # Required when creating a user
        min_length=8)  # Minimum length for security

    class Meta:

        model = CustomUser # Model to serialize
        fields = ['id', 'email', 'password'] # Fields to accept / return
        read_only_fields = ['id', 'team'] # Automatically generated fields, cannot be set manually

    def validate_email(self, value):

        return value.lower()
    
    def create(self, validated_data):

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

    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)

#Agregar la documentacion
    class Meta:
        model = CustomUser
        fields = ['email', 'password']

class RegisterSerializer(serializers.ModelSerializer):
    
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

        value = value.lower()
        if CustomUser.objects.filter(email__iexact=value).exists():
            raise serializers.ValidationError("Email already registered.")
        return value

    def validate_password(self, value):
        # Validar con los validators activos en settings.py
        validate_password(value)  # ya no necesitamos pasar `user`
        return value

    def create(self, validated_data):

        email = validated_data.pop('email').lower()
        password = validated_data.pop('password')

        # Get or create default team
        default_team, _ = Team.objects.get_or_create(name="Default")

        user = CustomUser(email=email, team=default_team)
        user.set_password(password)
        user.save()
        return user