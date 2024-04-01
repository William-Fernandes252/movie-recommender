from django.contrib.auth.models import AbstractUser

from users.managers import UserManager


class User(AbstractUser):
    objects = UserManager()
