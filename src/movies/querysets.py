from django.db import models
from django.utils import timezone

MOVIE_RATING_RECALCULATE_MINUTES = 10


class MovieQuerySet(models.QuerySet):
    def filter_outdated_rating(self):
        now = timezone.now()
        return self.filter(
            models.Q(rating_last_updated__isnull=True)
            | models.Q(
                rating_last_updated__lte=now
                - timezone.timedelta(minutes=MOVIE_RATING_RECALCULATE_MINUTES)
            )
        )
