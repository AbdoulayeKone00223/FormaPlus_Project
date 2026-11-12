from django.conf import settings

from .permissions import ROLE_LABELS, get_role


def globales(request):
    role = get_role(request.user)
    return {
        "role": role,
        "role_label": ROLE_LABELS.get(role, ""),
        "devise": settings.DEVISE,
    }
