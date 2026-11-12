from django.db import models
from django.utils import timezone


class Attestation(models.Model):
    inscription = models.OneToOneField(
        "enrollments.Inscription",
        on_delete=models.CASCADE,
        related_name="attestation",
        verbose_name="inscription",
    )
    reference = models.CharField("référence", max_length=40, unique=True)
    date_emission = models.DateField("date d'émission", default=timezone.localdate)

    class Meta:
        verbose_name = "attestation"
        verbose_name_plural = "attestations"
        ordering = ["-date_emission", "-id"]

    def __str__(self):
        return self.reference
