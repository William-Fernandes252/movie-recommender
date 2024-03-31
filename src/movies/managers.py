from django.db import models

from . import querysets


class MovieManager(models.Manager):
    def get_queryset(self):
        return querysets.MovieQuerySet(self.model, using=self._db)

    def filter_outdated_rating(self):
        return self.get_queryset().filter_outdated_rating()

    def popular(self, reverse=False):
        return self.get_queryset().popular_on_demand(reverse=reverse)
