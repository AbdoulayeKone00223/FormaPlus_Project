from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django.db import transaction

from learners.models import Apprenant
from trainers.models import Formateur

from .models import Profil

User = get_user_model()


def style_fields(form):
    """Ajoute les classes Bootstrap aux champs d'un formulaire."""
    for field in form.fields.values():
        widget = field.widget
        if isinstance(widget, forms.CheckboxInput):
            widget.attrs.setdefault("class", "form-check-input")
        elif isinstance(widget, forms.Select):
            widget.attrs.setdefault("class", "form-select")
        else:
            widget.attrs.setdefault("class", "form-control")


class ConnexionForm(AuthenticationForm):
    """Connexion par adresse e-mail (l'e-mail sert d'identifiant)."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["username"].label = "Adresse e-mail"
        self.fields["username"].widget.attrs["autofocus"] = True
        style_fields(self)

    def clean_username(self):
        username = self.cleaned_data["username"].strip()
        return username.lower() if "@" in username else username


class InscriptionForm(UserCreationForm):
    """Création de compte (apprenant ou formateur). L'administrateur est créé en ligne de commande."""

    nom = forms.CharField(label="Nom complet", max_length=150)
    email = forms.EmailField(label="Adresse e-mail")
    telephone = forms.CharField(label="Téléphone", max_length=30, required=False)
    role = forms.ChoiceField(
        label="Je suis",
        choices=[(Profil.APPRENANT, "Apprenant"), (Profil.FORMATEUR, "Formateur")],
        initial=Profil.APPRENANT,
    )
    specialite = forms.CharField(label="Spécialité", max_length=150, required=False)

    field_order = ["nom", "email", "telephone", "role", "specialite", "password1", "password2"]

    class Meta(UserCreationForm.Meta):
        model = User
        fields = ()

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        style_fields(self)

    def clean_email(self):
        email = self.cleaned_data["email"].strip().lower()
        if User.objects.filter(username__iexact=email).exists() or User.objects.filter(
            email__iexact=email
        ).exists():
            raise forms.ValidationError("Un compte existe déjà avec cette adresse e-mail.")
        return email

    @transaction.atomic
    def save(self, commit=True):
        user = super().save(commit=False)
        email = self.cleaned_data["email"]
        user.username = email
        user.email = email
        user.first_name = self.cleaned_data["nom"][:150]
        user.save()
        role = self.cleaned_data["role"]
        Profil.objects.create(user=user, role=role)
        if role == Profil.FORMATEUR:
            Formateur.objects.create(
                user=user,
                nom=self.cleaned_data["nom"],
                specialite=self.cleaned_data["specialite"],
            )
        else:
            Apprenant.objects.create(
                user=user,
                nom=self.cleaned_data["nom"],
                telephone=self.cleaned_data["telephone"],
            )
        return user
