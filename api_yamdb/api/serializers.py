from rest_framework import serializers
from rest_framework.exceptions import ValidationError
from rest_framework.generics import get_object_or_404

from backend.models import Category, Genre, Title, User
from reviews.models import Comment, Review


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        exclude = ('id', )
        ordering = ['-id']


class GenreSerializer(serializers.ModelSerializer):
    class Meta:
        model = Genre
        exclude = ('id', )
        ordering = ['-id']


class TitleReadSerializer(serializers.ModelSerializer):
    genre = GenreSerializer(
        read_only=True,
        many=True)
    category = CategorySerializer(read_only=True)
    rating = serializers.IntegerField(read_only=True, required=False)

    class Meta:
        fields = '__all__'
        model = Title
        ordering = ['-id']


class TitleWriteSerializer(serializers.ModelSerializer):
    genre = serializers.SlugRelatedField(
        queryset=Genre.objects.all(),
        slug_field='slug',
        many=True
    )
    category = serializers.SlugRelatedField(
        queryset=Category.objects.all(),
        slug_field='slug'
    )

    class Meta:
        fields = '__all__'
        model = Title
        ordering = ['-id']


class SignupSerializer(serializers.ModelSerializer):
    """Сериализатор для проверки данных для регистрации пользователя"""
    username = serializers.CharField(required=True, allow_null=False)
    email = serializers.EmailField(required=True, allow_null=False)

    class Meta:
        model = User
        fields = ['username', 'email']
        ordering = ['username']

    # TODO: Попробовать упростить валидацию
    def validate(self, data):
        if data.get('username') == 'me':
            raise serializers.ValidationError(
                'Вы не можете использовать "me" как имя пользователя'
            )

        if User.objects.filter(username=data.get('username')).exists():
            raise serializers.ValidationError(
                'Этот username уже используется'
            )

        if User.objects.filter(email=data.get('email')).exists():
            raise serializers.ValidationError(
                'Этот email уже используется'
            )

        return data


class TokenSerializer(serializers.ModelSerializer):
    """Сериализатор для проверки токена"""
    username = serializers.CharField(required=True, allow_null=False)
    confirmation_code = serializers.CharField(required=True, allow_null=False)

    class Meta:
        model = User
        fields = ['username', 'confirmation_code']
        ordering = ['username']


class UserSerializer(serializers.ModelSerializer):
    """Сериализатор для проверки запросов о пользователях"""

    class Meta:
        model = User
        fields = ['username', 'email', 'first_name', 'last_name', 'bio',
                  'role']
        ordering = ['username']

    def validate_username(self, username):
        """Запрет & Проверка на использование 'me' как имя пользователя"""
        if username == 'me':
            raise serializers.ValidationError(
                'Вы не можете использовать "me" как имя пользователя'
            )
        return username


class UserRoleSerializer(serializers.ModelSerializer):
    """Сериализатор для запрета изменения роли пользователя"""
    role = serializers.CharField(read_only=True)

    class Meta:
        model = User
        fields = ['username', 'email', 'first_name', 'last_name', 'bio',
                  'role']
        ordering = ['username']

    def validate_username(self, username):
        """Запрет & Проверка на использование 'me' как имя пользователя"""
        if username == 'me':
            raise serializers.ValidationError(
                'Вы не можете использовать "me" как имя пользователя'
            )
        return username


class ReviewSerializer(serializers.ModelSerializer):
    author = serializers.SlugRelatedField(
        read_only=True,
        slug_field='username',
    )
    score = serializers.IntegerField(
        min_value=1,
        max_value=10,
    )

    def validate(self, data):
        request = self.context['request']
        title_id = self.context['view'].kwargs.get('title_id')
        title = get_object_or_404(Title, pk=title_id)

        if request.method == 'POST':
            if Review.objects.filter(
                    title=title,
                    author=request.user
            ).exists():
                raise ValidationError('Такой отзыв уже добавлен')

        return data

    class Meta:
        fields = ['id', 'text', 'author', 'score', 'pub_date']
        model = Review
        ordering = ['-pub_date']


class CommentSerializer(serializers.ModelSerializer):
    author = serializers.SlugRelatedField(
        read_only=True, slug_field='username')
    review = serializers.PrimaryKeyRelatedField(
        read_only=True,
    )

    class Meta:
        fields = ['id', 'text', 'author', 'pub_date', 'review']
        model = Comment
        read_only_fields = ['author', 'review']
        ordering = ['-pub_date']
