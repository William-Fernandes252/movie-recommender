from django.contrib import admin
from django.utils.translation import gettext_lazy as _

from . import models


@admin.register(models.Movie)
class MovieAdmin(admin.ModelAdmin):
    list_display = ("title", "index", "released", "ratings_average", "ratings_count")
    search_fields = ("@title", "@overview", "id")
    list_filter = ("released",)
    date_hierarchy = "released"
    readonly_fields = (
        "created",
        "modified",
        "id",
        "index",
        "ratings_average",
        "ratings_count",
        "rating_last_updated",
    )
    search_help_text = _("Search for movies by title, overview, or ID.")
