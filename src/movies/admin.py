from django.contrib import admin

from . import models


class MovieAdmin(admin.ModelAdmin):
    list_display = ("title", "released")
    search_fields = ("title", "overview")
    list_filter = ("released",)
    date_hierarchy = "released"


admin.site.register(models.Movie, MovieAdmin)
