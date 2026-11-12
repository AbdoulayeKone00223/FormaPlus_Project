from decimal import Decimal, InvalidOperation

from django.contrib import messages
from django.core.exceptions import PermissionDenied
from django.shortcuts import get_object_or_404, redirect, render

from accounts.permissions import ADMIN, FORMATEUR, peut_gerer_session, role_required
from enrollments.models import Inscription
from training_sessions.models import Session

from .models import Evaluation, Presence


def _session_geree(request, session_id):
    session = get_object_or_404(
        Session.objects.select_related("formation", "formateur"), pk=session_id
    )
    if not peut_gerer_session(request.user, session):
        raise PermissionDenied
    return session


def _inscriptions(session):
    return list(
        session.inscriptions.exclude(statut=Inscription.ANNULEE)
        .select_related("apprenant")
        .order_by("apprenant__nom")
    )


@role_required(ADMIN, FORMATEUR)
def presence_sheet(request, session_id):
    session = _session_geree(request, session_id)
    inscriptions = _inscriptions(session)
    dates = session.dates()

    if request.method == "POST":
        valides = {valeur for valeur, _ in Presence.STATUTS}
        for inscription in inscriptions:
            for jour in dates:
                valeur = request.POST.get(f"p_{inscription.pk}_{jour.isoformat()}", "")
                if valeur in valides:
                    Presence.objects.update_or_create(
                        inscription=inscription, date=jour, defaults={"statut": valeur}
                    )
                else:
                    Presence.objects.filter(inscription=inscription, date=jour).delete()
        messages.success(request, "Feuille de présence enregistrée.")
        return redirect("presence_sheet", session_id=session.pk)

    existantes = {
        (p.inscription_id, p.date): p.statut
        for p in Presence.objects.filter(inscription__in=inscriptions)
    }
    lignes = [
        {
            "inscription": inscription,
            "cellules": [
                {
                    "date": jour,
                    "nom": f"p_{inscription.pk}_{jour.isoformat()}",
                    "valeur": existantes.get((inscription.pk, jour), ""),
                }
                for jour in dates
            ],
        }
        for inscription in inscriptions
    ]
    return render(
        request,
        "attendance/presence.html",
        {"session": session, "dates": dates, "lignes": lignes, "statuts": Presence.STATUTS},
    )


@role_required(ADMIN, FORMATEUR)
def evaluation_sheet(request, session_id):
    session = _session_geree(request, session_id)
    inscriptions = _inscriptions(session)

    if request.method == "POST":
        erreurs = []
        for inscription in inscriptions:
            brut = request.POST.get(f"note_{inscription.pk}", "").strip().replace(",", ".")
            note = None
            if brut:
                try:
                    note = Decimal(brut)
                except InvalidOperation:
                    erreurs.append(f"{inscription.apprenant} : note invalide.")
                    continue
                if not note.is_finite() or not (Decimal("0") <= note <= Decimal("20")):
                    erreurs.append(f"{inscription.apprenant} : la note doit être entre 0 et 20.")
                    continue
                note = note.quantize(Decimal("0.01"))
            evaluation, _ = Evaluation.objects.get_or_create(inscription=inscription)
            evaluation.note = note
            evaluation.commentaire = request.POST.get(f"commentaire_{inscription.pk}", "").strip()
            evaluation.valide_par_formateur = f"valide_{inscription.pk}" in request.POST
            evaluation.save()
        if erreurs:
            for erreur in erreurs:
                messages.error(request, erreur)
        else:
            messages.success(request, "Évaluations enregistrées.")
        return redirect("evaluation_sheet", session_id=session.pk)

    lignes = [
        {"inscription": i, "evaluation": getattr(i, "evaluation", None)} for i in inscriptions
    ]
    return render(
        request, "attendance/evaluation.html", {"session": session, "lignes": lignes}
    )
