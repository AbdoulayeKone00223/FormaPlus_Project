from datetime import timedelta

from django.core.exceptions import ValidationError
from django.core.validators import MinValueValidator
from django.db import models


class Session(models.Model):
    formation = models.ForeignKey(
        "courses.Formation",
        on_delete=models.PROTECT,
        related_name="sessions",
        verbose_name="formation",
    )
    formateur = models.ForeignKey(
        "trainers.Formateur",
        on_delete=models.PROTECT,
        related_name="sessions",
        verbose_name="formateur",
    )
    date_debut = models.DateField("date de début")
    date_fin = models.DateField("date de fin")
    lieu = models.CharField("lieu", max_length=200)
    capacite = models.PositiveIntegerField("capacité", validators=[MinValueValidator(1)])

    class Meta:
        verbose_name = "session"
        verbose_name_plural = "sessions"
        ordering = ["-date_debut"]

    def __str__(self):
        return f"{self.formation} ({self.date_debut:%d/%m/%Y} - {self.date_fin:%d/%m/%Y})"

    def clean(self):
        if self.date_debut and self.date_fin and self.date_fin < self.date_debut:
            raise ValidationError(
                {"date_fin": "La date de fin doit être postérieure ou égale à la date de début."}
            )

    @property
    def nb_seances(self):
        """Une séance par jour entre la date de début et la date de fin (incluses)."""
        return (self.date_fin - self.date_debut).days + 1

    def dates(self):
        return [self.date_debut + timedelta(days=i) for i in range(self.nb_seances)]

    @property
    def places_prises(self):
        return self.inscriptions.exclude(statut="annulee").count()

    @property
    def places_restantes(self):
        return max(self.capacite - self.places_prises, 0)

    @property
    def est_complete(self):
        return self.places_prises >= self.capacite

    @property
    def taux_remplissage(self):
        return round(self.places_prises * 100 / self.capacite) if self.capacite else 0
