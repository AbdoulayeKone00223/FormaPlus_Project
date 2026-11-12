from decimal import Decimal

from django.core.exceptions import ValidationError
from django.core.validators import MinValueValidator
from django.db import models
from django.db.models import Sum
from django.utils import timezone


class Inscription(models.Model):
    CONFIRMEE = "confirmee"
    EN_ATTENTE = "en_attente"
    ANNULEE = "annulee"
    STATUTS = [
        (CONFIRMEE, "Confirmée"),
        (EN_ATTENTE, "En attente"),
        (ANNULEE, "Annulée"),
    ]

    apprenant = models.ForeignKey(
        "learners.Apprenant",
        on_delete=models.CASCADE,
        related_name="inscriptions",
        verbose_name="apprenant",
    )
    session = models.ForeignKey(
        "training_sessions.Session",
        on_delete=models.CASCADE,
        related_name="inscriptions",
        verbose_name="session",
    )
    statut = models.CharField("statut", max_length=12, choices=STATUTS, default=CONFIRMEE)
    date_inscription = models.DateTimeField("date d'inscription", auto_now_add=True)

    class Meta:
        verbose_name = "inscription"
        verbose_name_plural = "inscriptions"
        ordering = ["-date_inscription"]
        constraints = [
            models.UniqueConstraint(
                fields=["apprenant", "session"],
                name="inscription_unique_apprenant_session",
            )
        ]

    def __str__(self):
        return f"{self.apprenant} - {self.session}"

    def clean(self):
        if self.statut != self.ANNULEE and self.session_id:
            autres = self.session.inscriptions.exclude(statut=self.ANNULEE).exclude(pk=self.pk)
            if autres.count() >= self.session.capacite:
                raise ValidationError("La capacité maximale de la session est atteinte.")

    @property
    def prix(self):
        return self.session.formation.prix

    @property
    def total_paye(self):
        return self.paiements.aggregate(total=Sum("montant"))["total"] or Decimal("0")

    @property
    def reste_a_payer(self):
        return max(self.prix - self.total_paye, Decimal("0"))

    @property
    def est_payee(self):
        return self.reste_a_payer <= 0


class Paiement(models.Model):
    inscription = models.ForeignKey(
        Inscription,
        on_delete=models.CASCADE,
        related_name="paiements",
        verbose_name="inscription",
    )
    montant = models.DecimalField(
        "montant",
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(Decimal("0.01"))],
    )
    date = models.DateField("date", default=timezone.localdate)

    class Meta:
        verbose_name = "paiement"
        verbose_name_plural = "paiements"
        ordering = ["-date", "-id"]

    def __str__(self):
        return f"{self.montant} ({self.date:%d/%m/%Y})"

    def clean(self):
        if self.inscription_id and self.montant is not None:
            deja = (
                self.inscription.paiements.exclude(pk=self.pk).aggregate(t=Sum("montant"))["t"]
                or Decimal("0")
            )
            if deja + self.montant > self.inscription.prix:
                raise ValidationError(
                    {"montant": "Le total des paiements dépasserait le prix de la formation."}
                )
