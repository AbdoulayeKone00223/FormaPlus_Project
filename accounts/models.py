from django.conf import settings
from django.db import models


class Profil(models.Model):
    ADMIN = "admin"
    FORMATEUR = "formateur"
    APPRENANT = "apprenant"
    ROLES = [
        (ADMIN, "Administrateur"),
        (FORMATEUR, "Formateur"),
        (APPRENANT, "Apprenant"),
    ]

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="profil",
        verbose_name="utilisateur",
    )
    role = models.CharField("rôle", max_length=10, choices=ROLES, default=APPRENANT)

    class Meta:
        verbose_name = "profil"
        verbose_name_plural = "profils"

    def __str__(self):
        return f"{self.user} ({self.get_role_display()})"
