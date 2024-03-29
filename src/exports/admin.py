from django.contrib import admin

from exports import models


@admin.register(models.Export)
class ExportAdmin(admin.ModelAdmin):
    list_display = ["filename", "created"]
    list_filter = ["created"]
    search_fields = ["id"]
