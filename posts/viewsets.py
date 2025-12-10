from rest_framework import viewsets
from rest_framework.exceptions import PermissionDenied
from django.contrib.auth.models import AnonymousUser

from .models import Post
from .serializers import PostSerializer
from .permissions import CanReadPost, CanEditPost


class PostViewSet(viewsets.ModelViewSet):
    """
    Este ViewSet maneja:
    - GET /posts/
    - POST /posts/
    - GET /posts/{id}/
    - PUT /posts/{id}/
    - DELETE /posts/{id}/
    """

    serializer_class = PostSerializer
    queryset = Post.objects.all()

    def get_queryset(self):
        """Devuelve solo los posts que el usuario puede leer"""
        user = self.request.user if hasattr(self.request, "user") else AnonymousUser()

        allowed_ids = [
            post.id for post in Post.objects.all()
            if post.can_user_read(user)
        ]

        return Post.objects.filter(id__in=allowed_ids)

    def perform_create(self, serializer):
        """Asigna el autor automáticamente"""
        user = self.request.user
        if not user.is_authenticated:
            raise PermissionDenied("Debes iniciar sesión para crear un post.")

        serializer.save(author=user)

    def get_object(self):
        """Controla permisos de lectura / edición"""
        obj = super().get_object()

        if self.request.method == "GET":
            if not CanReadPost().has_object_permission(self.request, self, obj):
                raise PermissionDenied("No puedes ver este post.")

        if self.request.method in ["PUT", "PATCH", "DELETE"]:
            if not CanEditPost().has_object_permission(self.request, self, obj):
                raise PermissionDenied("No puedes editar este post.")

        return obj
