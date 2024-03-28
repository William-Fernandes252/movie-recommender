from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = "Update movie ratings."

    def add_arguments(self, parser):
        parser.add_argument(
            "count",
            nargs="?",
            type=int,
            help="Number of movies to update",
            default=None,
        )
        parser.add_argument(
            "--all",
            action="store_true",
            default=False,
            help="Update all the movies in the database",
        )

    def handle(self, *args, **kwargs):
        from movies.tasks import update_movie_ratings

        all = kwargs["all"]
        count = kwargs["count"]
        try:
            updated = update_movie_ratings(all, count)
            self.stdout.write(
                self.style.SUCCESS(f"Ratings of {updated} movies updated successfully")
            )
        except Exception as exc:
            self.stdout.write(self.style.ERROR(str(exc)))
            return
