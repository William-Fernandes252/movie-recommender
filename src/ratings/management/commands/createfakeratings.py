from django.contrib.contenttypes.models import ContentType
from django.core.management.base import BaseCommand

from ratings.tasks import generate_fake_ratings


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

        from ratings.models import Rating

        total = kwargs["total"]
        show_total = kwargs["show_total"]

        try:
            generate_fake_ratings(total)
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
