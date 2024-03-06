from django.db import models

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
