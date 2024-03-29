import pathlib
import uuid

from django.db import models
from django.utils import timezone
from django_extensions.db.models import TimeStampedModel


def export_file_handler(instance, filename):
    ext = pathlib.Path(filename).suffix
    if hasattr(instance, "id"):
        new_filename = f"{instance.id}{ext}"
    else:
        new_filename = f"{uuid.uuid4()}{ext}"
    return pathlib.Path("exports") / timezone.now().strftime("%Y-%m-%d") / new_filename


class Export(TimeStampedModel, models.Model):
    id = models.UUIDField(primary_key=True, editable=False, default=uuid.uuid4)
    file = models.FileField(blank=True, null=True, upload_to=export_file_handler)

    class Meta:
        ordering = ["-created"]

    @property
    def filename(self):
        return pathlib.Path(self.file.name).name

    def delete(self, *args, **kwargs):
        if self.file and self.file.storage.exists(self.file.name):
            self.file.delete(save=False)
        super().delete(*args, **kwargs)
