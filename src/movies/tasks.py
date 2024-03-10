from celery import shared_task
from django.contrib.contenttypes.models import ContentType
from django.db.models import Avg, Count
from django.utils import timezone
from ratings.models import Rating

from movies import managers, models


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
