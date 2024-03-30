import random

from celery import shared_task

from movies.models import Movie
from movies.tests.factories import MovieRatingFactory
from users.models import User


@shared_task(name="generate_fake_ratings")
def generate_fake_ratings(count: int):
    """Generates fake ratings for movies.

    Args:
        count (int): The number of ratings to be created.

    Returns:
        int: the number of ratings created.
    """
    movie_ids = Movie.objects.values_list("id", flat=True)
    user_ids = User.objects.values_list("id", flat=True)
    ratings = []
    for _ in range(count):
        ratings.append(
            MovieRatingFactory.create(
                content_object=Movie.objects.get(pk=random.choice(movie_ids)),
                user=User.objects.get(pk=random.choice(user_ids)),
            )
        )
    return len(ratings)
