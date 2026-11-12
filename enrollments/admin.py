from django.contrib import admin, messages
from django.core.exceptions import ValidationError

from attendance.models import Evaluation, Presence

from .models import Inscription, Paiement


class PaiementInline(admin.TabularInline):
    model = Paiement
    extra = 0


class PresenceInline(admin.TabularInline):
    model = Presence
    extra = 0


class EvaluationInline(admin.StackedInline):
    model = Evaluation
    extra = 0


@admin.register(Inscription)
class InscriptionAdmin(admin.ModelAdmin):
    list_display = ("apprenant", "session", "statut", "date_inscription", "total_paye", "reste_a_payer")
    list_filter = ("statut", "session")
    search_fields = ("apprenant__nom", "session__formation__titre")
    inlines = [PaiementInline, PresenceInline, EvaluationInline]
    actions = ["generer_attestations"]

    @admin.action(description="Générer les attestations (inscriptions éligibles)")
    def generer_attestations(self, request, queryset):
        from certificates.services import generer_attestation

        crees = 0
        for inscription in queryset:
            try:
                _, creee = generer_attestation(inscription)
                crees += int(creee)
            except ValidationError as erreur:
                self.message_user(
                    request,
                    f"{inscription.apprenant} : {' '.join(erreur.messages)}",
                    level=messages.WARNING,
                )
        self.message_user(request, f"{crees} attestation(s) générée(s).", level=messages.SUCCESS)


@admin.register(Paiement)
class PaiementAdmin(admin.ModelAdmin):
    list_display = ("inscription", "montant", "date")
    list_filter = ("date",)
    date_hierarchy = "date"
