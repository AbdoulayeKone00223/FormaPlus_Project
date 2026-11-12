from django.conf import settings
from django.db import models


class Apprenant(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="apprenant",
        verbose_name="compte utilisateur",
    )
    nom = models.CharField("nom", max_length=150)
    telephone = models.CharField("téléphone", max_length=30, blank=True)

    class Meta:
        verbose_name = "apprenant"
        verbose_name_plural = "apprenants"
        ordering = ["nom"]

    def __str__(self):
        return self.nom
