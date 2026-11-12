from django.contrib import messages
from django.core.exceptions import PermissionDenied, ValidationError
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST

from accounts.permissions import (
    ADMIN,
    APPRENANT,
    FORMATEUR,
    get_role,
    peut_gerer_session,
    role_required,
)
from enrollments.models import Inscription
from training_sessions.models import Session

from .models import Attestation
from .pdf import pdf_attestation
from .services import evaluer, generer_attestation


def _lignes(session):
    inscriptions = (
        session.inscriptions.exclude(statut=Inscription.ANNULEE)
        .select_related("apprenant", "session__formation")
        .order_by("apprenant__nom")
    )
    lignes = []
    for inscription in inscriptions:
        ligne = evaluer(inscription)
        ligne["inscription"] = inscription
        ligne["attestation"] = getattr(inscription, "attestation", None)
        lignes.append(ligne)
    return lignes


@role_required(ADMIN, FORMATEUR)
def session_attestations(request, session_id):
    session = get_object_or_404(
        Session.objects.select_related("formation", "formateur"), pk=session_id
    )
    if not peut_gerer_session(request.user, session):
        raise PermissionDenied

    if request.method == "POST":
        cible = request.POST.get("inscription_id")
        crees, refus = 0, []
        for ligne in _lignes(session):
            inscription = ligne["inscription"]
            if cible and str(inscription.pk) != cible:
                continue
            if ligne["attestation"]:
                continue
            if not cible and not ligne["eligible"]:
                continue
            try:
                _, creee = generer_attestation(inscription)
                crees += int(creee)
            except ValidationError as erreur:
                refus.append(f"{inscription.apprenant} : {' '.join(erreur.messages)}")
        if crees:
            messages.success(request, f"{crees} attestation(s) générée(s).")
        elif not refus:
            messages.info(request, "Aucune nouvelle attestation à générer.")
        for message in refus:
            messages.error(request, message)
        return redirect("session_attestations", session_id=session.pk)

    return render(
        request,
        "certificates/session_attestations.html",
        {"session": session, "lignes": _lignes(session)},
    )


def _peut_voir(user, attestation):
    role = get_role(user)
    inscription = attestation.inscription
    if role == ADMIN:
        return True
    if role == FORMATEUR:
        return peut_gerer_session(user, inscription.session)
    if role == APPRENANT:
        return inscription.apprenant.user_id is not None and inscription.apprenant.user_id == user.pk
    return False


@role_required(ADMIN, FORMATEUR, APPRENANT)
def download_attestation(request, pk):
    attestation = get_object_or_404(
        Attestation.objects.select_related(
            "inscription__apprenant",
            "inscription__session__formation__centre",
            "inscription__session__formateur",
        ),
        pk=pk,
    )
    if not _peut_voir(request.user, attestation):
        raise PermissionDenied
    reponse = HttpResponse(pdf_attestation(attestation), content_type="application/pdf")
    reponse["Content-Disposition"] = f'attachment; filename="{attestation.reference}.pdf"'
    return reponse
