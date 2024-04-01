from django.contrib import admin

from suggestions.models import Suggestion


@admin.register(Suggestion)
class SuggestionAdmin(admin.ModelAdmin):
    list_display = ("content_object", "user", "value", "created", "did_rate", "active")
    list_filter = ("created",)
    search_fields = ("user__username", "object_id")
    ordering = ("created", "user__username", "value")
    date_hierarchy = "created"
    readonly_fields = ("created",)
