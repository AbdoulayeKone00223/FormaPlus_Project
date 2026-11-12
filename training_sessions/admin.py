from django.contrib import admin

from enrollments.models import Inscription

from .models import Session


class InscriptionInline(admin.TabularInline):
    model = Inscription
    extra = 0


@admin.register(Session)
class SessionAdmin(admin.ModelAdmin):
    list_display = ("formation", "formateur", "date_debut", "date_fin", "lieu", "capacite", "places_prises")
    list_filter = ("formation", "formateur", "date_debut")
    search_fields = ("formation__titre", "lieu", "formateur__nom")
    date_hierarchy = "date_debut"
    inlines = [InscriptionInline]

    @admin.display(description="Inscrits")
    def places_prises(self, obj):
        return obj.places_prises
