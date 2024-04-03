from django.contrib.contenttypes.models import ContentType
from django.db import models
from django.db.models import F, QuerySet

from ratings.querysets import RatingQuerySet


class RatingManager(models.Manager):
    def get_queryset(self):
        return RatingQuerySet(self.model, using=self._db)

    def active(self):
        """Return only active ratings."""
        return self.get_queryset().active()

    def inactive(self):
        """Return only inactive ratings."""
        return self.get_queryset().inactive()

    def average(self):
        return self.get_queryset().average()

    def to_dataset(
        self,
        content_type: ContentType,
        item_column_name: str | None = None,
    ) -> QuerySet:
        """Generates a dataset with the active ratings.

        The dataset is generated as a values queryset with the following columns:
        - userId
        - `item_column_name` (defaults to the model name)
        - rating
        - createdAt

        Args:
            content_type (ContentType): The content type of the model.
            item_column_name (str | None, optional): A name for the item id column.
            Defaults to the model name.

        Returns:
            QuerySet: The ratings dataset (as a values queryset) for the given model.
        """
        item_column_name = (
            item_column_name or content_type.model_class()._meta.model_name
        )
        return (
            self.filter(
                content_type=content_type,
                object_id=F("object_id"),
                active=True,
            )
            .annotate(
                **{
                    "userId": F("user_id"),
                    item_column_name: F("object_id"),
                    "rating": F("value"),
                    "createdAt": F("created"),
                }
            )
            .values("userId", "movieId", "rating", "createdAt")
        )
