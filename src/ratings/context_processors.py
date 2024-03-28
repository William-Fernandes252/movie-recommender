from ratings.models import RatingChoices


def rating_choices(request):
    """Render rating choices in templates."""
    return {"rating_choices": RatingChoices.values}
