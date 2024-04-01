import pickle
import tempfile
from typing import Any, Iterable, Sequence

from django.conf import settings
from django.contrib.contenttypes.models import ContentType
from django.core.files import File
from django.db.models import F
from exports.utils import save
from ratings.models import Rating
from surprise import SVD, Dataset, Reader, Trainset, accuracy, dataset
from surprise.model_selection import cross_validate

from movies.models import Movie


def export_movie_ratings_dataset() -> Iterable[dict[str, Any]]:
    """Exports a dataset with the movies ratings average and count."""
    return (
        Rating.objects.filter(
            active=True, content_type=ContentType.objects.get_for_model(Movie)
        )
        .annotate(
            **{"userId": F("user_id"), "movieId": F("object_id"), "rating": F("value")}
        )
        .values("userId", "movieId", "rating")
    )


def get_model_accuracy(trainset: Trainset, model: SVD, use_rmse=True) -> float:
    testset = trainset.build_testset()
    predictions = model.test(testset)
    if use_rmse:
        return accuracy.rmse(predictions)
    return accuracy.mae(predictions)


def get_data_loader(
    dataset: list[dict[str, Any]],
    columns: Sequence[str] = ["userId", "movieId", "rating"],
) -> dataset.DatasetAutoFolds:
    """Loads a dataset into a Surprise DatasetAutoFolds object.

    Args:
        dataset (list[dict[str, Any]]): The dataset to be loaded.
        columns (Sequence[str], optional): The columns to be used as the rating data.
        Defaults to ["userId", "movieId", "rating"].

    Returns:
        dataset.DatasetAutoFolds: The loaded dataset.
    """
    import pandas as pd

    df = pd.DataFrame(dataset)
    df["rating"].dropna(inplace=True)

    max_rating, min_rating = df["rating"].max(), df["rating"].min()

    reader = Reader(rating_scale=(min_rating, max_rating))

    return Dataset.load_from_df(df[columns], reader)


def get_model_name_from_accuracy(accuracy: float) -> str:
    """Generates a model name based on its accuracy."""
    return f"model-{int(100 * accuracy)}"


def train_surprise_model(epochs: int = 20) -> tuple[SVD, float, dict[str, Any]]:
    """Trains a model using the Surprise library.

    Args:
        epochs (int, optional): The number of epochs to run. Defaults to 20.

    Returns:
        tuple[SVD, float, dict[str, Any]]: A tuple containing the trained model,
        its accuracy and the validation results.
    """
    dataset = export_movie_ratings_dataset()
    loaded_data = get_data_loader([*dataset])
    model = SVD(verbose=True, n_epochs=epochs)
    validation_results = cross_validate(
        model, loaded_data, measures=["RMSE", "MAE"], cv=4, verbose=True
    )
    trainset = loaded_data.build_full_trainset()
    model.fit(trainset)
    return model, get_model_accuracy(trainset, model), validation_results


def _get_lastest_model_path(type="surprise", ext="pkl") -> str:
    """Returns the path to the latest model file."""
    return f"ml/models/{type}/latest.{ext}"


def export_model(
    model: Any, name: str, type="surprise", ext="pkl", verbose=False
) -> None:
    """Exports a model to a file using pickle."""
    with tempfile.NamedTemporaryFile("rb+") as temp:
        pickle.dump(model, temp)
        path = f"ml/models/{type}/{name}.{ext}"
        if verbose:
            print(f"Saving model to {path} and {type}/latest.{ext}")
        save(path, File(temp))
        save(_get_lastest_model_path(type, ext), File(temp))


def load_model(type="surprise", ext="pkl"):
    """Loads the latest model from a file using pickle."""
    path = settings.MEDIA_ROOT / _get_lastest_model_path(type, ext)
    if not path.exists():
        return None

    model = None
    with open(path, "rb") as file:
        model = pickle.load(file)

    return model
