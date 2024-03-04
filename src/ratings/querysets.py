from django.db.models import QuerySet


class RatingQuerySet(QuerySet):
    def active(self):
        """Return only active ratings."""
        return self.filter(active=True)

    def inactive(self):
        """Return only inactive ratings."""
        return self.filter(active=False)

    def activate(self):
        """Activates the selected ratings."""
        return self.update(active=True)

    def deactivate(self):
        """Deactivates the selected ratings."""
        return self.update(active=False)
