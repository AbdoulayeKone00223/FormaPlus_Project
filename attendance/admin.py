from django.contrib import admin

from .models import Evaluation, Presence


@admin.register(Presence)
class PresenceAdmin(admin.ModelAdmin):
    list_display = ("inscription", "date", "statut")
    list_filter = ("statut", "date")


@admin.register(Evaluation)
class EvaluationAdmin(admin.ModelAdmin):
    list_display = ("inscription", "note", "valide_par_formateur")
    list_filter = ("valide_par_formateur",)
