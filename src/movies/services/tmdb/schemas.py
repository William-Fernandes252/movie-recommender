from typing import Generic, TypedDict, TypeVar

T = TypeVar("T")


class Movie(TypedDict):
    adult: bool
    backdrop_path: str
    genre_ids: list[int]
    id: int
    original_language: str
    original_title: str
    overview: str
    popularity: float
    poster_path: str
    release_date: str
    title: str
    video: bool
    vote_average: float
    vote_count: int


class PaginatedResponse(Generic[T], TypedDict):
    page: int
    results: list[T]
    total_pages: int
    total_results: int
