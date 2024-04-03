from django.core.management.base import BaseCommand, CommandParser


class Command(BaseCommand):
    help = "Create movie suggestions for users"

    def add_arguments(self, parser: CommandParser):
        parser.add_argument(
            "--start",
            default=0,
            type=int,
            help="The movie page to start.",
        )
        parser.add_argument(
            "--offset",
            default=50,
            type=int,
            help="The movies batch size.",
        )
        parser.add_argument(
            "--max",
            default=250,
            type=int,
            help="The number of movies to generate suggestions.",
        )
        parser.add_argument(
            "--reuse-suggestions-up-to-days",
            type=int,
            default=7,
            help="The number of days to consider current suggestions as still valid.",
        )

    def handle(self, *args, **options):
        from movies.tasks import batch_user_prediction

        total = len(
            batch_user_prediction(
                start=options["start"],
                offset=options["offset"],
                max=options["max"],
                use_suggestions_up_to_days=options["reuse_suggestions_up_to_days"],
            )
        )

        self.stdout.write(
            self.style.SUCCESS(f"Successfully created {total} movie suggestions.")
        )
