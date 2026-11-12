from decimal import Decimal

from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models


class Presence(models.Model):
    PRESENT = "present"
    ABSENT = "absent"
    EXCUSE = "excuse"
    STATUTS = [(PRESENT, "Présent"), (ABSENT, "Absent"), (EXCUSE, "Excusé")]

    inscription = models.ForeignKey(
        "enrollments.Inscription",
        on_delete=models.CASCADE,
        related_name="presences",
        verbose_name="inscription",
    )
    date = models.DateField("date")
    statut = models.CharField("statut", max_length=10, choices=STATUTS, default=PRESENT)

    class Meta:
        verbose_name = "présence"
        verbose_name_plural = "présences"
        ordering = ["date"]
        constraints = [
            models.UniqueConstraint(
                fields=["inscription", "date"], name="presence_unique_inscription_date"
            )
        ]

    def __str__(self):
        return f"{self.inscription.apprenant} - {self.date:%d/%m/%Y} : {self.get_statut_display()}"


class Evaluation(models.Model):
    inscription = models.OneToOneField(
        "enrollments.Inscription",
        on_delete=models.CASCADE,
        related_name="evaluation",
        verbose_name="inscription",
    )
    note = models.DecimalField(
        "note (sur 20)",
        max_digits=4,
        decimal_places=2,
        null=True,
        blank=True,
        validators=[MinValueValidator(Decimal("0")), MaxValueValidator(Decimal("20"))],
    )
    commentaire = models.TextField("commentaire", blank=True)
    valide_par_formateur = models.BooleanField("validé par le formateur", default=False)

    class Meta:
        verbose_name = "évaluation"
        verbose_name_plural = "évaluations"

    def __str__(self):
        note = "-" if self.note is None else self.note
        return f"{self.inscription.apprenant} : {note}/20"
