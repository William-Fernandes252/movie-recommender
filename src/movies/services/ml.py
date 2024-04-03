import pickle
import tempfile
from typing import Any

import pandas
from django.conf import settings
from django.contrib.contenttypes.models import ContentType
from django.core.files import File
from surprise import SVD, Dataset, Reader, Trainset, accuracy, dataset
from surprise.model_selection import cross_validate

from exports.models import Export
from exports.utils import save
from movies.models import Movie
from ratings.models import Rating


def import_movie_ratings_dataset() -> pandas.DataFrame:
    """Imports the movies ratings dataset and joins it with the movies dataset."""
    movies_latest_export: Export | None = Export.objects.get_latest_for_content_type(
        ContentType.objects.get_for_model(Movie)
    )
    if (movies_latest_export is None) or not movies_latest_export.file.storage.exists(
        movies_latest_export.file.name
    ):
        raise ValueError("No movie dataset found.")

    ratings_latest_export: Export | None = Export.objects.get_latest_for_content_type(
        ContentType.objects.get_for_model(Rating)
    )
    if (ratings_latest_export is None) or not ratings_latest_export.file.storage.exists(
        ratings_latest_export.file.name
    ):
        raise ValueError("No ratings dataset found.")

    movies_df = pandas.read_csv(movies_latest_export.file)
    ratings_df = pandas.read_csv(ratings_latest_export.file)

    return ratings_df.copy().join(
        movies_df, on="movieId", rsuffix="_movie_df", how="inner"
    )


def prepare_for_training(df: pandas.DataFrame) -> pandas.DataFrame:
    """Prepare the dataset for training by renaming the columns and fixing the data types.

    Args:
        df (pandas.DataFrame): The base movie ratings dataset.

    Returns:
        pandas.DataFrame: The resulting dataset.
    """
    training_df = df.copy().dropna(subset=["userId", "movieId", "rating"])

    for column, type in [
        ("userId", int),
        ("movieId", int),
        ("movieIndex", int),
        ("rating", float),
    ]:
        training_df[column] = training_df[column].astype(type)

    return training_df.rename(
        columns={"userId": "user", "movieIndex": "movie", "rating": "rating"}
    )


def get_model_accuracy(trainset: Trainset, model: SVD, use_rmse=True) -> float:
    """Return the model accuracy using the RMSE or MAE metric.

    Args:
        trainset (Trainset): The training set.
        model (SVD): The trained model.
        use_rmse (bool, optional): It should use the RMSE (True) or the MAE (False) metric.
        Defaults to True.

    Returns:
        float: The model accuracy according to the chosen metric.
    """
    testset = trainset.build_testset()
    predictions = model.test(testset)
    if use_rmse:
        return accuracy.rmse(predictions)
    return accuracy.mae(predictions)


def get_data_loader(
    dataset_as_df: pandas.DataFrame,
) -> dataset.DatasetAutoFolds:
    """Loads a dataset into a Surprise DatasetAutoFolds object.

    Args:
        dataset_as_df (pandas.DataFrame): The dataset to load. Must contain the columns:
        - user: The users IDs.
        - movie: The movies IDs.
        - rating: The ratings.

    Returns:
        dataset.DatasetAutoFolds: The loaded dataset.
    """
    reader = Reader(
        rating_scale=(dataset_as_df["rating"].max(), dataset_as_df["rating"].min())
    )
    return Dataset.load_from_df(dataset_as_df[["user", "movie", "rating"]], reader)


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
    loaded_data = get_data_loader(prepare_for_training(import_movie_ratings_dataset()))
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
