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

    def popular_on_demand(self, reverse=False):
        order_by = models.F("computed_score")
        if not reverse:
            order_by = order_by.desc(nulls_last=True)
        return self.annotate(
            computed_score=models.Sum(
                models.F("ratings_average") * models.F("ratings_count"),
                output_field=models.FloatField(),
            ),
        ).order_by(order_by)
