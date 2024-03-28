# mypy: disable-error-code="attr-defined"

from django.contrib.contenttypes.models import ContentType
from django.views.generic.list import MultipleObjectMixin

from . import models


class UserRatingsContextMixin:
    """Add user ratings on the view objects to the context."""

    def get_object_ids(self, context: dict) -> list[str]:
        """Return the object ids from the context."""
        return [
            str(obj.pk)
            for obj in (
                context[self.get_context_object_name(self.object_list)]
                if isinstance(self, MultipleObjectMixin)
                else [context[self.get_context_object_name(self.object)]]
            )
        ]

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.request.user.is_authenticated:
            context["user_ratings"] = models.Rating.objects.filter(
                user=self.request.user,
                active=True,
                content_type=ContentType.objects.get_for_model(self.model),
            ).as_object_id_to_value_dict(self.get_object_ids(context))
        return context
