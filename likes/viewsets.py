# from rest_framework import viewsets, status
# from rest_framework.permissions import IsAuthenticated, IsAuthenticatedOrReadOnly
# from rest_framework.response import Response
# from rest_framework.exceptions import ValidationError
# from .pagination import LikePagination
# from rest_framework.decorators import action
# from django.shortcuts import get_object_or_404

# from .models import Like
# from .serializers import LikeSerializer
# from .permissions import CanLike, CanUnlike

# from posts.models import Post


# class LikeViewSet(viewsets.ModelViewSet):
#     """
#     ViewSet for managing Likes.

#     Endpoints provided:
#     - list: List likes, optionally filtered by post
#     - create: Create a new like (authenticated users only)
#     - destroy: Delete a like (only the creator or superuser)
#     """

#     queryset = Like.objects.all().order_by("-created_at")
#     serializer_class = LikeSerializer

#     pagination_class = LikePagination

#     # ============================================================
#     # PERMISSIONS
#     # ============================================================
#     def get_permissions(self):
#         if self.action == 'destroy':
#             return [CanUnlike()]
#         elif self.action == 'create':
#             return [IsAuthenticated()]
#         return []

#     # ============================================================
#     # CREATE LIKE: prevent duplicates
#     # ============================================================
#     def perform_create(self, serializer):
#         user = self.request.user
#         # post = serializer.validated_data["post"]
#         post_id = self.kwargs.get("post_pk")
#         post = get_object_or_404(Post, id=post_id)

#         # Check if user already liked this post
#         if not post.can_user_read(self.request.user):
#             raise ValidationError("You cannot like this post.")
        
#         if Like.objects.filter(user=self.request.user, post=post).exists():
#             raise ValidationError("You have already liked this post.")

#         serializer.save(user=user, post=post)

#     # ============================================================
#     # OPTIONAL: Filter likes by post
#     # ============================================================
#     def get_queryset(self):
#         queryset = Like.objects.all().order_by("-created_at")
#         post_id = self.kwargs.get("post_pk")  # viene del nested router
#         # post_id = self.request.query_params.get("post", None)
#         if post_id is not None:
#             queryset = queryset.filter(post_id=post_id)
#         return queryset
    
#     @action(detail=False, methods=['delete'], url_path='unlike')
#     def unlike(self, request, post_pk=None):
#         try:
#             like = Like.objects.get(user=request.user, post_id=post_pk)
#         except Like.DoesNotExist:
#             return Response(
#                 {"detail": "You have not liked this post."},
#                 status=status.HTTP_404_NOT_FOUND
#             )

#         like.delete()
#         return Response(status=status.HTTP_204_NO_CONTENT)

from rest_framework import viewsets, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.exceptions import ValidationError
from rest_framework.decorators import action
from django.shortcuts import get_object_or_404

from drf_spectacular.utils import (
    extend_schema_view,
    extend_schema,
    OpenApiResponse,
)

from .models import Like
from .serializers import LikeSerializer
from .permissions import CanLike, CanUnlike
from .pagination import LikePagination

from posts.models import Post


@extend_schema_view(
    list=extend_schema(
        summary="List likes",
        description="Return a paginated list of likes. Can be filtered by post.",
        responses={200: LikeSerializer(many=True)},
    ),
    create=extend_schema(
        summary="Like a post",
        description=(
            "Create a like for a blog post. "
            "User must be authenticated and have read access to the post. "
            "Duplicate likes are not allowed."
        ),
        request=LikeSerializer,
        responses={
            201: LikeSerializer,
            400: OpenApiResponse(description="Already liked or invalid request"),
            401: OpenApiResponse(description="Authentication required"),
        },
    ),
    destroy=extend_schema(
        summary="Delete a like",
        description="Delete a like. Only the user who created the like can delete it.",
        responses={
            204: OpenApiResponse(description="Like deleted"),
            403: OpenApiResponse(description="Permission denied"),
        },
    ),
)
class LikeViewSet(viewsets.ModelViewSet):
    """
    API endpoints for managing likes on blog posts.

    - Authenticated users can like a post
    - Users cannot like the same post more than once
    - Only the creator of a like can remove it
    """

    queryset = Like.objects.all().order_by("-created_at")
    serializer_class = LikeSerializer
    pagination_class = LikePagination

    def get_permissions(self):
        if self.action == "destroy":
            permission_classes = [CanUnlike]
        elif self.action == "create":
            permission_classes = [IsAuthenticated]
        else:
            permission_classes = []

        return [permission() for permission in permission_classes]

    def get_queryset(self):
        """
        Optionally filter likes by post using nested routes.
        """
        queryset = Like.objects.all().order_by("-created_at")
        post_id = self.kwargs.get("post_pk")
        if post_id:
            queryset = queryset.filter(post_id=post_id)
        return queryset

    def perform_create(self, serializer):
        """
        Create a like for a post.
        Prevent duplicate likes and enforce read permissions.
        """
        user = self.request.user
        post_id = self.kwargs.get("post_pk")
        post = get_object_or_404(Post, id=post_id)

        if not post.can_user_read(user):
            raise ValidationError("You cannot like this post.")

        if Like.objects.filter(user=user, post=post).exists():
            raise ValidationError("You have already liked this post.")

        serializer.save(user=user, post=post)

    @extend_schema(
        summary="Unlike a post",
        description="Remove a like from a post that the user previously liked.",
        responses={
            204: OpenApiResponse(description="Like removed"),
            404: OpenApiResponse(description="Like not found"),
        },
    )
    @action(detail=False, methods=["delete"], url_path="unlike")
    def unlike(self, request, post_pk=None):
        """
        Remove a previously created like for the given post.
        """
        try:
            like = Like.objects.get(user=request.user, post_id=post_pk)
        except Like.DoesNotExist:
            return Response(
                {"detail": "You have not liked this post."},
                status=status.HTTP_404_NOT_FOUND,
            )

        like.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
