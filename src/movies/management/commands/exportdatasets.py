from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = "Export movies and movie ratings datasets for training models."

    def handle(self, *args, **options):
        import threading

        from movies.tasks import export_movie_ratings_dataset, export_movies_dataset

        threads = [
            threading.Thread(target=export_movies_dataset),
            threading.Thread(target=export_movie_ratings_dataset),
        ]
        for thread in threads:
            thread.start()

        for thread in threads:
            thread.join()

        self.stdout.write(self.style.SUCCESS("Successfully exported datasets."))
