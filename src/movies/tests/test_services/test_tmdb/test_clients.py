import pytest
import responses
from responses import matchers

from movies.services.tmdb import errors
from movies.services.tmdb.clients import TmdbClient

BASE_URL = "https://example.com"
API_KEY = "123"


class TestTmdbClient:
    @pytest.fixture
    def client(self):
        return TmdbClient(API_KEY, BASE_URL)

    class TestGetMovies:
        @responses.activate
        def test_it_should_return_the_movies_on_success(self, client: TmdbClient):
            """It should return the movies."""
            url = f"{BASE_URL}/discover/movie"
            params = {"page": 1}
            expected = {
                "results": [
                    {
                        "id": 1,
                        "title": "Movie",
                        "overview": "Overview",
                        "release_date": "2021-01-01",
                    }
                ]
            }

            responses.get(
                url, json=expected, match=[matchers.query_param_matcher(params)]
            )

            response = client.get_movies(params)
            assert response == expected

        @responses.activate
        def test_it_should_raise_bad_request_error_on_failure(self, client: TmdbClient):
            """It should raise BadRequestError."""
            url = f"{BASE_URL}/discover/movie"
            params = {"page": 1}
            expected = {"status_code": 400, "status_message": "Bad request"}

            responses.get(
                url,
                status=400,
                json=expected,
                match=[matchers.query_param_matcher(params)],
            )

            with pytest.raises(errors.BadRequestError) as excinfo:
                client.get_movies(params)

            assert str(excinfo.value) == expected["status_message"]
