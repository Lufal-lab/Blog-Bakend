from rest_framework.permissions import BasePermission
from posts.models import Post

class CanCreateComment(BasePermission):

    def has_permission(self, request, view):

        return request.user and request.user.is_authenticated

class CanDeleteComment(BasePermission):

    def has_object_permission(self, request, view, obj):

        # Comment author can delete their own comment
        if obj.user == request.user:
            return True
        
        # Staff (admin) users can delete any comment
        if request.user.is_staff:
            return True
        
        # Otherwise, deletion is not allowed
        return False
