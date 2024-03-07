import random

from django.contrib.contenttypes.models import ContentType
from django.core.management.base import BaseCommand

from auth.models import User


class Command(BaseCommand):
    help = "Create fake ratings for movies."

    def add_arguments(self, parser):
        parser.add_argument(
            "total",
            nargs="?",
            type=int,
            help="Indicates the number of ratings to be created",
            default=10,
        )
        parser.add_argument(
            "--show-total",
            action="store_true",
            default=False,
            help="Show the total number of movie ratings in the database after the command runs",  # noqa
        )

    def handle(self, *args, **kwargs):
        from movies.models import Movie

        from movies.tests.factories import MovieRatingFactory
        from ratings.models import Rating

        total = kwargs["total"]
        show_total = kwargs["show_total"]

        movie_ids = Movie.objects.values_list("id", flat=True)
        user_ids = User.objects.values_list("id", flat=True)
        for _ in range(total):
            try:
                MovieRatingFactory.create(
                    content_object=Movie.objects.get(pk=random.choice(movie_ids)),
                    user=User.objects.get(pk=random.choice(user_ids)),
                )
            except Exception as exc:
                self.stdout.write(self.style.ERROR(str(exc)))
                return

        self.stdout.write(self.style.SUCCESS(f"{total} ratings created successfully"))

        if show_total:
            movie_ratings_count = Rating.objects.filter(
                content_type=ContentType.objects.get_for_model(Movie)
            ).count()
            self.stdout.write(
                self.style.WARNING(
                    f"There are {movie_ratings_count} movie ratings in the database."
                )
            )
