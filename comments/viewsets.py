from rest_framework.viewsets import ModelViewSet
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from rest_framework.authentication import SessionAuthentication, BasicAuthentication
from drf_spectacular.utils import extend_schema_view, extend_schema, OpenApiResponse, OpenApiParameter
from django.shortcuts import get_object_or_404

from .models import Comment
from .serializers import CommentSerializer
from .permissions import CanCreateComment, CanDeleteComment
from .pagination import CommentPagination
from posts.models import Post

# ============================================================
# SCHEMA / DOCUMENTATION WITH DRF SPECTACULAR
# ============================================================
@extend_schema_view(
    list=extend_schema(
        description="""
        List all comments, optionally filtered by post ID.
        
        Query parameters:
        - post: ID of the post to filter comments (optional)
        - page: page number for pagination (optional)
        - page_size: number of items per page (optional, default 20)
        
        Ordering: newest comments first.
        Permissions:
        - Anyone can list comments.
        """,
        parameters=[
            OpenApiParameter(
                name="post",
                type=int,
                location=OpenApiParameter.QUERY,
                description="Filter comments belonging to a specific post",
                required=False,
            ),
            OpenApiParameter(
                name="page",
                type=int,
                location=OpenApiParameter.QUERY,
                description="Page number for pagination (default 1)",
                required=False,
            ),
            OpenApiParameter(
                name="page_size",
                type=int,
                location=OpenApiParameter.QUERY,
                description="Number of comments per page (default 20, max 50)",
                required=False,
            ),
        ],
        responses={
            200: CommentSerializer(many=True),
        },
    ),
    retrieve=extend_schema(
        description="Retrieve a specific comment by ID.",
        responses={
            200: CommentSerializer,
            401: OpenApiResponse(description="Unauthorized"),
            403: OpenApiResponse(description="Forbidden"),
            404: OpenApiResponse(description="Comment not found"),
        },
    ),
    create=extend_schema(
        description="""
        Create a new comment.

        Notes:
        - Requires authentication.
        - The comment's user and post are automatically assigned.
        - Only users who can read the post can comment.
        """,
        request=CommentSerializer,
        responses={
            201: CommentSerializer,
            400: OpenApiResponse(description="Validation error"),
            401: OpenApiResponse(description="Unauthorized"),
            403: OpenApiResponse(description="Forbidden"),
        },
    ),
    destroy=extend_schema(
        description="""
        Delete a comment.

        Rules:
        - The comment author can delete their own comment.
        - Staff users can delete any comment.
        """,
        responses={
            204: OpenApiResponse(description="Comment deleted successfully"),
            403: OpenApiResponse(description="Forbidden"),
            404: OpenApiResponse(description="Comment not found"),
        },
    ),
)

class CommentViewSet(ModelViewSet):
    """
    ViewSet for managing comments.

    Provides endpoints for:
    - Listing comments
    - Retrieving individual comments
    - Creating comments
    - Deleting comments

    Features:
    - Pagination using CommentPagination
    - Automatic assignment of the authenticated user and related post
        when creating a comment
    - Custom permissions handled via CanCreateComment and CanDeleteComment

    Permissions:
    - Anyone can list or retrieve
    - Only users who can read the post can create comments
    - Only comment author or staff can delete
    """


    serializer_class = CommentSerializer
    pagination_class = CommentPagination

    authentication_classes = [SessionAuthentication, BasicAuthentication]
    permission_classes = [IsAuthenticatedOrReadOnly]

    def get_queryset(self):
        """
        Returns comments ordered by creation date (newest first).

        Optional filtering:
        - `post` query parameter: filter comments belonging to a specific post
        """
        queryset = Comment.objects.all().order_by("-created_at")
        post_id = self.kwargs.get("post_pk")
        if post_id:
            queryset = queryset.filter(post_id=post_id)
        return queryset

        # post_id = self.kwargs.get("post_pk")
        # return Comment.objects.filter(post_id=post_id).order_by("-created_at")

    def get_serializer_context(self):
        """
        Extend the serializer context to include the related Post object
        based on `post` provided in request data or query params.

        This allows the serializer to automatically assign the correct
        post when creating a comment.
        """

        # context = super().get_serializer_context()
        # post_id = self.kwargs.get("post_pk")
        # if post_id:
        #     context["post"] = Post.objects.get(id=post_id)
        # return context

        context = super().get_serializer_context()
        post_id = self.kwargs.get("post_pk") or self.request.data.get("post") or self.request.query_params.get("post")
        if post_id:
            context["post"] = get_object_or_404(Post, id=post_id)
        return context


    def perform_create(self, serializer):
        """
        Save a new comment.

        Note:
        - `user` and `post` are automatically handled by the serializer,
            so we do NOT pass them here.
        """
        serializer.save()  # NO pasar user, ya se maneja en el serializer

    def get_permissions(self):
        """
        Dynamically assign permissions based on the current action:

        - create: CanCreateComment (user must be authenticated and able to read the post)
        - destroy: CanDeleteComment (user must be author or staff)
        - list/retrieve: default IsAuthenticatedOrReadOnly (anyone can read)
        """
        if self.action == "create":
            permission_classes = [CanCreateComment]
        elif self.action == "destroy":
            permission_classes = [CanDeleteComment]
        else:
            permission_classes = self.permission_classes

        return [permission() for permission in permission_classes]
