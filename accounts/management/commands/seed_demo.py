"""Crée un jeu de données de démonstration : python manage.py seed_demo"""
from datetime import timedelta
from decimal import Decimal

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand
from django.db import transaction
from django.utils import timezone

from accounts.models import Profil
from attendance.models import Evaluation, Presence
from certificates.services import generer_attestation
from courses.models import Centre, Formation
from enrollments.models import Inscription, Paiement
from learners.models import Apprenant
from trainers.models import Formateur
from training_sessions.models import Session

User = get_user_model()

COMPTES = {
    "admin": ("admin@formaplus.test", "Admin12345"),
    "formateur": ("formateur@formaplus.test", "Formateur12345"),
    "apprenant": ("apprenant@formaplus.test", "Apprenant12345"),
}


def creer_user(email, mot_de_passe, nom, role, superuser=False):
    user = User(username=email, email=email, first_name=nom)
    user.is_superuser = superuser
    user.is_staff = superuser
    user.set_password(mot_de_passe)
    user.save()
    Profil.objects.create(user=user, role=role)
    return user


class Command(BaseCommand):
    help = "Peuple la base avec des données de démonstration."

    @transaction.atomic
    def handle(self, *args, **options):
        if User.objects.filter(username=COMPTES["admin"][0]).exists():
            self.stdout.write("Les données de démonstration existent déjà.")
            return

        today = timezone.localdate()
        creer_user(*COMPTES["admin"], "Administrateur", Profil.ADMIN, superuser=True)

        centre = Centre.objects.create(nom="Centre FormaPlus", adresse="Quartier du Fleuve, Bamako")
        python = Formation.objects.create(
            centre=centre, titre="Python pour débutants", duree_heures=15, prix=Decimal("50000"),
            description="Bases de la programmation avec Python : variables, boucles, fonctions.",
        )
        compta = Formation.objects.create(
            centre=centre, titre="Comptabilité de base", duree_heures=20, prix=Decimal("40000"),
            description="Principes comptables, journal, grand livre et bilan simplifié.",
        )
        marketing = Formation.objects.create(
            centre=centre, titre="Marketing digital", duree_heures=12, prix=Decimal("60000"),
            description="Réseaux sociaux, publicité en ligne et mesure des résultats.",
        )
        Formation.objects.create(
            centre=centre, titre="Bureautique avancée", duree_heures=10, prix=Decimal("30000"),
            description="Tableurs, traitement de texte et présentations professionnelles.",
        )

        u_f1 = creer_user(*COMPTES["formateur"], "M. Sidibé", Profil.FORMATEUR)
        f1 = Formateur.objects.create(user=u_f1, nom="M. Sidibé", specialite="Informatique")
        f2 = Formateur.objects.create(nom="Mme Konaté", specialite="Comptabilité et gestion")

        u_a1 = creer_user(*COMPTES["apprenant"], "Awa Traoré", Profil.APPRENANT)
        awa = Apprenant.objects.create(user=u_a1, nom="Awa Traoré", telephone="+223 70 00 00 01")
        autres = [
            Apprenant.objects.create(nom=nom, telephone=tel)
            for nom, tel in [
                ("Moussa Keita", "+223 70 00 00 02"),
                ("Fatoumata Diarra", "+223 70 00 00 03"),
                ("Ibrahim Coulibaly", "+223 70 00 00 04"),
                ("Aminata Camara", "+223 70 00 00 05"),
            ]
        ]
        moussa, fatoumata, ibrahim, aminata = autres

        # Session terminée (3 jours) : cas variés pour la démonstration
        terminee = Session.objects.create(
            formation=python, formateur=f1, date_debut=today - timedelta(days=10),
            date_fin=today - timedelta(days=8), lieu="Salle B2", capacite=20,
        )
        # Session en cours, session à venir, session complète
        Session.objects.create(
            formation=compta, formateur=f2, date_debut=today - timedelta(days=1),
            date_fin=today + timedelta(days=1), lieu="Salle A1", capacite=20,
        )
        Session.objects.create(
            formation=marketing, formateur=f1, date_debut=today + timedelta(days=14),
            date_fin=today + timedelta(days=16), lieu="Salle C3", capacite=15,
        )
        complete = Session.objects.create(
            formation=compta, formateur=f2, date_debut=today + timedelta(days=21),
            date_fin=today + timedelta(days=22), lieu="Salle A1", capacite=2,
        )
        Inscription.objects.create(apprenant=moussa, session=complete)
        Inscription.objects.create(apprenant=aminata, session=complete)

        jours = terminee.dates()

        def inscrire(apprenant, presences, note, valide, paye):
            ins = Inscription.objects.create(apprenant=apprenant, session=terminee)
            for jour, statut in zip(jours, presences):
                Presence.objects.create(inscription=ins, date=jour, statut=statut)
            Evaluation.objects.create(inscription=ins, note=note, valide_par_formateur=valide)
            if paye:
                Paiement.objects.create(inscription=ins, montant=python.prix, date=terminee.date_debut)
            return ins

        P, A = Presence.PRESENT, Presence.ABSENT
        ins_awa = inscrire(awa, [P, P, P], Decimal("15"), False, True)      # éligible
        inscrire(moussa, [P, A, P], Decimal("13"), False, True)             # présence 67 %
        inscrire(fatoumata, [P, P, P], Decimal("8"), False, True)           # note basse
        inscrire(ibrahim, [P, P, P], Decimal("9"), True, True)              # validé par le formateur
        inscrire(aminata, [P, P, P], Decimal("16"), False, False)           # paiement incomplet

        generer_attestation(ins_awa)

        self.stdout.write(self.style.SUCCESS("Données de démonstration créées."))
        for role, (email, mdp) in COMPTES.items():
            self.stdout.write(f"  {role:<10} {email}  /  {mdp}")
