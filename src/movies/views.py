from collections.abc import Sequence
from typing import Any

from django.db.models import F
from django.db.models.query import QuerySet
from django.views import generic
from ratings.mixins import UserRatingsContextMixin

from . import models

SORTING_CHOICES = {
    "popular": F("ratings_average").desc(nulls_last=True),
    "unpopular": "ratings_average",
    "recent": F("released").desc(nulls_last=True),
    "old": "released",
}


class MovieListView(UserRatingsContextMixin, generic.ListView):
    paginate_by = 100
    model = models.Movie

    def get_ordering(self) -> Sequence[str]:
        default_ordering = SORTING_CHOICES[
            self.request.session.get("default_ordering", "popular")
        ]
        if key := self.request.GET.get("sort"):
            self.request.session["movie_sort_order"] = key
            return [SORTING_CHOICES[key]]
        return [default_ordering]

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
    def get_object(self, queryset: QuerySet[Any] | None = None) -> models.Movie:
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
