from django.contrib import admin
from django.http import HttpRequest

from ratings.querysets import RatingQuerySet

from .models import Rating


@admin.register(Rating)
class RatingAdmin(admin.ModelAdmin):
    list_display = ("content_object", "user", "value", "created", "active")
    list_filter = ("active", "created")
    search_fields = ("user__username", "object_id")
    ordering = ("created", "active", "user__username", "value")
    date_hierarchy = "created"
    actions = ["activate", "deactivate"]
    readonly_fields = ("created", "active")

    @admin.action(description="Activate selected ratings")
    def activate(self, request: HttpRequest, queryset: RatingQuerySet):
        queryset.activate()

    @admin.action(description="Deactivate selected ratings")
    def deactivate(self, request: HttpRequest, queryset: RatingQuerySet):
        queryset.deactivate()
