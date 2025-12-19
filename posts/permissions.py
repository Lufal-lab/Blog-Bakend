# from rest_framework.permissions import BasePermission

# class ObjectPermissionHelpers:

#     @staticmethod
#     def user_is_authenticated(user):

#         return getattr(user, "is_authenticated", False)
    
#     @staticmethod

#     def same_team(user, author):
#         if not user.is_authenticated:
#             return False

#         if not user.team or not author.team:
#             return False

#         if author.team.name == "Default":
#             return False

#         return user.team == author.team

# class CanReadPost(BasePermission):

#     def has_permission(self, request, view):
#         return True

#     def has_object_permission(self, request, view, obj):

#         if getattr(request.user, "is_superuser", False):
#             return True

#         if obj.privacy_read == obj.PrivacyChoices.PUBLIC:
#             return True

#         if obj.privacy_read == obj.PrivacyChoices.AUTHENTICATED:
#             return ObjectPermissionHelpers.user_is_authenticated(request.user)

#         if obj.privacy_read == obj.PrivacyChoices.TEAM:
#             return ObjectPermissionHelpers.same_team(request.user, obj.author)

#         if obj.privacy_read == obj.PrivacyChoices.AUTHOR:
#             return request.user == obj.author

#         return False

# class CanEditPost(BasePermission):

#     def has_permission(self, request, view):

#         if view.action == "create":
#             return request.user.is_authenticated
#         return True

#     def has_object_permission(self, request, view, obj):
        
#         if getattr(request.user, "is_superuser", False):
#             return True

#         if not request.user.is_authenticated:
#             return False

#         if obj.privacy_write == obj.PrivacyChoices.AUTHENTICATED:
#             return ObjectPermissionHelpers.user_is_authenticated(request.user)

#         if obj.privacy_write == obj.PrivacyChoices.TEAM:
#             return ObjectPermissionHelpers.same_team(request.user, obj.author)

#         if obj.privacy_write == obj.PrivacyChoices.AUTHOR:
#             return request.user == obj.author

#         return False

from rest_framework.permissions import BasePermission

class ObjectPermissionHelpers:

    @staticmethod
    def user_is_authenticated(user):
        return getattr(user, "is_authenticated", False)
    
    @staticmethod
    def same_team(user, author):
        if not getattr(user, "is_authenticated", False):
            return False

        if not getattr(user, "team", None) or not getattr(author, "team", None):
            return False

        if author.team.name == "Default":
            return False

        return user.team == author.team


class CanReadPost(BasePermission):

    def has_permission(self, request, view):
        # Cualquier usuario puede listar posts; el filtrado real está en has_object_permission
        return True

    def has_object_permission(self, request, view, obj):
        if getattr(request.user, "is_superuser", False):
            return True

        permission_map = {
            obj.PrivacyChoices.PUBLIC: lambda u: True,
            obj.PrivacyChoices.AUTHENTICATED: ObjectPermissionHelpers.user_is_authenticated,
            obj.PrivacyChoices.TEAM: lambda u: ObjectPermissionHelpers.same_team(u, obj.author),
            obj.PrivacyChoices.AUTHOR: lambda u: u == obj.author
        }

        return permission_map.get(obj.privacy_read, lambda u: False)(request.user)


class CanEditPost(BasePermission):

    def has_permission(self, request, view):
        if view.action == "create":
            return getattr(request.user, "is_authenticated", False)
        return True

    def has_object_permission(self, request, view, obj):
        user = request.user

        if getattr(user, "is_superuser", False):
            return True

        if not getattr(user, "is_authenticated", False):
            return False

        permission_map = {
            obj.PrivacyChoices.AUTHENTICATED: ObjectPermissionHelpers.user_is_authenticated,
            obj.PrivacyChoices.TEAM: lambda u: ObjectPermissionHelpers.same_team(u, obj.author),
            obj.PrivacyChoices.AUTHOR: lambda u: u == obj.author
        }

        return permission_map.get(obj.privacy_write, lambda u: False)(user)
