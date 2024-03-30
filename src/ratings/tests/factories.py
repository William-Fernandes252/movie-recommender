from random import choice

from django.contrib.contenttypes.models import ContentType
from factory import LazyAttribute, SelfAttribute, SubFactory
from factory.django import DjangoModelFactory

from ratings import models
from users.tests.factories import UserFactory


class RatingFactory(DjangoModelFactory):
    class Meta:
        model = models.Rating
        exclude = ["content_object"]
        abstract = True

    user = SubFactory(UserFactory)
    value = choice(
        [value for value in models.RatingChoices.values if value is not None]
    )
    object_id = SelfAttribute("content_object.id")
    content_type = LazyAttribute(
        lambda o: ContentType.objects.get_for_model(o.content_object)
    )
