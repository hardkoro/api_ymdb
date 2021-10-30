from django.contrib.auth.models import AbstractUser
from django.db import models

from api.validators import validate_year


# Кастомные роли для пользователей
USER = 'user'
MODERATOR = 'moderator'
ADMIN = 'admin'
CHOICES_ROLES = (
    (USER, 'Аутентифицированный пользователь'),
    (MODERATOR, 'Модератор'),
    (ADMIN, 'Администратор'),
)


class User(AbstractUser):
    """Создание своей модели User с кастомными полями"""
    email = models.EmailField(unique=True, db_index=True)
    role = models.CharField(
        max_length=16, choices=CHOICES_ROLES, default='user', db_index=True)
    bio = models.TextField('Биография', blank=True)
    confirmation_code = models.CharField(max_length=256, null=True, blank=True)

    class Meta:
        # Комбинация username & email должна быть уникальная
        constraints = [
            models.UniqueConstraint(
                fields=['username', 'email'], name='one_email_one_account'
            ),
        ]
        ordering = ['username']

    def is_admin(self):
        return self.role == ADMIN

    def is_moderator(self):
        return self.role == MODERATOR

    def is_user(self):
        return self.role == USER

    def __str__(self):
        return self.username


class Category(models.Model):
    name = models.CharField(max_length=256)
    slug = models.CharField(max_length=50, unique=True, db_index=True)

    class Meta:
        ordering = ['-id']

    def __str__(self):
        return self.name


class Genre(models.Model):
    name = models.CharField(max_length=50)
    slug = models.CharField(max_length=50, unique=True, db_index=True)

    class Meta:
        ordering = ['-id']

    def __str__(self):
        return self.name


class Title(models.Model):
    name = models.CharField(max_length=150, db_index=True)
    year = models.IntegerField(
        blank=True,
        null=True,
        validators=(validate_year, ))
    description = models.TextField()
    genre = models.ManyToManyField(
        Genre,
        related_name='titles',
        blank=True)
    category = models.ForeignKey(
        Category,
        on_delete=models.SET_NULL,
        related_name='titles',
        blank=True,
        null=True)

    class Meta:
        ordering = ['-id']

    def __str__(self):
        return f'{self.name} ({self.year})'
