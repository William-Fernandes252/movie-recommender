from movies import models
from movies.tasks import update_movie_position_embeddings


def recalculate_movie_embeddings_on_delete(sender: type[models.Movie], *args, **kwargs):
    """Updates the movie embeddings when a movie is deleted.

    This is necessary to keep the embeddings in sync with the movies data,
    as deletions create gaps on the positions, which can compromise the
    value and quality of suggestions.
    """
    update_movie_position_embeddings()


def recalculate_movie_embeddings_on_save(
    sender: type[models.Movie], instance: models.Movie, created: bool, *args, **kwargs
):
    """Updates the movie embeddings when a movie is saved."""
    if created and instance.pk:
        update_movie_position_embeddings()
