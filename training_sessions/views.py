from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, render
from django.utils import timezone

from accounts.permissions import (
    ADMIN,
    APPRENANT,
    FORMATEUR,
    get_apprenant,
    get_formateur,
    get_role,
    peut_gerer_session,
)
from enrollments.models import Inscription

from .models import Session


def _ids_inscrits(user):
    apprenant = get_apprenant(user)
    if not apprenant:
        return set()
    return set(
        Inscription.objects.filter(apprenant=apprenant)
        .exclude(statut=Inscription.ANNULEE)
        .values_list("session_id", flat=True)
    )


@login_required
def session_list(request):
    role = get_role(request.user)
    sessions = Session.objects.select_related("formation__centre", "formateur")
    mes_ids = set()
    if role == FORMATEUR:
        formateur = get_formateur(request.user)
        sessions = sessions.filter(formateur=formateur) if formateur else sessions.none()
    elif role == APPRENANT:
        sessions = sessions.filter(date_fin__gte=timezone.localdate())
        mes_ids = _ids_inscrits(request.user)
    elif role != ADMIN:
        sessions = sessions.none()
    return render(
        request,
        "training_sessions/session_list.html",
        {"sessions": sessions.order_by("date_debut"), "mes_ids": mes_ids},
    )


@login_required
def session_detail(request, pk):
    session = get_object_or_404(
        Session.objects.select_related("formation__centre", "formateur"), pk=pk
    )
    role = get_role(request.user)
    peut_gerer = peut_gerer_session(request.user, session)
    inscriptions = None
    if peut_gerer:
        inscriptions = session.inscriptions.exclude(statut=Inscription.ANNULEE).select_related(
            "apprenant"
        ).order_by("apprenant__nom")
    mon_inscription = None
    if role == APPRENANT:
        apprenant = get_apprenant(request.user)
        if apprenant:
            mon_inscription = (
                Inscription.objects.filter(apprenant=apprenant, session=session)
                .exclude(statut=Inscription.ANNULEE)
                .first()
            )
    return render(
        request,
        "training_sessions/session_detail.html",
        {
            "session": session,
            "peut_gerer": peut_gerer,
            "inscriptions": inscriptions,
            "mon_inscription": mon_inscription,
            "terminee": session.date_fin < timezone.localdate(),
        },
    )
