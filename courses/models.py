from decimal import Decimal

from django.core.validators import MinValueValidator
from django.db import models


class Centre(models.Model):
    nom = models.CharField("nom", max_length=150)
    adresse = models.CharField("adresse", max_length=255, blank=True)

    class Meta:
        verbose_name = "centre"
        verbose_name_plural = "centres"
        ordering = ["nom"]

    def __str__(self):
        return self.nom


class Formation(models.Model):
    centre = models.ForeignKey(
        Centre, on_delete=models.CASCADE, related_name="formations", verbose_name="centre"
    )
    titre = models.CharField("titre", max_length=200)
    description = models.TextField("description", blank=True)
    duree_heures = models.PositiveIntegerField(
        "durée (heures)", validators=[MinValueValidator(1)]
    )
    prix = models.DecimalField(
        "prix",
        max_digits=10,
        decimal_places=2,
        default=Decimal("0"),
        validators=[MinValueValidator(Decimal("0"))],
    )

    class Meta:
        verbose_name = "formation"
        verbose_name_plural = "formations"
        ordering = ["titre"]

    def __str__(self):
        return self.titre
