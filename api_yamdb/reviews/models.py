from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models

from backend.models import Title, User


class Review(models.Model):
    text = models.TextField()
    pub_date = models.DateTimeField(
        'Дата публикации', auto_now_add=True, db_index=True
    )
    title = models.ForeignKey(
        Title, on_delete=models.CASCADE, related_name='reviews'
    )
    author = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='reviews')
    score = models.PositiveSmallIntegerField(
        default=1,
        validators=[MinValueValidator(1, 'Значение должно быть от 1 до 10'),
                    MaxValueValidator(10, 'Значение должно быть от 1 до 10')],
        db_index=True,
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['title', 'author'],
                name='only 1 comment per author for title')
        ]
        ordering = ['pub_date']
        verbose_name = 'review of a work'
        verbose_name_plural = 'reviews of a work'

    def __str__(self):
        return self.text


class Comment(models.Model):
    text = models.TextField(verbose_name='comment text')
    pub_date = models.DateTimeField(
        'Дата публикации комментария', auto_now_add=True, db_index=True)
    review = models.ForeignKey(
        Review,
        on_delete=models.CASCADE,
        related_name='comments',
        verbose_name='review of a work')
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='comments',
        verbose_name='comment author')

    class Meta:
        ordering = ['pub_date']
        verbose_name = 'comment to review'
        verbose_name_plural = 'comments to review'

    def __str__(self):
        return self.text
