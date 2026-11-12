from django.contrib import messages
from django.core.exceptions import PermissionDenied, ValidationError
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST

from accounts.permissions import ADMIN, APPRENANT, get_apprenant, get_role, role_required
from training_sessions.models import Session

from .forms import PaiementForm
from .models import Inscription, Paiement
from .services import inscrire


@require_POST
@role_required(APPRENANT)
def enroll(request, session_id):
    session = get_object_or_404(Session, pk=session_id)
    apprenant = get_apprenant(request.user)
    if not apprenant:
        messages.error(request, "Votre compte n'est lié à aucune fiche apprenant.")
        return redirect("session_detail", pk=session.pk)
    try:
        inscrire(apprenant, session)
        messages.success(request, f"Inscription confirmée : {session.formation.titre}.")
    except ValidationError as erreur:
        messages.error(request, " ".join(erreur.messages))
    return redirect("session_detail", pk=session.pk)


@require_POST
@role_required(ADMIN, APPRENANT)
def cancel_enrollment(request, pk):
    inscription = get_object_or_404(Inscription.objects.select_related("apprenant", "session"), pk=pk)
    role = get_role(request.user)
    if role == APPRENANT and inscription.apprenant.user_id != request.user.pk:
        raise PermissionDenied
    inscription.statut = Inscription.ANNULEE
    inscription.save(update_fields=["statut"])
    messages.success(request, "Inscription annulée.")
    if role == ADMIN:
        return redirect("inscription_list")
    return redirect("dashboard")


@role_required(ADMIN)
def inscription_list(request):
    inscriptions = Inscription.objects.select_related(
        "apprenant", "session__formation"
    ).order_by("-date_inscription")
    session_id = request.GET.get("session", "")
    if session_id.isdigit():
        inscriptions = inscriptions.filter(session_id=int(session_id))
    return render(
        request,
        "enrollments/inscription_list.html",
        {
            "inscriptions": inscriptions,
            "sessions": Session.objects.select_related("formation").order_by("-date_debut"),
            "session_id": session_id,
        },
    )


@role_required(ADMIN)
def paiement_create(request, pk):
    inscription = get_object_or_404(
        Inscription.objects.select_related("apprenant", "session__formation"), pk=pk
    )
    form = PaiementForm(request.POST or None, instance=Paiement(inscription=inscription))
    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, "Paiement enregistré.")
        return redirect("paiement_create", pk=inscription.pk)
    return render(
        request,
        "enrollments/paiement_form.html",
        {
            "form": form,
            "inscription": inscription,
            "paiements": inscription.paiements.all(),
        },
    )
