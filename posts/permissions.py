from rest_framework.permissions import BasePermission

class ObjectPermissionHelpers:

    @staticmethod
    def user_is_authenticated(user):

        return getattr(user, "is_authenticated", False)
    
    @staticmethod

    def same_team(user, author):
        if not user.is_authenticated:
            return False

        if not user.team or not author.team:
            return False

        if author.team.name == "Default":
            return False

        return user.team == author.team

class CanReadPost(BasePermission):

    def has_permission(self, request, view):
        return True

    def has_object_permission(self, request, view, obj):

        if getattr(request.user, "is_superuser", False):
            return True

        if obj.privacy_read == obj.PrivacyChoices.PUBLIC:
            return True

        if obj.privacy_read == obj.PrivacyChoices.AUTHENTICATED:
            return ObjectPermissionHelpers.user_is_authenticated(request.user)

        if obj.privacy_read == obj.PrivacyChoices.TEAM:
            return ObjectPermissionHelpers.same_team(request.user, obj.author)

        if obj.privacy_read == obj.PrivacyChoices.AUTHOR:
            return request.user == obj.author

        return False

class CanEditPost(BasePermission):

    def has_permission(self, request, view):

        if view.action == "create":
            return request.user.is_authenticated
        return True

    def has_object_permission(self, request, view, obj):
        
        if getattr(request.user, "is_superuser", False):
            return True

        if not request.user.is_authenticated:
            return False

        if obj.privacy_write == obj.PrivacyChoices.AUTHENTICATED:
            return ObjectPermissionHelpers.user_is_authenticated(request.user)

        if obj.privacy_write == obj.PrivacyChoices.TEAM:
            return ObjectPermissionHelpers.same_team(request.user, obj.author)

        if obj.privacy_write == obj.PrivacyChoices.AUTHOR:
            return request.user == obj.author

        return False
