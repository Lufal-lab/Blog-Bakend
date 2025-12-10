# from django.urls import path
# from .views import PostListCreateView, PostDetailView

# urlpatterns = [
#     path("posts/", PostListCreateView.as_view(), name="post-list-create"),
#     path("posts/<int:pk>/", PostDetailView.as_view(), name="post-detail"),
# ]

from rest_framework.routers import DefaultRouter
from .viewsets import PostViewSet

router = DefaultRouter()
router.register(r'posts', PostViewSet, basename='posts')

urlpatterns = router.urls
