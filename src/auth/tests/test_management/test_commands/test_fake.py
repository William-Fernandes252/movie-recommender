import pytest
from django.core.management import call_command

from auth.models import User


@pytest.mark.django_db
class TestCommand:
    def test_it_should_create_total_users(self):
        """It should create the total number of users."""
        total = 5
        call_command("fake", total, "--show-total")
        assert User.objects.count() == total
