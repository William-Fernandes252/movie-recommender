from typing import Any, Self

import requests
from django.conf import Settings

from movies.services.tmdb.errors import BadRequestError
from movies.services.tmdb.schemas import Movie, PaginatedResponse


class TmdbClient:
    def __init__(self, api_key: str, base_url: str):
        """Initialize the `TmdbClient` with the API key and base URL.

        Args:
            api_key (str): The API key to authenticate with the TMDb API.
            base_url (str): The base URL of the TMDb API.
        """
        self._api_key = api_key
        self._base_url = base_url

    def get_movies(self, query: dict[str, Any]) -> PaginatedResponse[Movie]:
        """Get movies from the TMDb API.

        Args:
            query (dict[str, Any]): The query parameters to filter the movies.

        Returns:
            PaginatedResponse[Movie]: The corresponding page of movies returned by the API.
        """
        response = requests.get(f"{self._base_url}/discover/movie", params=query)
        self.validate_response(response)
        return response.json()

    @classmethod
    def from_settings(cls, settings: Settings) -> Self:
        """Creates a `TmdbClient` from the Django settings.

        Args:
            settings (Settings): A Django settings object.

        Returns:
            Self: A `TmdbClient` instance.
        """
        return cls(settings.TMDB_API_KEY, settings.TMDB_BASE_URL)

    @classmethod
    def validate_response(cls, response: requests.Response) -> None:
        """Validates the response from the TMDb API, raising an error
        depending on its status code.

        Args:
            response (requests.Response): A response from the TMDb API.

        Raises:
            BadRequestError: If the response status code is 400.
        """
        if response.status_code == 400:
            raise BadRequestError(response.json()["status_message"])
