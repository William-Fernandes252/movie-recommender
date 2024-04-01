import csv
import tempfile

from django.contrib.contenttypes.models import ContentType
from django.core.files import File
from django.core.files.storage import Storage, default_storage
from django.db.models import F, QuerySet
from ratings.models import Rating

from exports.models import Export


def generate_ratings_dataset(app_label: str, model: str) -> QuerySet:
    """Generates a dataset with the ratings average and count.

    Args:
        app_label (str): The app label from wich the model belongs.
        model (str): The model name.

    Returns:
        Queryset: The ratings dataset (as a values queryset) for the given model.
    """
    ctype = ContentType.objects.get(app_label=app_label, model=model)
    return (
        Rating.objects.filter(
            content_type=ctype,
            object_id=F("object_id"),
            active=True,
        )
        .annotate(
            **{"userId": F("user_id"), "movieId": F("object_id"), "rating": F("value")}
        )
        .values("userId", "movieId", "rating")
    )


def export_dataset(
    app_label: str, model: str, filename: str | None = None
) -> Export | None:
    """Exports a dataset to a CSV file.

    Args:
        app_label (str): The app label from wich the model belongs.
        model (str): The model name.
        filename (str | None, optional): A name for the destination file. Defaults to `f"{model}_ratings"`.

    Returns:
        Export | None: _description_
    """
    with tempfile.NamedTemporaryFile(mode="r+") as tmp:
        dataset = generate_ratings_dataset(app_label, model)
        try:
            keys = dataset.first().keys()
        except AttributeError:
            return None
        writer = csv.DictWriter(tmp, fieldnames=keys)
        writer.writeheader()
        writer.writerows(dataset)
        tmp.seek(0)
        export = Export.objects.create()
        export.file.save(
            (f"{model}_ratings" if not filename else filename) + ".csv", File(tmp)
        )
        return export


def save(path: str, file: File, overwrite=False, storage: Storage = default_storage):
    """Export a file directly to a project storage.

    Args:
        path (str): The destination path.
        file (File): The file to be saved.
        overwrite (bool, optional): If the destination should be overwritten. Defaults to False.
        storage (Storage, optional): The storage instance to be used.
        Defaults to `default_storage`.
    """
    if overwrite is True and storage.exists(path):
        storage.delete(path)
    storage.save(path, file)
