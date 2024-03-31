from decimal import Decimal

from django.contrib.contenttypes.fields import GenericRelation
from django.db import models
from django.urls import reverse
from django.utils import timezone
from django_extensions.db.models import TimeStampedModel

from movies import managers
from ratings.managers import RatingManager
from ratings.models import Rating


class Movie(TimeStampedModel, models.Model):
    title = models.CharField(max_length=255, unique=True)
    overview = models.TextField()
    released = models.DateField(blank=True, null=True)
    ratings: RatingManager = GenericRelation(Rating)
    ratings_average = models.DecimalField(
        max_digits=5, decimal_places=2, blank=True, null=True
    )
    ratings_count = models.PositiveIntegerField(blank=True, null=True)
    rating_last_updated = models.DateTimeField(blank=True, null=True)
    score = models.FloatField(blank=True, null=True)

    objects = managers.MovieManager()

    def get_absolute_url(self):
        return reverse("movie-detail", kwargs={"pk": self.pk})

    def get_ratings_average(self):
        """Calculates the ratings average."""
        return self.ratings.average()

    def get_ratings_count(self):
        """Calculates the number of ratings for the movie."""
        return self.ratings.count()

    def update_ratings(
        self, average: Decimal | None = None, count: int | None = None, save=True
    ):
        """Updates the ratings related fields."""
        self.ratings_average = average or self.get_ratings_average()
        self.ratings_count = count or self.get_ratings_count()
        self.score = self.ratings_average * self.ratings_count
        self.rating_last_updated = timezone.now()
        if save:
            self.save()

    def __str__(self):
        """Returns the title of the movie."""
        return self.title + f" ({self.released.year})" if self.released else ""
