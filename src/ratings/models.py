from django.contrib.auth import get_user_model
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.db import models
from django.utils.translation import gettext_lazy as _

from ratings.querysets import RatingQuerySet


class RatingChoices(models.IntegerChoices):
    ONE = 1
    TWO = 2
    THREE = 3
    FOUR = 4
    FIVE = 5
    __empty__ = _("Rate this")


class Rating(models.Model):
    objects = RatingQuerySet.as_manager()

    user = models.ForeignKey(
        get_user_model(), on_delete=models.CASCADE, related_name="ratings"
    )
    value = models.SmallIntegerField(
        null=True, blank=True, choices=RatingChoices.choices
    )
    created = models.DateTimeField(auto_now_add=True)
    active = models.BooleanField(default=True)

    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.UUIDField()
    content_object = GenericForeignKey("content_type", "object_id")
