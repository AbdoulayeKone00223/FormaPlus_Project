"""Logique métier des attestations."""
from decimal import Decimal
from uuid import uuid4

from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import transaction

from attendance.models import Presence
from enrollments.models import Inscription

from .models import Attestation
from .rules import evaluer_conditions


def taux_presence(inscription):
    """Pourcentage de séances (1 par jour de la session) où l'apprenant était présent."""
    session = inscription.session
    nb = session.nb_seances
    if nb <= 0:
        return Decimal("0")
    presents = inscription.presences.filter(
        statut=Presence.PRESENT, date__range=(session.date_debut, session.date_fin)
    ).count()
    return min(Decimal(presents) * 100 / nb, Decimal("100"))


def evaluer(inscription):
    """Calcule la situation d'une inscription vis-à-vis des conditions de réussite."""
    evaluation = getattr(inscription, "evaluation", None)
    note = evaluation.note if evaluation else None
    valide = evaluation.valide_par_formateur if evaluation else False
    taux = taux_presence(inscription)
    reste = inscription.reste_a_payer
    eligible, raisons = evaluer_conditions(
        taux=taux,
        note=note,
        valide=valide,
        reste=reste,
        annulee=inscription.statut == Inscription.ANNULEE,
        presence_min=settings.ATTESTATION_PRESENCE_MIN,
        note_min=settings.ATTESTATION_NOTE_MIN,
        paiement_obligatoire=settings.ATTESTATION_PAIEMENT_OBLIGATOIRE,
    )
    return {
        "taux": taux,
        "note": note,
        "valide": valide,
        "reste": reste,
        "eligible": eligible,
        "raisons": raisons,
    }


@transaction.atomic
def generer_attestation(inscription):
    """Crée l'attestation si les conditions sont remplies. Retourne (attestation, creee)."""
    existante = Attestation.objects.filter(inscription=inscription).first()
    if existante:
        return existante, False
    resultat = evaluer(inscription)
    if not resultat["eligible"]:
        raise ValidationError(resultat["raisons"])
    attestation = Attestation.objects.create(
        inscription=inscription, reference=f"TMP-{uuid4().hex[:12]}"
    )
    attestation.reference = f"ATT-{attestation.date_emission.year}-{attestation.pk:04d}"
    attestation.save(update_fields=["reference"])
    return attestation, True
