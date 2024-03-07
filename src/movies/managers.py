from django.db import models

from . import querysets


class MovieManager(models.Manager):
    def get_queryset(self):
        return querysets.MovieQuerySet(self.model, using=self._db)

    def filter_outdated_rating(self):
        return self.get_queryset().filter_outdated_rating()
