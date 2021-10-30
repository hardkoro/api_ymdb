from django.conf import settings
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import send_mail
from django.db.models import Avg
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, permissions, status, viewsets
from rest_framework.decorators import action
from rest_framework.filters import SearchFilter
from rest_framework.pagination import (LimitOffsetPagination,
                                       PageNumberPagination)
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.viewsets import ModelViewSet

from api.filters import TitleFilter
from api.permissions import (ReviewPermissions, CommentPermissions,
                             IsAdminOrReadOnly, IsAdminOrSuperuser)
from api.serializers import (CategorySerializer, CommentSerializer,
                             GenreSerializer, ReviewSerializer,
                             SignupSerializer, TitleReadSerializer,
                             TitleWriteSerializer, TokenSerializer,
                             UserRoleSerializer, UserSerializer)
from api.tokens import get_tokens_for_user
from backend.models import Category, Genre, Title, User
from reviews.models import Review
from .mixins import CreateDestroyListViewSet


class CategoryViewSet(CreateDestroyListViewSet):
    """ViewSet для работы с категориями контента"""
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = (IsAdminOrReadOnly,)
    filter_backends = (SearchFilter,)
    search_fields = ('name',)
    pagination_class = LimitOffsetPagination
    lookup_field = 'slug'


class GenreViewSet(CreateDestroyListViewSet):
    """ViewSet для работы с жанрами"""
    queryset = Genre.objects.all()
    serializer_class = GenreSerializer
    permission_classes = (IsAdminOrReadOnly,)
    filter_backends = (SearchFilter,)
    search_fields = ('name',)
    pagination_class = LimitOffsetPagination
    lookup_field = 'slug'


class CommentViewSet(ModelViewSet):
    """ViewSet для работы с комментариями"""
    serializer_class = CommentSerializer
    permission_classes = (CommentPermissions,)
    pagination_class = LimitOffsetPagination

    def get_queryset(self):
        review = get_object_or_404(Review, pk=self.kwargs.get('review_id'))
        return review.comments.all()

    def perform_create(self, serializer):
        review = get_object_or_404(Review, pk=self.kwargs.get('review_id'))
        serializer.save(author=self.request.user, review=review)


class ReviewViewSet(viewsets.ModelViewSet):
    serializer_class = ReviewSerializer
    permission_classes = (ReviewPermissions,)
    pagination_class = PageNumberPagination

    def get_queryset(self):
        title = get_object_or_404(Title, id=self.kwargs.get('title_id'))
        return title.reviews.all()

    def perform_create(self, serializer):
        title = get_object_or_404(Title, id=self.kwargs.get('title_id'))
        serializer.save(author=self.request.user, title_id=title.id)


class TitleViewSet(ModelViewSet):
    """ViewSet для работы с произведениями"""
    queryset = Title.objects.annotate(rating=Avg(
        'reviews__score')).order_by('-id')
    permission_classes = (IsAdminOrReadOnly,)
    filter_backends = (DjangoFilterBackend,)
    filterset_class = TitleFilter
    pagination_class = LimitOffsetPagination

    def get_serializer_class(self):
        if self.request.method in ['POST', 'PATCH']:
            return TitleWriteSerializer
        return TitleReadSerializer


class SignupAPI(APIView):
    permission_classes = (permissions.AllowAny,)

    def post(self, request):
        serializer = SignupSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        user = get_object_or_404(
            User,
            username=serializer.validated_data.get('username')
        )
        confirmation_code = default_token_generator.make_token(user)
        send_mail(
            'Your Confirmation Code',
            f'Your Confirmation Code is {confirmation_code}',
            settings.NO_REPLY_EMAIL,
            [serializer.validated_data['email']],
            fail_silently=False,
        )
        return Response(serializer.validated_data, status=status.HTTP_200_OK)


class TokenAPI(APIView):
    """Класс проверки кода подтверждения и выдачи JWT токена"""
    permission_classes = (permissions.AllowAny,)

    def post(self, request):
        """Кастомизация обработки POST (единственный рабочий метод)"""
        serializer = TokenSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = get_object_or_404(
            User, username=serializer.validated_data.get('username')
        )
        # Проверка корректности кода
        confirmation_code = default_token_generator.check_token(
            user,
            serializer.validated_data.get('confirmation_code')
        )
        # Выдать JWT токен, если confirmation_code корректный
        if confirmation_code:
            token = get_tokens_for_user(user)
        else:
            return Response(
                {'confirmation_code': 'Неправильный код подтверждения'},
                status=status.HTTP_400_BAD_REQUEST
            )
        return Response(token, status=status.HTTP_201_CREATED)


class UserViewSet(viewsets.ModelViewSet):
    """ViewSet для обработки запросов о пользователях"""
    lookup_field = 'username'  # Обработка users/{username}
    queryset = User.objects.all()
    permission_classes = (IsAdminOrSuperuser, permissions.IsAuthenticated,)
    serializer_class = UserSerializer
    pagination_class = PageNumberPagination
    filter_backends = (filters.SearchFilter,)
    search_fields = ('username',)

    @action(
        methods=['GET', 'PATCH'],
        permission_classes=[permissions.IsAuthenticated],
        detail=False
    )
    def me(self, request):
        """Обработка запроса url'а users/me"""
        user = request.user
        # Вернуть информацию пользователю о себе на запрос GET
        if request.method == 'GET':
            serializer = UserSerializer(user)
            return Response(
                serializer.data,
                status=status.HTTP_200_OK
            )
        # Обработка запроса на изменение
        elif request.method == 'PATCH':
            serializer = UserRoleSerializer(
                request.user, data=request.data, partial=True)

            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(
                serializer.data,
                status=status.HTTP_200_OK
            )
