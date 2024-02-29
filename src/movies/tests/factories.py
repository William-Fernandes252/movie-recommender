from factory.django import DjangoModelFactory
from faker import Faker

from movies import models

faker = Faker("en_US")


class MovieFactory(DjangoModelFactory):
    class Meta:
        model = models.Movie

    title = faker.sentence()
    overview = faker.text()
    released = faker.date()
