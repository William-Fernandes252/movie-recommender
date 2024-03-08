from django.contrib import admin
from django.utils.translation import gettext_lazy as _

from . import models


@admin.register(models.Movie)
class MovieAdmin(admin.ModelAdmin):
    list_display = ("id", "title", "released", "rating_average")
    search_fields = ("@title", "@overview", "id")
    list_filter = ("released",)
    date_hierarchy = "released"
    readonly_fields = (
        "created",
        "modified",
        "id",
        "rating_average",
        "rating_count",
    )
    search_help_text = _("Search for movies by title, overview, or ID.")
