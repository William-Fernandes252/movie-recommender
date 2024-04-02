from django.contrib.auth.decorators import login_required
from django.http import HttpRequest, HttpResponse, HttpResponseNotAllowed
from django.shortcuts import get_object_or_404, render
from django.views.decorators.http import require_POST

from movies.models import Movie
from movies.tasks import batch_user_prediction
from ratings import models


@login_required
@require_POST
def rate_movie(request: HttpRequest):
    """Rate a movie."""
    if not request.htmx:
        return HttpResponseNotAllowed()

    object_id = request.POST.get("object_id")
    rating_value = request.POST.get("value")
    if not object_id or not rating_value:
        response = HttpResponse("Skipping", status=200)
        response["HX-Trigger"] = "did-skip-movie"
        return response

    movie = get_object_or_404(Movie, pk=request.POST.get("object_id"))
    rating = request.POST.get("value")
    if rating:
        items_rated = request.session.get("items_rated", 0)
        items_rated += 1
        request.session["items_rated"] = items_rated

        start = request.session.get("total_new_suggestions", 0)
        if items_rated % 5 == 0:
            batch_user_prediction.delay(
                users_ids=[request.user.id],
                start=start,
                offset=25,
                max=25,
                use_suggestions_up_to_days=None,
            )

        models.Rating.objects.create(
            content_object=movie,
            user=request.user,
            value=rating,
        )
    response = render(
        request, "ratings/partials/rating_created.html", {"movie": movie}, status=201
    )
    response["HX-Trigger-After-Settle"] = "did-rate-movie"
    return response
