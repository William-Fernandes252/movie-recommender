from collections.abc import Sequence
from typing import Any, ClassVar

from django.db.models import F
from django.db.models.base import Model as Model
from django.db.models.query import QuerySet
from django.views import generic

from movies import querysets
from ratings.mixins import UserRatingsContextMixin

from . import models

SORTING_CHOICES = {
    "popular": F("score").desc(nulls_last=True),
    "unpopular": "score",
    "top rated": F("ratings_average").desc(nulls_last=True),
    "low rated": "ratings_average",
    "recent": F("released").desc(nulls_last=True),
    "old": "released",
}


class MovieListView(UserRatingsContextMixin, generic.ListView):
    paginate_by = 100
    model = models.Movie
    default_sort_key: ClassVar[str] = "popular"

    def get_sorting_key(self) -> str:
        """Return the sorting key from the request.

        First it looks for the key in the request query params, and them, in the user session.
        If the key is not found, it defaults to the class property `default_sort_key`.

        Returns:
            str: The sorting key.
        """
        return (
            self.request.GET.get("sort")
            or self.request.session.get("movie_sort_order")
            or self.default_sort_key
        )

    def get_ordering(self) -> Sequence[str]:
        if (key := self.get_sorting_key()) in SORTING_CHOICES:
            self.request.session["movie_sort_order"] = key
        return [SORTING_CHOICES.get(key, self.default_sort_key)]

    def get_template_names(self) -> list[str]:
        if self.request.htmx:
            return ["movies/partials/movie_rows.html"]
        return super().get_template_names()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["sorting_choices"] = list(SORTING_CHOICES.keys())
        return context


class MovieDetailView(UserRatingsContextMixin, generic.DetailView):
    model = models.Movie


class MovieInfiniteRatingView(MovieDetailView):
    def exclude_already_rated(
        self, queryset: querysets.MovieQuerySet
    ) -> querysets.MovieQuerySet:
        user = self.request.user
        exclude_ids = []
        if user.is_authenticated:
            exclude_ids = user.ratings.filter(active=True).values_list(
                "object_id", flat=True
            )
        return queryset.exclude(pk__in=exclude_ids)

    def get_queryset(
        self, queryset: querysets.MovieQuerySet | None = None
    ) -> querysets.MovieQuerySet:
        return self.exclude_already_rated(queryset or models.Movie.objects.all())

    def get_object(self, queryset: QuerySet[Any] | None = ...) -> models.Movie:
        return self.get_queryset().order_by("?").first()

    def get_template_names(self) -> list[str]:
        if self.request.htmx:
            return ["movies/partials/movie_infinite_slide.html"]
        return ["movies/movie_infinite.html"]


class MoviePopularRatingView(MovieInfiniteRatingView):
    def get_context_data(self, **kwargs) -> dict[str, Any]:
        context = super().get_context_data(**kwargs)
        context["endless_path"] = "/movies/popular"
        return context

    def get_object(self, *args, **kwargs) -> querysets.MovieQuerySet:
        movie_options_ids = self.exclude_already_rated(
            models.Movie.objects.popular()
        ).values_list("id", flat=True)[:250]
        return (
            super()
            .get_queryset()
            .filter(id__in=movie_options_ids)
            .order_by("?")
            .first()
        )
