from factory import Sequence, post_generation
from factory.django import DjangoModelFactory, DjangoOptions
from faker import Faker

from users.models import User

faker = Faker("en_US")


class UserFactory(DjangoModelFactory):
    class Meta(DjangoOptions):
        model = User

    username = Sequence(lambda n: f"{faker.user_name()}{n}")
    email = faker.email()
    first_name = faker.first_name()
    last_name = faker.last_name()

    @post_generation
    def password(self: User, create: bool, extracted: str, **kwargs):  # noqa: FBT001
        if create:
            password = extracted if extracted else faker.password(20)
            self.set_password(password)

    @classmethod
    def _after_postgeneration(cls, instance, create, results=None):
        """Save again the instance if creating and at least one hook ran."""
        if create and results and not cls._meta.skip_postgeneration_save:
            instance.save()
