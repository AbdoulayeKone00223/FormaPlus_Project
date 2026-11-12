from django.contrib import admin

from .models import Attestation


@admin.register(Attestation)
class AttestationAdmin(admin.ModelAdmin):
    list_display = ("reference", "inscription", "date_emission")
    search_fields = ("reference", "inscription__apprenant__nom")
    date_hierarchy = "date_emission"
    readonly_fields = ("reference",)
