from typing import TYPE_CHECKING

from django.contrib.auth.models import UserManager as DjangoUserManager
from django.db.models import Q
from django.utils import timezone

if TYPE_CHECKING:
    from users.models import User  # noqa: F401


class UserManager(DjangoUserManager["User"]):
    """Custom manager for the User model."""

    def recent(self, days: int = 7, ids_only: bool = False):
        base_date = timezone.now() - timezone.timedelta(days=days)
        queryset = self.filter(
            Q(date_joined__gte=base_date) | Q(last_login__gte=base_date)
        ).values_list("id", flat=True)
        if ids_only:
            queryset = queryset.values_list("id", flat=True)
        return queryset
