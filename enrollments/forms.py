from django import forms

from accounts.forms import style_fields

from .models import Paiement


class PaiementForm(forms.ModelForm):
    class Meta:
        model = Paiement
        fields = ["montant", "date"]
        widgets = {"date": forms.DateInput(attrs={"type": "date"}, format="%Y-%m-%d")}

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["date"].input_formats = ["%Y-%m-%d", "%d/%m/%Y"]
        style_fields(self)
