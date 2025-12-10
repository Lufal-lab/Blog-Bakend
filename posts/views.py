# from rest_framework import generics, status
# from rest_framework.response import Response
# from rest_framework.exceptions import PermissionDenied
# from django.contrib.auth.models import AnonymousUser

# from .models import Post
# from .serializers import PostSerializer
# from .permissions import CanReadPost, CanEditPost

# class PostListCreateView(generics.ListCreateAPIView):
#     """
#     GET  -> lista posts que el usuario puede LEER
#     POST -> crea un nuevo post (autor = request.user)
#     """

#     serializer_class = PostSerializer

#     def get_queryset(self):
#         """
#         Devolver solo los posts que el request.user puede leer.
#         Esto evita que la lista muestre posts a los que no tiene acceso.
#         """
#         user = self.request.user if hasattr(self.request, "user") else AnonymousUser()
#         qs = Post.objects.all()

#         # Filtro manual: solo los posts donde can_user_read(user) es True
#         # IMPORTANTE: esto puede ser ineficiente si hay muchos posts; en apps reales
#         # se recomienda traducir las reglas a consultas SQL (filter) cuando sea posible.
#         allowed = []
#         for p in qs:
#             # usamos el método del modelo si lo tienes (post.can_user_read(user))
#             # Si no lo tienes, podrías reimplementar la lógica aquí.
#             if p.can_user_read(user):
#                 allowed.append(p.pk)

#         return Post.objects.filter(pk__in=allowed).order_by("-created_at")

#     def perform_create(self, serializer):
#         """
#         Asignar el autor automáticamente (no confiar en que venga en el request).
#         Si el usuario no está autenticado, le lanzamos error.
#         """
#         user = self.request.user
#         if not getattr(user, "is_authenticated", False):
#             # No permitimos crear posts si no hay usuario autenticado
#             raise PermissionDenied("Debes iniciar sesión para crear un post.")

#         # guardamos pasando author explícitamente
#         serializer.save(author=user)


# class PostDetailView(generics.RetrieveUpdateDestroyAPIView):
#     """
#     GET    -> ver un post (si tiene permiso de lectura)
#     PUT    -> actualizar (si tiene permiso de edición)
#     PATCH  -> parcial (idem)
#     DELETE -> eliminar (si tiene permiso de edición)
#     """

#     queryset = Post.objects.all()
#     serializer_class = PostSerializer

#     def get_object(self):
#         """
#         Recupera el objeto y verifica permiso de lectura cuando es GET,
#         o permiso de edición cuando el método es PUT/PATCH/DELETE.
#         """
#         obj = super().get_object()

#         # Si es GET → comprobar permiso de lectura
#         if self.request.method == "GET":
#             perm = CanReadPost()
#             if not perm.has_object_permission(self.request, self, obj):
#                 # si no tiene permiso → 404 o 403. Preferimos 404 para no revelar existencia.
#                 raise PermissionDenied("No tienes permiso para ver este post.")

#         # Si es PUT/PATCH/DELETE -> comprobar permiso de edición
#         if self.request.method in ("PUT", "PATCH", "DELETE"):
#             perm = CanEditPost()
#             if not perm.has_object_permission(self.request, self, obj):
#                 raise PermissionDenied("No tienes permiso para editar/eliminar este post.")

#         return obj
