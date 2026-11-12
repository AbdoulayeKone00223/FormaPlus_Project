from django.contrib import admin

from .models import Apprenant


@admin.register(Apprenant)
class ApprenantAdmin(admin.ModelAdmin):
    list_display = ("nom", "telephone", "user")
    search_fields = ("nom", "telephone")
