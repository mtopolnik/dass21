from django.contrib import admin

from .models import Response


@admin.register(Response)
class ResponseAdmin(admin.ModelAdmin):
    list_display = ("person", "date", "updated_at")
    list_filter = ("person", "date")
    ordering = ("-date", "person")
