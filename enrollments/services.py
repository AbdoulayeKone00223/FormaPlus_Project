from django.core.exceptions import ValidationError
from django.db import transaction
from django.utils import timezone

from training_sessions.models import Session

from .models import Inscription


@transaction.atomic
def inscrire(apprenant, session):
    """Inscrit un apprenant à une session (capacité, doublon et date contrôlés)."""
    session = Session.objects.select_for_update().get(pk=session.pk)
    existante = Inscription.objects.filter(apprenant=apprenant, session=session).first()
    if existante and existante.statut != Inscription.ANNULEE:
        raise ValidationError("Vous êtes déjà inscrit à cette session.")
    if session.date_fin < timezone.localdate():
        raise ValidationError("Cette session est terminée.")
    if session.est_complete:
        raise ValidationError("Cette session est complète.")
    if existante:
        existante.statut = Inscription.CONFIRMEE
        existante.save(update_fields=["statut"])
        return existante
    return Inscription.objects.create(apprenant=apprenant, session=session)
