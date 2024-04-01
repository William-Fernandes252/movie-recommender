from django.contrib.auth import get_user_model
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.db import models

from suggestions.managers import SuggestionManager


class Suggestion(models.Model):
    user = models.ForeignKey(
        get_user_model(), on_delete=models.CASCADE, related_name="suggestions"
    )
    value = models.FloatField(null=True, blank=True)
    created = models.DateTimeField(auto_now_add=True)
    rating = models.ForeignKey(
        "ratings.Rating",
        on_delete=models.PROTECT,
        related_name="suggestions",
        null=True,
        blank=True,
    )

    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.BigIntegerField()
    content_object = GenericForeignKey("content_type", "object_id")
    active = models.BooleanField(default=True)

    objects = SuggestionManager()

    @property
    def did_rate(self):
        """Returns the date when the user rated the suggested content."""
        return self.rating.created if self.rating else None
