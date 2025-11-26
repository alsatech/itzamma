from django import forms
from .models import UserProfile

class UserProfileForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = [
            "nombre",
            "peso",
            "estatura",
            "edad",
            "telefono",
            "residencia",
            "masa_muscular",
            "masa_grasa",
            "lesiones",
            "cirugias",
            "medicamentos",
            "suplementos",
            "objetivo",
            "deporte",
        ]

        widgets = {
            "lesiones": forms.Textarea(attrs={"rows": 2}),
            "cirugias": forms.Textarea(attrs={"rows": 2}),
            "medicamentos": forms.Textarea(attrs={"rows": 2}),
            "suplementos": forms.Textarea(attrs={"rows": 2}),
        }
