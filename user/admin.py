from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from django.contrib.auth import get_user_model
from django import forms
from .models import CustomUser, Team

class CustomUserCreationForm(UserCreationForm):

    class Meta(UserCreationForm.Meta):
        model = CustomUser
        fields = ('email', 'team', 'is_staff', 'is_active')

    def clean_email(self):
        email = self.cleaned_data.get("email").lower()
        if get_user_model().objects.filter(email__iexact=email).exists():
            raise forms.ValidationError("A user with that email already exists.")
        return email
    
    def save(self, commit=True):
        user = super().save(commit=False)
        # Force email to lowercase
        user.email = user.email.lower()
        if commit:
            user.save()
        return user

class CustomUserChangeForm(UserChangeForm):

    class Meta:
        model = CustomUser
        fields = ('email', 'team', 'is_staff', 'is_active')

    def save(self, commit=True):
        user = super().save(commit=False)
        # Force email to lowercase when editing
        user.email = user.email.lower()
        if commit:
            user.save()
        return user

# Admin
@admin.register(CustomUser)
class CustomUserAdmin(BaseUserAdmin):

    add_form = CustomUserCreationForm
    form = CustomUserChangeForm
    model = CustomUser

    # Fields to display in the user list view
    list_display = ('email', 'is_staff', 'is_active', 'team')
    list_filter = ('is_staff', 'is_active','team')

    # Field grouping in the detail view
    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        ('Permissions', {'fields': ('is_staff', 'is_active')}),  # Excluding groups and user_permissions
        ('Additional info', {'fields': ('team',)}),
    )

    # Fields shown when adding a new user
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'password1', 'password2', 'is_staff', 'is_active', 'team'),
        }),
    )

    list_editable = ['team']
    search_fields = ('email',)
    ordering = ('email',)

@admin.register(Team)
class TeamAdmin(admin.ModelAdmin):

    list_display = ['name']
    search_fields = ['name']