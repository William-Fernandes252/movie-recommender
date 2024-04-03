from celery import shared_task
from django.contrib.contenttypes.models import ContentType
from django.db.models import Avg, Count, F, Window
from django.db.models.functions import DenseRank
from django.utils import timezone

from exports import utils
from movies import managers, models
from movies.services import ml
from ratings.models import Rating
from suggestions.models import Suggestion
from users.models import User


def update_movie_ratings(all=False, count: int | None = None):
    """Updates movies ratings data (average and count).

    Args:
        all (bool, optional): If True, all the movies in the database are updated,
        only movies with outdated ratings information are updated otherwise.
        Defaults to False.
        count (int, optional): The number of movies to update. Defaults to None.

    Returns:
        int: The number of movies updated.
    """
    content_type = ContentType.objects.get_for_model(models.Movie)

    aggregated_ratings = (
        Rating.objects.filter(content_type=content_type)
        .values("object_id")
        .annotate(average=Avg("value"), count=Count("object_id"))
    )

    queryset: managers.MovieManager = models.Movie.objects.all().order_by(
        "rating_last_updated"
    )
    if not all:
        queryset = queryset.filter_outdated_rating()

    updated = 0
    for agg in aggregated_ratings:
        queryset.filter(pk=agg["object_id"]).update(
            ratings_average=agg["average"],
            ratings_count=agg["count"],
            score=agg["average"] * agg["count"],
            rating_last_updated=timezone.now(),
        )
        updated += 1
        if count and updated >= count:
            break
    return updated


@shared_task(name="update_movie_ratings_outdated")
def update_movie_ratings_outdated():
    """Updates outdated movies ratings data."""
    return update_movie_ratings()


@shared_task(name="export_movie_ratings_dataset")
def export_movie_ratings_dataset(filename: str | None = None) -> str | None:
    """Exports a dataset with the movies ratings average and count.

    Args:
        filename (str | None, optional): A name for the destination file. Defaults to `movies_ratings`.

    Returns:
        Export | None: The export file path.
    """
    export = utils.export_dataset("movies", "movie", filename)
    return export.file.path if export else None


@shared_task
def train_and_export_surprise_model(epochs: int = 20):
    """Trains a model using the Surprise library and exports it to a file.

    Args:
        epochs (int, optional): The number of epochs to train the model. Defaults to 20.

    Returns:
        str: The path to the exported model file.
    """
    model, accuracy, _ = ml.train_surprise_model(epochs)
    model_name = ml.get_model_name_from_accuracy(accuracy)
    return ml.export_model(model, model_name)


@shared_task
def batch_user_prediction(
    users_ids: list[int] | None = None,
    start: int = 0,
    offset: int = 50,
    max: int = 1000,
    use_suggestions_up_to_days: int | None = 7,
) -> list[int]:
    """Generates suggestions for a batch of users.

    Args:
        users_ids (list[int] | None, optional): The users to generate suggestions to.
        Defaults to the users that interacted with the application recently.
        start (int, optional): The movie to start to suggest. Defaults to 0.
        offset (int, optional): The amount of suggestions to create per batch. Defaults to 50.
        max (int, optional): The max number of movies to suggest. Defaults to 1000.
        use_suggestions_up_to_days (int | None, optional): Skip suggestions for movies
        that were suggested to the users in the last days. Defaults to 7.

    Raises:
        ValueError: If the model is not found.

    Returns:
        list[int]: The IDs of the created suggestions.
    """

    model = ml.load_model()
    if not model:
        raise ValueError("Model not found.")

    if users_ids is None:
        users_ids = User.objects.recent(ids_only=True)

    end = start + offset
    movies_ids: list[int] = (
        models.Movie.objects.all().popular().values_list("id", flat=True)[start:end]
    )

    recent_suggestions = {}
    if use_suggestions_up_to_days:
        recent_suggestions = models.Movie.objects.recent_suggestions(
            users_ids, movies_ids
        )

    ctype = ContentType.objects.get_for_model(models.Movie)
    ids: list[int] = []
    count = 0
    while count < max:
        suggestions: list[Suggestion] = []
        for movie_id in movies_ids:
            users_covered = recent_suggestions.get(movie_id, [])
            for user_id in users_ids:
                if user_id in users_covered:
                    continue
                suggestions.append(
                    Suggestion(
                        user_id=user_id,
                        content_type=ctype,
                        object_id=movie_id,
                        value=model.predict(uid=user_id, iid=movie_id).est,
                    )
                )
            count += 1
        ids.extend(
            suggestion.id for suggestion in Suggestion.objects.bulk_create(suggestions)
        )

        start += offset
        end = start + offset  # Update end for the next iteration
        movies_ids = (
            models.Movie.objects.all()
            .popular()
            .values_list("id", flat=True)[start : start + offset]
        )

    return ids


@shared_task
def update_movie_position_embeddings():
    """Update the movies embeddings.

    Returns:
        int: The number of movies updated.
    """
    updated = 0
    for movie in (
        models.Movie.objects.all()
        .annotate(embedding_index=Window(DenseRank(), order_by=[F("id").asc()]))
        .annotate(new_index=F("embedding_index") - 1)
    ):
        if movie.index != getattr(movie, "new_index", None):
            movie.index = getattr(movie, "new_index", None)
            movie.save()
            updated += 1
    return updated
