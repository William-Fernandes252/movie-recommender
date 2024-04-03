from django.contrib.contenttypes.models import ContentType
from django.db import models

from movies import querysets
from suggestions.models import Suggestion


class MovieManager(models.Manager):
    def get_queryset(self) -> querysets.MovieQuerySet:
        return querysets.MovieQuerySet(self.model, using=self._db)

    def filter_outdated_rating(self) -> querysets.MovieQuerySet:
        return self.get_queryset().filter_outdated_rating()

    def popular(self, reverse=False) -> querysets.MovieQuerySet:
        return self.get_queryset().popular_on_demand(reverse=reverse)

    def order_by_ids(self, ids: list[int]) -> querysets.MovieQuerySet:
        """Orders the queryset by the given IDs.

        Args:
            ids (list[int]): The IDs to order by.

        Returns:
            QuerySet: The ordered queryset.
        """
        return (
            self.get_queryset()
            .filter(pk__in=ids)
            .order_by(
                models.Case(
                    *[models.When(pk=pk, then=pos) for pos, pk in enumerate(ids)]
                )
            )
        )

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

    def to_dataset(self) -> models.QuerySet:
        """Generates a dataset with the movies data.

        The dataset is generated as a values queryset with the following columns:
        - movieId
        - movieIndex
        - title
        - releasedAt
        - ratingsAverage
        - ratingsCount

        Returns:
            QuerySet: The movies dataset.
        """
        return (
            self.get_queryset()
            .annotate(
                **{
                    "movieId": models.F("pk"),
                    "movieIndex": models.F("index"),
                    "releasedAt": models.F("released"),
                    "ratingsAverage": models.F("ratings_average"),
                    "ratingsCount": models.F("ratings_count"),
                }
            )
            .values(
                "movieId",
                "movieIndex",
                "title",
                "releasedAt",
                "ratingsAverage",
                "ratingsCount",
            )
        )
