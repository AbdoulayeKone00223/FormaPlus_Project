from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render
from django.utils import timezone

from certificates.models import Attestation
from certificates.services import evaluer
from courses.models import Formation
from enrollments.models import Inscription
from learners.models import Apprenant
from training_sessions.models import Session

from .forms import InscriptionForm
from .permissions import ADMIN, APPRENANT, FORMATEUR, get_apprenant, get_formateur, get_role


def demo_login(request, role):
    from django.contrib.auth import get_user_model
    User = get_user_model()
    demo_emails = {
        "admin": "admin@formaplus.test",
        "formateur": "formateur@formaplus.test",
        "apprenant": "apprenant@formaplus.test",
    }
    email = demo_emails.get(role.lower())
    if email:
        user = User.objects.filter(username=email).first()
        if user:
            login(request, user)
            role_noms = {
                "admin": "Administrateur",
                "formateur": "Formateur",
                "apprenant": "Apprenant",
            }
            messages.success(
                request,
                f"Mode Démo actif : Vous êtes connecté en tant que {role_noms.get(role, role)}."
            )
            return redirect("dashboard")
    messages.error(request, "Compte de démonstration introuvable.")
    return redirect("login")


def register(request):
    if request.user.is_authenticated:
        return redirect("dashboard")
    form = InscriptionForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        user = form.save()
        login(request, user)
        messages.success(request, "Compte créé. Bienvenue sur FormaPlus.")
        return redirect("dashboard")
    return render(request, "accounts/register.html", {"form": form})


@login_required
def dashboard(request):
    role = get_role(request.user)
    today = timezone.localdate()
    ctx = {}

    if role == ADMIN:
        ouvertes = Session.objects.filter(date_fin__gte=today)
        ctx.update(
            nb_formations=Formation.objects.count(),
            nb_sessions=ouvertes.count(),
            nb_apprenants=Apprenant.objects.count(),
            nb_attestations=Attestation.objects.count(),
            prochaines=ouvertes.select_related("formation", "formateur").order_by("date_debut")[:8],
        )
    elif role == FORMATEUR:
        formateur = get_formateur(request.user)
        sessions = Session.objects.filter(formateur=formateur) if formateur else Session.objects.none()
        ctx["sessions"] = sessions.select_related("formation").order_by("-date_debut")
    elif role == APPRENANT:
        apprenant = get_apprenant(request.user)
        lignes = []
        if apprenant:
            inscriptions = (
                Inscription.objects.filter(apprenant=apprenant)
                .exclude(statut=Inscription.ANNULEE)
                .select_related("session__formation")
                .order_by("-session__date_debut")
            )
            for inscription in inscriptions:
                ligne = evaluer(inscription)
                ligne["inscription"] = inscription
                ligne["attestation"] = getattr(inscription, "attestation", None)
                lignes.append(ligne)
        ctx["lignes"] = lignes
        ctx["ouvertes"] = Session.objects.filter(date_fin__gte=today).count()

    return render(request, "accounts/dashboard.html", ctx)
