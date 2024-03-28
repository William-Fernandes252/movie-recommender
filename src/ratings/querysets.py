from django.db import models


class RatingQuerySet(models.QuerySet):
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

    def average(self):
        return self.aggregate(average=models.Avg("value"))["average"]

    def as_object_id_to_value_dict(self, object_ids: list[str]) -> dict[str, int]:
        """Converts itself to a object_id to value dicionarie."""
        return {
            f"{rating.object_id}": rating.value
            for rating in self.filter(object_id__in=object_ids)
        }
