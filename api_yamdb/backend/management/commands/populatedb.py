import codecs
import csv
import os

from backend.models import Category, Genre, Title, User
from django.core.management.base import BaseCommand, CommandError
from reviews.models import Comment, Review

CATEGORY = 'category.csv'
COMMENT = 'comments.csv'
GENRES = 'genre.csv'
GENRE_TITLE = 'genre_title.csv'
REVIEW = 'review.csv'
TITLES = 'titles.csv'
USERS = 'users.csv'

MODEL_FILE_NAMES = {
    CATEGORY: Category,
    COMMENT: Comment,
    GENRES: Genre,
    REVIEW: Review,
    TITLES: Title,
    USERS: User
}


class Command(BaseCommand):
    help = 'Populates DB with data from specified csv-file'

    def add_arguments(self, parser):
        parser.add_argument('csv_file', nargs=1, type=open)

    def genres_or_categories(data, model):
        [
            model.objects.create(
                id=row.get('id'),
                name=row.get('name'),
                slug=row.get('slug')
            ) for row in data
        ]

    def add_users(data, model):
        [
            model.objects.create(
                id=row.get('id'),
                password=row.get('password'),
                username=row.get('username'),
                email=row.get('email'),
                role=row.get('user_role'),
                first_name=row.get('first_name'),
                last_name=row.get('last_name'),
                is_superuser=row.get('is_superuser'),
                is_staff=row.get('is_staff'),
                is_active=row.get('is_active'),
                date_joined=row.get('date_joined'),
                bio=row.get('bio')
            ) for row in data
        ]

    def add_genre_titles(data):
        for row in data:
            title = Title.objects.get(id=row.get('title_id'))
            genre = Genre.objects.get(id=row.get('genre_id'))
            title.genre.add(genre)
            title.save()

    def add_titles(data, model):
        [
            model.objects.create(
                id=row.get('id'),
                name=row.get('name'),
                year=row.get('year'),
                category=Category.objects.get(
                    id=row.get('category')
                )
            ) for row in data
        ]

    def add_reviews(data, model):
        [
            model.objects.create(
                id=row.get('id'),
                title=Title.objects.get(
                    id=row.get('title_id')
                ),
                text=row.get('text'),
                author=User.objects.get(
                    pk=row.get('author')
                ),
                pub_date=row.get('pub_date'),
                score=row.get('score'),
            ) for row in data
        ]

    def add_comments(data, model):
        [
            model.objects.create(
                id=row.get('id'),
                review=Review.objects.get(
                    id=row.get('review_id')
                ),
                text=row.get('text'),
                author=User.objects.get(
                    pk=row.get('author')
                ),
                pub_date=row.get('pub_date'),
            ) for row in data
        ]

    def handle(self, *args, **options):
        for csv_file in options['csv_file']:
            try:
                with codecs.open(csv_file.name, 'r', 'utf-8') as f:
                    data = csv.DictReader(f)
                    file_name = os.path.basename(csv_file.name)

                    if file_name == GENRES or file_name == CATEGORY:
                        model = MODEL_FILE_NAMES.get(file_name)
                        self.add_genres_or_categories(data, model)
                    elif file_name == USERS:
                        model = MODEL_FILE_NAMES.get(file_name)
                        self.add_users(data, model)
                    elif file_name == GENRE_TITLE:
                        self.add_genre_titles
                    elif file_name == TITLES:
                        model = MODEL_FILE_NAMES.get(file_name)
                        self.add_titles(data, model)
                    elif file_name == REVIEW:
                        model = MODEL_FILE_NAMES.get(file_name)
                        self.add_reviews(model, data)
                    elif file_name == COMMENT:
                        model = MODEL_FILE_NAMES.get(file_name)
                        self.add_comments(model, data)
            except Exception as e:
                raise CommandError(f'Population failed: {e}')

        self.stdout.write(
            self.style.SUCCESS('Successfully populated db')
        )
