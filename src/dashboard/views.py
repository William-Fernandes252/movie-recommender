from django.shortcuts import render
from movies.models import Movie


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
