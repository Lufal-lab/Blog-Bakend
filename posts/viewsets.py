# from rest_framework import viewsets, status
# from rest_framework.response import Response
# from rest_framework.permissions import IsAuthenticatedOrReadOnly
# from django.db.models import Q

# from drf_spectacular.utils import (
#     extend_schema_view,
#     extend_schema,
#     OpenApiResponse,
#     OpenApiParameter
# )
# from .pagination import PostPagination

# from .models import Post
# from .serializers import PostSerializer, PostWriteSerializer, PostValidationErrorSerializer
# from .permissions import CanReadPost, CanEditPost


# class PostViewSet(viewsets.ModelViewSet):
#     queryset = Post.objects.all()
#     pagination_class = PostPagination

#     def get_permissions(self):
#         if self.action in ["list", "retrieve"]:
#             return [CanReadPost()]

#         if self.action in ["update", "partial_update", "destroy"]:
#             return [IsAuthenticatedOrReadOnly(), CanEditPost()]

#         if self.action == "create":
#             return [IsAuthenticatedOrReadOnly()]

#         return super().get_permissions()

#     def get_serializer_class(self):
#         if self.action in ["create", "update", "partial_update"]:
#             return PostWriteSerializer
#         return PostSerializer

#     def get_queryset(self):
#         user = self.request.user

#         print("USER:", user)
#         print("AUTH:", user.is_authenticated)

#         if self.action == "list":
#             if user.is_staff:  # superusuario o staff
#                 queryset = Post.objects.all()
#             elif not user.is_authenticated:
#                 queryset = Post.objects.filter(
#                     privacy_read=Post.PrivacyChoices.PUBLIC
#                 )
#             else:
#                 queryset = Post.objects.filter(
#                     Q(privacy_read=Post.PrivacyChoices.PUBLIC) |
#                     Q(privacy_read=Post.PrivacyChoices.AUTHENTICATED) |
#                     Q(privacy_read=Post.PrivacyChoices.AUTHOR, author=user) |
#                     Q(
#                         privacy_read=Post.PrivacyChoices.TEAM,
#                         author__team=user.team
#                     )
#                 ).distinct()

#         else:
#             queryset = Post.objects.all()

#         params = self.request.query_params

#         if "id" in params:
#             queryset = queryset.filter(id=params["id"])

#         if "author" in params:
#             queryset = queryset.filter(author_id=params["author"])

#         if "team" in params:
#             queryset = queryset.filter(author__team__name=params["team"])

#         if "privacy_read" in params:
#             queryset = queryset.filter(privacy_read=params["privacy_read"])

#         if "privacy_write" in params:
#             queryset = queryset.filter(privacy_write=params["privacy_write"])

#         if "created_from" in params:
#             queryset = queryset.filter(created_at__date__gte=params["created_from"])

#         if "created_to" in params:
#             queryset = queryset.filter(created_at__date__lte=params["created_to"])

#         return queryset.order_by("-created_at")

#     def create(self, request, *args, **kwargs):
#         serializer = PostWriteSerializer(data=request.data)
#         serializer.is_valid(raise_exception=True)

#         post = serializer.save(author=request.user)

#         response_serializer = PostSerializer(post)
#         return Response(response_serializer.data, status=status.HTTP_201_CREATED)

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

    def get_permissions(self):
        if self.action in ["list", "retrieve"]:
            return [CanReadPost()]

        if self.action in ["update", "partial_update", "destroy"]:
            return [IsAuthenticatedOrReadOnly(), CanEditPost()]

        if self.action == "create":
            return [IsAuthenticatedOrReadOnly()]

        return super().get_permissions()

    def get_serializer_class(self):
        if self.action in ["create", "update", "partial_update"]:
            return PostWriteSerializer
        return PostSerializer

    def get_queryset(self):
        user = self.request.user

        if self.action == "list":
            if user.is_staff:
                queryset = Post.objects.all()
            elif not user.is_authenticated:
                queryset = Post.objects.filter(
                    privacy_read=Post.PrivacyChoices.PUBLIC
                )
            else:
                queryset = Post.objects.filter(
                    Q(privacy_read=Post.PrivacyChoices.PUBLIC)
                    | Q(privacy_read=Post.PrivacyChoices.AUTHENTICATED)
                    | Q(privacy_read=Post.PrivacyChoices.AUTHOR, author=user)
                    | Q(
                        privacy_read=Post.PrivacyChoices.TEAM,
                        author__team=user.team,
                    )
                ).distinct()
        else:
            queryset = Post.objects.all()

        params = self.request.query_params

        if "id" in params:
            queryset = queryset.filter(id=params["id"])

        if "author" in params:
            queryset = queryset.filter(author_id=params["author"])

        if "team" in params:
            queryset = queryset.filter(author__team__name=params["team"])

        if "privacy_read" in params:
            queryset = queryset.filter(privacy_read=params["privacy_read"])

        if "privacy_write" in params:
            queryset = queryset.filter(privacy_write=params["privacy_write"])

        if "created_from" in params:
            queryset = queryset.filter(created_at__date__gte=params["created_from"])

        if "created_to" in params:
            queryset = queryset.filter(created_at__date__lte=params["created_to"])

        return queryset.order_by("-created_at")

    def create(self, request, *args, **kwargs):
        serializer = PostWriteSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        post = serializer.save(author=request.user)

        response_serializer = PostSerializer(post)
        return Response(response_serializer.data, status=status.HTTP_201_CREATED)
