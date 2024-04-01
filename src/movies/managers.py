from django.contrib.contenttypes.models import ContentType
from django.db import models

from movies import querysets
from suggestions.models import Suggestion


class MovieManager(models.Manager):
    def get_queryset(self):
        return querysets.MovieQuerySet(self.model, using=self._db)

    def filter_outdated_rating(self):
        return self.get_queryset().filter_outdated_rating()

    def popular(self, reverse=False):
        return self.get_queryset().popular_on_demand(reverse=reverse)

    def recent_suggestions(
        self,
        users_ids: list[int],
        movies_ids: list[int],
        days: int = 7,
    ) -> dict[int, list[int]]:
        """Returns the recent suggestions for the given users and movies.

        Args:
            users_ids (list[int]): The IDs of the users.
            movies_ids (list[int]): The IDs of the movies.
            days (int, optional): Days to consider. Defaults to 7.

        Returns:
            dict[int, list[int]]: A dictionary mapping movies to the users each movie
            was suggested to.
        """
        data: dict[int, list[int]] = {}
        for item in (
            Suggestion.objects.recent(
                content_type=ContentType.objects.get_for_model(self.model),
                objects_ids=movies_ids,
                users_ids=users_ids,
                days=days,
            )
            .annotate(
                **{"movieId": models.F("object_id"), "userId": models.F("user_id")}
            )
            .values("movieId", "userId")
        ):
            if item["movieId"] not in data:
                data[item["movieId"]] = []
            data[item["movieId"]].append(item["userId"])
        return data
