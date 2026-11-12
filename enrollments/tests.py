from datetime import date
from decimal import Decimal

from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse

from accounts.models import Profil
from courses.models import Centre, Formation
from enrollments.models import Inscription, Paiement
from learners.models import Apprenant
from trainers.models import Formateur
from training_sessions.models import Session

User = get_user_model()


class PaiementViewTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.admin = User.objects.create_user(
            username="admin@test.com", email="admin@test.com", password="password123"
        )
        Profil.objects.create(user=self.admin, role=Profil.ADMIN)

        self.centre = Centre.objects.create(nom="Centre Test")
        self.formation = Formation.objects.create(
            centre=self.centre, titre="Python Pro", duree_heures=40, prix=Decimal("150000")
        )
        self.formateur_user = User.objects.create_user(
            username="formateur@test.com", email="formateur@test.com", password="password123"
        )
        self.formateur = Formateur.objects.create(user=self.formateur_user, nom="Formateur Test")
        self.session = Session.objects.create(
            formation=self.formation,
            formateur=self.formateur,
            date_debut=date(2026, 11, 10),
            date_fin=date(2026, 11, 15),
            lieu="Salle A",
            capacite=20,
        )
        self.apprenant_user = User.objects.create_user(
            username="apprenant@test.com", email="apprenant@test.com", password="password123"
        )
        self.apprenant = Apprenant.objects.create(user=self.apprenant_user, nom="Apprenant Test")
        self.inscription = Inscription.objects.create(
            session=self.session, apprenant=self.apprenant
        )
        # Create an existing payment with date
        self.paiement = Paiement.objects.create(
            inscription=self.inscription, montant=Decimal("50000"), date=date(2026, 11, 8)
        )

    def test_paiement_create_get(self):
        self.client.force_login(self.admin)
        url = reverse("paiement_create", kwargs={"pk": self.inscription.pk})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "50000")
        self.assertContains(response, "08/11/2026")

    def test_paiement_create_post_valid(self):
        self.client.force_login(self.admin)
        url = reverse("paiement_create", kwargs={"pk": self.inscription.pk})
        response = self.client.post(
            url, {"montant": "100000", "date": "2026-11-08"}
        )
        self.assertEqual(response.status_code, 302)
        self.inscription.refresh_from_db()
        self.assertTrue(self.inscription.est_payee)

    def test_paiement_create_post_invalid_renders_template_without_error(self):
        self.client.force_login(self.admin)
        url = reverse("paiement_create", kwargs={"pk": self.inscription.pk})
        # Empty POST triggers form validation error and re-renders template
        response = self.client.post(url, {})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "08/11/2026")

