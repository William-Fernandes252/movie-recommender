from collections.abc import Sequence
from typing import Any

from django.db.models.base import Model as Model
from django.db.models.query import QuerySet
from django.views import generic

from ratings.mixins import UserRatingsContextMixin

from . import models

SORTING_CHOICES = {
    "popular": "-ratings_average",
    "unpopular": "ratings_average",
    "recent": "-released",
    "old": "released",
}


class MovieListView(UserRatingsContextMixin, generic.ListView):
    paginate_by = 100
    model = models.Movie

    def get_ordering(self) -> Sequence[str]:
        default_ordering = self.request.session.get(
            "default_ordering", "-ratings_average"
        )
        if sort := self.request.GET.get("sort"):
            self.request.session["movie_sort_order"] = sort
            return [sort]
        return [default_ordering]

    def get_template_names(self) -> list[str]:
        if self.request.htmx:
            return ["movies/partials/movie_rows.html"]
        return super().get_template_names()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["sorting_choices"] = SORTING_CHOICES
        return context


class MovieDetailView(UserRatingsContextMixin, generic.DetailView):
    model = models.Movie


class MovieInfiniteRatingView(MovieDetailView):
    def get_object(self, queryset: QuerySet[Any] | None = None) -> Model:
        user = self.request.user
        exclude_ids = []
        if user.is_authenticated:
            exclude_ids = user.ratings.filter(active=True).values_list(
                "object_id", flat=True
            )
        return (
            (queryset or models.Movie.objects.all())
            .exclude(pk__in=exclude_ids)
            .order_by("?")
            .first()
        )

    def get_template_names(self) -> list[str]:
        if self.request.htmx:
            return ["movies/partials/movie_infinite_slide.html"]
        return ["movies/movie_infinite.html"]
