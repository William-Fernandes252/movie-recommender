from django.contrib.contenttypes.models import ContentType
from django.db import models
from django.utils import timezone


class SuggestionManager(models.Manager):
    def recent(
        self,
        content_type: ContentType,
        objects_ids: list[int],
        users_ids: list[int],
        days: int = 7,
    ):
        """Returns recently created suggestions of the specified objects for the given users.

        Args:
            content_type (ContentType): The content type of the objects.
            objects_ids (list[int]): The IDs of the objects.
            users_ids (list[int]): The IDs of the users.
            days (int, optional): The number of days to consider. Defaults to 7.

        Returns:
            QuerySet: The suggestions queryset.
        """
        return self.get_queryset().filter(
            content_type=content_type,
            object_id__in=objects_ids,
            user_id__in=users_ids,
            active=True,
            created__gte=timezone.now() - timezone.timedelta(days=days),
        )
