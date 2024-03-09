from celery import shared_task

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
    queryset: managers.MovieManager = models.Movie.objects.all()
    if not all:
        queryset = queryset.filter_outdated_rating()
    queryset = queryset.order_by("rating_last_updated")
    if count:
        queryset = queryset[:count]

    movies: list[models.Movie] = [movie for movie in queryset]
    for movie in movies:
        movie.update_ratings_average()

    return len(movies)


@shared_task(name="update_movie_ratings_outdated")
def update_movie_ratings_outdated():
    """Updates outdated movies ratings data."""
    return update_movie_ratings()
