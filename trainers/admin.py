from django.contrib import admin

from .models import Formateur


@admin.register(Formateur)
class FormateurAdmin(admin.ModelAdmin):
    list_display = ("nom", "specialite", "user")
    search_fields = ("nom", "specialite")
