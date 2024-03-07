from factory import SubFactory
from factory.django import DjangoModelFactory
from faker import Faker

from movies import models
from ratings.tests.factories import RatingFactory

faker = Faker("en_US")


class MovieFactory(DjangoModelFactory):
    class Meta:
        model = models.Movie

    title = faker.sentence()
    overview = faker.text()
    released = faker.date()


class MovieRatingFactory(RatingFactory):
    content_object = SubFactory(MovieFactory)

    class Meta:
        model = models.Rating
