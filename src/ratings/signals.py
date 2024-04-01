from suggestions.models import Suggestion

from ratings import models
from ratings.querysets import RatingQuerySet


def deactivate_old_ratings(
    sender: type[models.Rating], instance: models.Rating, created: bool, **kwargs
):
    """Deactivate users old ratings for a object when a new one is created."""
    if created:
        id = instance.pk
        if instance.active:
            old_ratings_queryset: RatingQuerySet = (
                models.Rating.objects.all()
                .filter(
                    user=instance.user,
                    content_type=instance.content_type,
                    object_id=instance.object_id,
                )
                .exclude(pk=id, active=True)
            )
            if old_ratings_queryset.exists():
                old_ratings_queryset.deactivate()
                instance.active = True
                instance.save()
        if (
            suggestion_queryset := Suggestion.objects.filter(
                user=instance.user,
                content_type=instance.content_type,
                object_id=instance.object_id,
                rating__isnull=True,
            )
        ).exists():
            suggestion_queryset.update(rating=instance)
