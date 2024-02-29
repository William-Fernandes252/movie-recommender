import pytest
from movies.models import Movie


class TestMovie:
    @pytest.mark.django_db
    def test_movie_creation(self):
        movie = Movie(title="The Godfather", released=1972)
        assert movie.title == "The Godfather"
        assert movie.released == 1972

    def test_movie_str(self, movie: Movie):
        assert str(movie) == movie.title
