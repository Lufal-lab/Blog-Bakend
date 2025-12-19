from rest_framework import viewsets, status
from rest_framework.permissions import IsAuthenticated, IsAuthenticatedOrReadOnly
from rest_framework.response import Response
from rest_framework.exceptions import ValidationError
from .pagination import LikePagination
from rest_framework.decorators import action
from django.shortcuts import get_object_or_404
from drf_spectacular.utils import extend_schema, extend_schema_view, OpenApiResponse

from .models import Like
from .serializers import LikeSerializer
from .permissions import CanLike, CanUnlike

from posts.models import Post

@extend_schema_view(
    list=extend_schema(
        description="List likes. Can be filtered by post using the post_pk from the nested route.",
        responses={200: LikeSerializer(many=True)},
    ),
    create=extend_schema(
        description="Create a like for a post. Users can only like a post once.",
        responses={
            201: LikeSerializer,
            400: OpenApiResponse(description="You have already liked this post."),
            403: OpenApiResponse(description="You cannot like this post."),
        },
    ),
    destroy=extend_schema(
        description="Delete a like. Only the owner or a superuser can delete it.",
        responses={
            204: OpenApiResponse(description="Like deleted successfully."),
            403: OpenApiResponse(description="You do not have permission to delete this like."),
        },
    ),
    unlike=extend_schema(
        description="Remove the like from the authenticated user for the given post.",
        responses={
            204: OpenApiResponse(description="Like removed successfully."),
            404: OpenApiResponse(description="You have not liked this post."),
        },
    ),
)
class LikeViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing Likes.

    Endpoints provided:
    - list: List likes, optionally filtered by post
    - create: Create a new like (authenticated users only)
    - destroy: Delete a like (only the creator or superuser)
    """

    queryset = Like.objects.all().order_by("-created_at")
    serializer_class = LikeSerializer

    pagination_class = LikePagination

    # ============================================================
    # PERMISSIONS
    # ============================================================
    def get_permissions(self):
        if self.action == 'destroy':
            return [CanUnlike()]
        elif self.action == 'create':
            return [IsAuthenticated()]
        return []

    # ============================================================
    # CREATE LIKE: prevent duplicates
    # ============================================================
    def perform_create(self, serializer):
        user = self.request.user
        # post = serializer.validated_data["post"]
        post_id = self.kwargs.get("post_pk")
        post = get_object_or_404(Post, id=post_id)

        # Check if user already liked this post
        if not post.can_user_read(self.request.user):
            raise ValidationError("You cannot like this post.")
        
        if Like.objects.filter(user=self.request.user, post=post).exists():
            raise ValidationError("You have already liked this post.")

        serializer.save(user=user, post=post)

    # ============================================================
    # OPTIONAL: Filter likes by post
    # ============================================================
    def get_queryset(self):
        queryset = Like.objects.all().order_by("-created_at")
        post_id = self.kwargs.get("post_pk")  # viene del nested router
        # post_id = self.request.query_params.get("post", None)
        if post_id is not None:
            queryset = queryset.filter(post_id=post_id)
        return queryset
    
    @action(detail=False, methods=['delete'], url_path='unlike')
    def unlike(self, request, post_pk=None):
        try:
            like = Like.objects.get(user=request.user, post_id=post_pk)
        except Like.DoesNotExist:
            return Response(
                {"detail": "You have not liked this post."},
                status=status.HTTP_404_NOT_FOUND
            )

        like.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
