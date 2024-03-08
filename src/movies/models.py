import uuid

from django.contrib.contenttypes.fields import GenericRelation
from django.db import models
from django.utils import timezone
from django_extensions.db.models import TimeStampedModel
from ratings.managers import RatingManager
from ratings.models import Rating

from movies import managers


class Movie(TimeStampedModel, models.Model):
    objects = managers.MovieManager()

    id = models.UUIDField(primary_key=True, editable=False, default=uuid.uuid4)
    title = models.CharField(max_length=255, unique=True)
    overview = models.TextField()
    released = models.DateField(blank=True, null=True)
    ratings: RatingManager = GenericRelation(Rating)
    rating_average = models.DecimalField(
        max_digits=5, decimal_places=2, blank=True, null=True
    )
    rating_count = models.PositiveIntegerField(blank=True, null=True)
    rating_last_updated = models.DateTimeField(blank=True, null=True)

    def get_ratings_average(self):
        """Calculates the ratings average."""
        return self.ratings.average()

    def get_ratings_count(self):
        """Calculates the number of ratings for the movie."""
        return self.ratings.count()

    def update_ratings_average(self, save=True):
        """Updates the rating_average, rating_count, and rating_last_updated fields."""
        self.rating_average = self.get_ratings_average()
        self.rating_count = self.get_ratings_count()
        self.rating_last_updated = timezone.now()
        if save:
            self.save()

    def __str__(self):
        """Returns the title of the movie."""
        return self.title + f" ({self.released.year})" if self.released else ""
