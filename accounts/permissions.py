"""Rôles et contrôle d'accès."""
from functools import wraps

from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied

ADMIN = "admin"
FORMATEUR = "formateur"
APPRENANT = "apprenant"

ROLE_LABELS = {
    ADMIN: "Administrateur",
    FORMATEUR: "Formateur",
    APPRENANT: "Apprenant",
}


def get_role(user):
    """Rôle d'un utilisateur : un superutilisateur est toujours administrateur."""
    if not user.is_authenticated:
        return None
    if user.is_superuser:
        return ADMIN
    profil = getattr(user, "profil", None)
    return profil.role if profil else None


def get_formateur(user):
    return getattr(user, "formateur", None)


def get_apprenant(user):
    return getattr(user, "apprenant", None)


def peut_gerer_session(user, session):
    """Administrateur, ou formateur responsable de la session."""
    role = get_role(user)
    if role == ADMIN:
        return True
    if role == FORMATEUR:
        return session.formateur.user_id is not None and session.formateur.user_id == user.pk
    return False


def role_required(*roles):
    """Exige une connexion et l'un des rôles indiqués (sinon erreur 403)."""

    def decorator(view):
        @wraps(view)
        def wrapper(request, *args, **kwargs):
            if get_role(request.user) not in roles:
                raise PermissionDenied
            return view(request, *args, **kwargs)

        return login_required(wrapper)

    return decorator
