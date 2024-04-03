from django.apps import AppConfig
from django.db.models.signals import post_delete, post_save


class MoviesConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "movies"

    def ready(self):
        from movies import models, signals

        post_delete.connect(
            signals.recalculate_movie_embeddings_on_delete, sender=models.Movie
        )
        post_save.connect(
            signals.recalculate_movie_embeddings_on_save, sender=models.Movie
        )
