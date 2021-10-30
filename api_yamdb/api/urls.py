from django.urls import include, path
from rest_framework.routers import DefaultRouter

from api.views import (CategoryViewSet, CommentViewSet, GenreViewSet,
                       ReviewViewSet, SignupAPI, TitleViewSet, TokenAPI,
                       UserViewSet)

# Регистрация роутера и вьюсетов для API v1
router_v1 = DefaultRouter()
router_v1.register('users', UserViewSet, basename='user')
router_v1.register('categories', CategoryViewSet, basename='category')
router_v1.register('genres', GenreViewSet, basename='genre')
router_v1.register(
    r'titles/(?P<title_id>\d+)/reviews',
    ReviewViewSet,
    basename='review'
)
router_v1.register(
    r'titles/(?P<title_id>\d+)/reviews/(?P<review_id>\d+)/comments',
    CommentViewSet,
    basename='comment'
)
router_v1.register('titles', TitleViewSet, basename='title')

# Urls для API v1
api_urls_v1 = [
    path('auth/signup/', SignupAPI.as_view(), name='signup'),
    path('auth/token/', TokenAPI.as_view(), name='token'),
    path('', include(router_v1.urls))
]

urlpatterns = [
    path('v1/', include(api_urls_v1))
]
