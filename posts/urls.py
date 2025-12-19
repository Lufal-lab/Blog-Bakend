from rest_framework_nested import routers
from posts.viewsets import PostViewSet
from comments.viewsets import CommentViewSet
from likes.viewsets import LikeViewSet

router = routers.DefaultRouter()
router.register(r'posts', PostViewSet, basename='posts')

# Nested routers
posts_router = routers.NestedDefaultRouter(router, r'posts', lookup='post')
posts_router.register(r'comments', CommentViewSet, basename='post-comments')
posts_router.register(r'likes', LikeViewSet, basename='post-likes')

urlpatterns = router.urls + posts_router.urls
