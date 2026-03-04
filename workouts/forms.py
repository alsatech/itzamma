# workouts/forms.py
from django import forms
from django.forms import inlineformset_factory

from .models import Ejercicio, EjercicioMedia, Rutina


class EjercicioForm(forms.ModelForm):
    class Meta:
        model = Ejercicio
        fields = ["nombre", "categoria", "descripcion"]
        widgets = {
            "nombre": forms.TextInput(attrs={
                "class": "input-text",
                "placeholder": "Ej. Press inclinado con mancuernas",
            }),
            "categoria": forms.HiddenInput(),
            "descripcion": forms.Textarea(attrs={
                "class": "textarea",
                "rows": 3,
                "placeholder": "Descripción opcional...",
            }),
        }


class EjercicioMediaForm(forms.ModelForm):
    class Meta:
        model = EjercicioMedia
        fields = ["tipo", "url_video", "imagen", "orden"]
        widgets = {
            "tipo": forms.HiddenInput(),
            "url_video": forms.URLInput(attrs={
                "class": "input-text",
                "placeholder": "URL de YouTube",
            }),
            "imagen": forms.ClearableFileInput(attrs={"class": "input-file"}),
            "orden": forms.HiddenInput(),
        }


EjercicioMediaFormSet = inlineformset_factory(
    Ejercicio,
    EjercicioMedia,
    form=EjercicioMediaForm,
    extra=1,
    can_delete=True,
)


class RutinaForm(forms.ModelForm):
    class Meta:
        model = Rutina
        fields = ["nombre", "descripcion", "deporte"]
        widgets = {
            "nombre": forms.TextInput(attrs={
                "class": "input-text",
                "placeholder": "Ej. Full Body Fuerza — Semana 1",
            }),
            "descripcion": forms.Textarea(attrs={
                "class": "textarea",
                "rows": 3,
                "placeholder": "Descripción opcional...",
            }),
            "deporte": forms.HiddenInput(),
        }
