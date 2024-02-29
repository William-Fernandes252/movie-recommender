from datetime import date, datetime
from unittest.mock import MagicMock

import pytest
from pytest_mock import MockFixture

from movies.models import Movie
from movies.services.tmdb import TmdbService, clients, schemas


class TestTmdbService:
    @pytest.fixture
    def mocked_client(self, mocker: MockFixture) -> MagicMock:
        return mocker.MagicMock(clients.TmdbClient)

    @pytest.fixture
    def movie_items(self) -> list[schemas.Movie]:
        return [
            {
                "adult": False,
                "backdrop_path": "/some/path.jpg",
                "genre_ids": [12, 14, 10751],
                "id": 123,
                "original_language": "en",
                "original_title": "The Shawshank Redemption",
                "overview": "Two imprisoned men bond over a number of years...",
                "popularity": 8.5,
                "poster_path": "/another/path.jpg",
                "release_date": "1994-09-23",
                "title": "The Shawshank Redemption",
                "video": False,
                "vote_average": 8.7,
                "vote_count": 10000,
            },
            {
                "adult": False,
                "backdrop_path": "/some/path2.jpg",
                "genre_ids": [18, 80],
                "id": 456,
                "original_language": "en",
                "original_title": "The Godfather",
                "overview": "The aging patriarch of an organized crime dynasty...",
                "popularity": 8.3,
                "poster_path": "/another/path2.jpg",
                "release_date": "1972-03-14",
                "title": "The Godfather",
                "video": False,
                "vote_average": 8.9,
                "vote_count": 12000,
            },
        ]

    class TestFetchLatestMovies:
        class TestWithSuccessfulResponse:
            def assert_movie_matches_resource(
                self, movie: Movie, expected: schemas.Movie
            ):
                """Assert that the movie object matches the resource returned by the TMDb API.

                Args:
                    movie (Movie): movie object to validate.
                    expected (schemas.Movie): movie resource from the API.
                """
                assert movie.title == expected["title"]
                assert movie.overview == expected["overview"]
                assert (
                    movie.released
                    == datetime.strptime(expected["release_date"], "%Y-%m-%d").date()
                )

            @pytest.fixture
            def mocked_client_with_movies(self, mocked_client: MagicMock, movie_items):
                mocked_client.get_movies.return_value = {"results": movie_items}
                return mocked_client

            def test_it_should_return_the_latest_movies(
                self, mocked_client_with_movies: MagicMock, movie_items
            ):
                service = TmdbService(mocked_client_with_movies)
                base_date = date(2021, 1, 1)

                result = service.fetch_latest_movies(base_date, max=2)

                for movie, expected in zip(result, movie_items):
                    self.assert_movie_matches_resource(movie, expected)

            def test_it_should_return_the_latest_movies_with_max_limit(
                self, mocked_client_with_movies: MagicMock, movie_items
            ):
                service = TmdbService(mocked_client_with_movies)
                base_date = date(2021, 1, 1)

                result = service.fetch_latest_movies(base_date, max=1)

                for movie, expected in zip(result, movie_items[:1]):
                    self.assert_movie_matches_resource(movie, expected)

            def test_it_should_return_the_latest_movies_with_multiple_pages(
                self, mocked_client_with_movies: MagicMock, movie_items
            ):
                service = TmdbService(mocked_client_with_movies)
                mocked_client_with_movies.get_movies.side_effect = [
                    {"results": movie_items[:1]},
                    {"results": movie_items[1:]},
                ]
                base_date = date(2021, 1, 1)

                result = service.fetch_latest_movies(base_date, max=2)

                for movie, expected in zip(result, movie_items):
                    self.assert_movie_matches_resource(movie, expected)

            def test_it_should_return_the_latest_movies_with_multiple_pages_and_max_limit(
                self, mocked_client_with_movies: MagicMock, movie_items
            ):
                service = TmdbService(mocked_client_with_movies)
                mocked_client_with_movies.get_movies.side_effect = [
                    {"results": movie_items[:1]},
                    {"results": movie_items[1:]},
                ]
                base_date = date(2021, 1, 1)

                result = service.fetch_latest_movies(base_date, max=1)

                for movie, expected in zip(result, movie_items[:1]):
                    self.assert_movie_matches_resource(movie, expected)

            def test_it_should_call_the_client_with_the_correct_params(
                self, mocked_client_with_movies: MagicMock
            ):
                service = TmdbService(mocked_client_with_movies)
                base_date = date(2021, 1, 1)

                service.fetch_latest_movies(base_date, max=1)

                mocked_client_with_movies.get_movies.assert_called_once_with(
                    {"page": 1, "release_date.gte": "2021-01-01"}
                )
