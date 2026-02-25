from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from django.db.models import Q

from drf_spectacular.utils import (
    extend_schema_view,
    extend_schema,
    OpenApiResponse,
    OpenApiParameter,
)

from .pagination import PostPagination
from .models import Post
from .serializers import (
    PostSerializer,
    PostWriteSerializer,
    PostValidationErrorSerializer,
)
from .permissions import CanReadPost, CanEditPost


@extend_schema_view(
    list=extend_schema(
        summary="List accessible blog posts",
        description=(
            "Returns a paginated list of blog posts that the current user has "
            "read access to based on post permissions."
        ),
        parameters=[
            OpenApiParameter(name="id", type=int, description="Filter by post ID"),
            OpenApiParameter(name="author", type=int, description="Filter by author ID"),
            OpenApiParameter(name="team", type=str, description="Filter by author team"),
            OpenApiParameter(
                name="privacy_read",
                type=str,
                description="Filter by read permission level",
            ),
            OpenApiParameter(
                name="privacy_write",
                type=str,
                description="Filter by write permission level",
            ),
        ],
        responses={200: PostSerializer(many=True)},
    ),
    retrieve=extend_schema(
        summary="Retrieve a blog post",
        description="Retrieve a single blog post if the user has read access.",
        responses={
            200: PostSerializer,
            404: OpenApiResponse(description="Post not found"),
        },
    ),
    create=extend_schema(
        summary="Create a blog post",
        description=(
            "Create a new blog post. The authenticated user is automatically "
            "set as the author. Read and write permissions can be configured."
        ),
        request=PostWriteSerializer,
        responses={
            201: PostSerializer,
            400: PostValidationErrorSerializer,
            401: OpenApiResponse(description="Authentication required"),
        },
    ),
    update=extend_schema(
        summary="Update a blog post",
        description="Update an existing blog post. User must have edit permission.",
        request=PostWriteSerializer,
        responses={
            200: PostSerializer,
            403: OpenApiResponse(description="Permission denied"),
        },
    ),
    partial_update=extend_schema(
        summary="Partially update a blog post",
        description="Partially update a blog post. User must have edit permission.",
        request=PostWriteSerializer,
        responses={
            200: PostSerializer,
            403: OpenApiResponse(description="Permission denied"),
        },
    ),
    destroy=extend_schema(
        summary="Delete a blog post",
        description="Delete a blog post. User must have edit permission.",
        responses={
            204: OpenApiResponse(description="Post deleted"),
            403: OpenApiResponse(description="Permission denied"),
        },
    ),
)

class PostViewSet(viewsets.ModelViewSet):
    """
    API endpoints for managing blog posts with fine-grained read and write permissions.
    """

    queryset = Post.objects.all()
    pagination_class = PostPagination

    # ----------------------------
    # Permisos
    # ----------------------------
    action_permissions = {
        "list": [CanReadPost()],
        "retrieve": [CanReadPost()],
        "create": [IsAuthenticatedOrReadOnly()],
        "update": [IsAuthenticatedOrReadOnly(), CanEditPost()],
        "partial_update": [IsAuthenticatedOrReadOnly(), CanEditPost()],
        "destroy": [IsAuthenticatedOrReadOnly(), CanEditPost()],
    }

    def get_permissions(self):
        return self.action_permissions.get(self.action, super().get_permissions())

    # ----------------------------
    # Serializers
    # ----------------------------
    action_serializers = {
        "create": PostWriteSerializer,
        "update": PostWriteSerializer,
        "partial_update": PostWriteSerializer,
    }

    def get_serializer_class(self):
        return self.action_serializers.get(self.action, PostSerializer)

    # ----------------------------
    # Queryset
    # ----------------------------
    def get_queryset(self):
        user = self.request.user
        queryset = Post.objects.all()

        if self.action == "list":
            if user.is_staff:
                queryset = Post.objects.all()
            elif not user.is_authenticated:
                queryset = queryset.filter(privacy_read=Post.PrivacyChoices.PUBLIC)
            else:
                queryset = Post.objects.filter(
                    Q(privacy_read=Post.PrivacyChoices.PUBLIC)
                    | Q(privacy_read=Post.PrivacyChoices.AUTHENTICATED)
                    | Q(privacy_read=Post.PrivacyChoices.AUTHOR, author=user)
                    | Q(privacy_read=Post.PrivacyChoices.TEAM, author__team=user.team)
                ).distinct()

        # ----------------------------
        # Filtros por query params
        # ----------------------------
        param_map = {
            "id": "id",
            "author": "author_id",
            "team": "author__team__name",
            "privacy_read": "privacy_read",
            "privacy_write": "privacy_write",
            "created_from": "created_at__date__gte",
            "created_to": "created_at__date__lte",
        }

        for param, field in param_map.items():
            if param in self.request.query_params:
                queryset = queryset.filter(**{field: self.request.query_params[param]})

        return queryset.order_by("-created_at")

    # ----------------------------
    # Crear post
    # ----------------------------
    def create(self, request, *args, **kwargs):
        serializer = PostWriteSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        post = serializer.save(author=request.user)

        # response_serializer = PostSerializer(post)
        response_serializer = PostSerializer(
            post,
            context={'request': request}  
    )
        return Response(response_serializer.data, status=status.HTTP_201_CREATED)
