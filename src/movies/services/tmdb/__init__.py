from datetime import date, datetime

from movies.models import Movie
from movies.services.tmdb import schemas
from movies.services.tmdb.clients import TmdbClient


class TmdbService:
    _client: TmdbClient

    def __init__(self, client: TmdbClient):
        """Initialize the TmdbService with the TmdbClient."""
        self._client = client

    def get_movies(self, params: dict) -> list[schemas.Movie]:
        """Get movies from the TMDb API.

        Args:
            params (dict): Parameters to filter the movies.

        Returns:
            list[schemas.Movie]: The list of movies returned by the API.
        """
        return [
            self.movie_from_response(item)
            for item in self._client.get_movies(params)["results"]
        ]

    def fetch_latest_movies(self, base_date: date, max: int = 200) -> list[Movie]:
        """Fetch the latest movies from the base date.

        Args:
            base_date (date): Initial date to fetch the movies.
            max (int, optional): The max amount of movies to load. Defaults to 200.

        Returns:
            list[Movie]: The list of movies fetched.
        """
        movies: list[Movie] = []
        current_page = 1
        while len(movies) < max:
            response = self._client.get_movies(
                {
                    "page": current_page,
                    "release_date.gte": base_date.strftime("%Y-%m-%d"),
                }
            )
            print(response)
            if not response["results"]:
                break
            movies.extend(
                [self.movie_from_response(data) for data in response["results"]]
            )
            current_page += 1
        if len(movies) > max:
            movies = movies[:max]
        return movies

    @staticmethod
    def movie_from_response(data: schemas.Movie) -> Movie:
        """Create a Movie from the response data.

        Args:
            data (schemas.Movie): A movie response data.

        Returns:
            Movie: The corresponding `Movie` instance.
        """
        return Movie(
            title=data["title"],
            overview=data["overview"],
            released=(datetime.strptime(data["release_date"], "%Y-%m-%d").date()),
        )
