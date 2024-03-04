from django.contrib import admin

from . import models


@admin.register(models.Movie)
class MovieAdmin(admin.ModelAdmin):
    list_display = ("id", "title", "released")
    search_fields = ("title", "overview")
    list_filter = ("released",)
    date_hierarchy = "released"
    readonly_fields = ("created", "modified", "id")
