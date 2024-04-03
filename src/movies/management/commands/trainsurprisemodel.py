from django.core.management.base import BaseCommand, CommandParser


class Command(BaseCommand):
    help = "Train a surprise model using the latest exported datasets."

    def add_arguments(self, parser: CommandParser) -> None:
        parser.add_argument(
            "--epochs",
            default=20,
            type=int,
            help="Number of epochs to train the model.",
        )

    def handle(self, *args, **kwargs):
        from movies.tasks import train_and_export_surprise_model

        train_and_export_surprise_model(epochs=kwargs["epochs"])

        self.stdout.write(self.style.SUCCESS("Successfully trained the model."))
