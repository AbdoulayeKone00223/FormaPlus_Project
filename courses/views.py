from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, render
from django.utils import timezone

from .models import Formation


@login_required
def formation_list(request):
    formations = Formation.objects.select_related("centre")
    return render(request, "courses/formation_list.html", {"formations": formations})


@login_required
def formation_detail(request, pk):
    formation = get_object_or_404(Formation.objects.select_related("centre"), pk=pk)
    sessions = formation.sessions.select_related("formateur").filter(
        date_fin__gte=timezone.localdate()
    ).order_by("date_debut")
    return render(
        request,
        "courses/formation_detail.html",
        {"formation": formation, "sessions": sessions},
    )
