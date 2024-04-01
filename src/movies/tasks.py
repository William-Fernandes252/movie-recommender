from celery import shared_task
from django.contrib.contenttypes.models import ContentType
from django.db.models import Avg, Count
from django.utils import timezone

from exports import utils
from movies import managers, models
from movies.services import ml
from ratings.models import Rating
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

