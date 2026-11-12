from django.conf import settings
from django.db import models


class Formateur(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="formateur",
        verbose_name="compte utilisateur",
    )
    nom = models.CharField("nom", max_length=150)
    specialite = models.CharField("spécialité", max_length=150, blank=True)

    class Meta:
        verbose_name = "formateur"
        verbose_name_plural = "formateurs"
        ordering = ["nom"]

    def __str__(self):
        return self.nom
