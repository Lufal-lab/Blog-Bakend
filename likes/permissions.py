from rest_framework.permissions import BasePermission

class CanLike(BasePermission):

    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated


class CanUnlike(BasePermission):

    def has_object_permission(self, request, view, obj):
        # obj is expected to be a Like instance
        return request.user and (request.user.is_superuser or obj.user == request.user)