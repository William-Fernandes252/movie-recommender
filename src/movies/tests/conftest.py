import pytest
from movies.tests.factories import MovieFactory


@pytest.fixture
def movie(db):
    return MovieFactory()
