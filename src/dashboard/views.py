from typing import Any

from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.contenttypes.models import ContentType
from django.db.models.query import QuerySet
from django.shortcuts import render
from django.views.generic import ListView
from movies.models import Movie
from suggestions.models import Suggestion


def index_view(request):
    """Home view."""
    context = {}
    user = request.user
    if not user.is_authenticated:
        return render(request, "home.html", context)
    context["endless_path"] = "/"
    max_movies = 50
    request.session["total-new-suggestions"] = 0
    context["object_list"] = Movie.objects.all().order_by("?")[:max_movies]
    if request.htmx:
        return render(request, "movies/snippet/infinite.html", context)
    return render(request, "dashboard/index.html", context)


class IndexView(ListView, LoginRequiredMixin):
    template_name = "dashboard/index.html"

    def get_queryset(self) -> QuerySet[Any]:
        suggestions_queryset = Suggestion.objects.filter(
            user=self.request.user,
            rating__isnull=True,
            content_type=ContentType.objects.get_for_model(Movie),
        )
        if suggestions_queryset.exists():
            movies_ids = suggestions_queryset.order_by("-value").values_list(
                "object_id", flat=True
            )
            return Movie.objects.order_by_ids(movies_ids)
        else:
            return Movie.objects.popular()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["endless_path"] = "/"
        return context
