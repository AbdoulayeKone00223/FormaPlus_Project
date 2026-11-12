"""Tests d'intégration (nécessitent Django) : python manage.py test"""
from datetime import timedelta
from decimal import Decimal

from django.core.exceptions import ValidationError
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from accounts.models import Profil
from attendance.models import Evaluation, Presence
from certificates.models import Attestation
from certificates.services import generer_attestation, taux_presence
from courses.models import Centre, Formation
from django.contrib.auth import get_user_model
from enrollments.models import Inscription, Paiement
from enrollments.services import inscrire
from learners.models import Apprenant
from trainers.models import Formateur
from training_sessions.models import Session

User = get_user_model()


class BaseTestCase(TestCase):
    def setUp(self):
        today = timezone.localdate()
        centre = Centre.objects.create(nom="Centre test")
        self.formation = Formation.objects.create(
            centre=centre, titre="Python", duree_heures=10, prix=Decimal("1000")
        )
        self.u_formateur = User.objects.create_user("f@test.io", password="Passe12345!")
        Profil.objects.create(user=self.u_formateur, role=Profil.FORMATEUR)
        self.formateur = Formateur.objects.create(user=self.u_formateur, nom="Formateur")
        self.u_apprenant = User.objects.create_user("a@test.io", password="Passe12345!")
        Profil.objects.create(user=self.u_apprenant, role=Profil.APPRENANT)
        self.apprenant = Apprenant.objects.create(user=self.u_apprenant, nom="Apprenant")
        self.session = Session.objects.create(
            formation=self.formation, formateur=self.formateur,
            date_debut=today - timedelta(days=4), date_fin=today - timedelta(days=1),
            lieu="Salle 1", capacite=2,
        )
        self.inscription = Inscription.objects.create(apprenant=self.apprenant, session=self.session)

    def remplir(self, presents=4, note="12", paye=True):
        for jour in self.session.dates()[:presents]:
            Presence.objects.create(inscription=self.inscription, date=jour, statut=Presence.PRESENT)
        Evaluation.objects.create(inscription=self.inscription, note=Decimal(note))
        if paye:
            Paiement.objects.create(inscription=self.inscription, montant=Decimal("1000"))


class AttestationTests(BaseTestCase):
    def test_taux_presence(self):
        self.remplir(presents=3)
        self.assertEqual(taux_presence(self.inscription), Decimal("75"))

    def test_generation_si_conditions_remplies(self):
        self.remplir()
        attestation, creee = generer_attestation(self.inscription)
        self.assertTrue(creee)
        self.assertTrue(attestation.reference.startswith("ATT-"))
        _, creee2 = generer_attestation(self.inscription)
        self.assertFalse(creee2)
        self.assertEqual(Attestation.objects.count(), 1)

    def test_refus_si_presence_insuffisante(self):
        self.remplir(presents=2)
        with self.assertRaises(ValidationError):
            generer_attestation(self.inscription)

    def test_refus_si_non_paye(self):
        self.remplir(paye=False)
        with self.assertRaises(ValidationError):
            generer_attestation(self.inscription)

    def test_telechargement_pdf_par_le_proprietaire(self):
        self.remplir()
        attestation, _ = generer_attestation(self.inscription)
        self.client.login(username="a@test.io", password="Passe12345!")
        reponse = self.client.get(reverse("download_attestation", args=[attestation.pk]))
        self.assertEqual(reponse.status_code, 200)
        self.assertEqual(reponse["Content-Type"], "application/pdf")
        self.assertTrue(reponse.content.startswith(b"%PDF"))

    def test_telechargement_refuse_a_un_autre_apprenant(self):
        self.remplir()
        attestation, _ = generer_attestation(self.inscription)
        autre = User.objects.create_user("autre@test.io", password="Passe12345!")
        Profil.objects.create(user=autre, role=Profil.APPRENANT)
        Apprenant.objects.create(user=autre, nom="Autre")
        self.client.login(username="autre@test.io", password="Passe12345!")
        reponse = self.client.get(reverse("download_attestation", args=[attestation.pk]))
        self.assertEqual(reponse.status_code, 403)


class InscriptionTests(BaseTestCase):
    def futur(self, capacite):
        today = timezone.localdate()
        return Session.objects.create(
            formation=self.formation, formateur=self.formateur,
            date_debut=today + timedelta(days=5), date_fin=today + timedelta(days=6),
            lieu="Salle 2", capacite=capacite,
        )

    def test_inscription_refusee_si_doublon(self):
        session = self.futur(5)
        inscrire(self.apprenant, session)
        with self.assertRaises(ValidationError):
            inscrire(self.apprenant, session)

    def test_inscription_refusee_si_complete(self):
        session = self.futur(1)
        inscrire(self.apprenant, session)
        autre = Apprenant.objects.create(nom="Autre")
        with self.assertRaises(ValidationError):
            inscrire(autre, session)

    def test_inscription_refusee_si_session_terminee(self):
        autre = Apprenant.objects.create(nom="Autre")
        with self.assertRaises(ValidationError):
            inscrire(autre, self.session)

    def test_paiement_ne_depasse_pas_le_prix(self):
        paiement = Paiement(inscription=self.inscription, montant=Decimal("1500"))
        with self.assertRaises(ValidationError):
            paiement.full_clean()


class ComptesTests(TestCase):
    def test_inscription_apprenant_puis_connexion(self):
        reponse = self.client.post(reverse("register"), {
            "nom": "Nouvel Apprenant", "email": "Nouveau@Test.io", "telephone": "123",
            "role": "apprenant", "specialite": "",
            "password1": "MotDePasse!2026", "password2": "MotDePasse!2026",
        })
        self.assertRedirects(reponse, reverse("dashboard"))
        user = User.objects.get(username="nouveau@test.io")
        self.assertEqual(user.profil.role, Profil.APPRENANT)
        self.assertTrue(Apprenant.objects.filter(user=user).exists())
        self.client.logout()
        self.assertTrue(self.client.login(username="nouveau@test.io", password="MotDePasse!2026"))

    def test_inscription_formateur(self):
        self.client.post(reverse("register"), {
            "nom": "Nouveau Formateur", "email": "form@test.io", "telephone": "",
            "role": "formateur", "specialite": "Réseaux",
            "password1": "MotDePasse!2026", "password2": "MotDePasse!2026",
        })
        user = User.objects.get(username="form@test.io")
        self.assertEqual(user.formateur.specialite, "Réseaux")

    def test_email_deja_utilise(self):
        User.objects.create_user("deja@test.io", email="deja@test.io", password="x")
        reponse = self.client.post(reverse("register"), {
            "nom": "X", "email": "deja@test.io", "role": "apprenant",
            "password1": "MotDePasse!2026", "password2": "MotDePasse!2026",
        })
        self.assertEqual(reponse.status_code, 200)
        self.assertFalse(Profil.objects.exists())

    def test_pages_protegees(self):
        reponse = self.client.get(reverse("dashboard"))
        self.assertEqual(reponse.status_code, 302)
        self.assertIn(reverse("login"), reponse["Location"])
