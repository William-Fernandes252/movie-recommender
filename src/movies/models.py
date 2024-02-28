import uuid

from django.db import models
from django_extensions.db.models import TimeStampedModel


class Movie(TimeStampedModel, models.Model):
    id = models.UUIDField(primary_key=True, editable=False, default=uuid.uuid4)
    title = models.CharField(max_length=255, unique=True)
    overview = models.TextField()
    released = models.DateField(blank=True, null=True)

    def __str__(self):
        """Return the title of the movie."""
        return self.title
