from typing import Any

from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.contenttypes.models import ContentType
from django.db.models.query import QuerySet
from django.views.generic import ListView

from movies.models import Movie
from suggestions.models import Suggestion


class IndexView(LoginRequiredMixin, ListView):
    template_name = "dashboard/index.html"
    paginate_by = 100

    def get_queryset(self) -> QuerySet[Any]:
        suggestions_queryset = Suggestion.objects.filter(
            user=self.request.user,
            rating__isnull=True,
            content_type=ContentType.objects.get_for_model(Movie),
        )

        self.request.session["total_new_suggestions"] = suggestions_queryset.count()

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
