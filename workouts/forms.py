# workouts/forms.py
from django import forms
from django.forms import inlineformset_factory

from .models import Workout, WorkoutMedia


class WorkoutForm(forms.ModelForm):
    class Meta:
        model = Workout
        fields = ["titulo", "descripcion"]
        widgets = {
            "titulo": forms.TextInput(attrs={
                "class": "input-text",
                "placeholder": "Nombre de la rutina (ej. Full Body Power)",
            }),
            "descripcion": forms.Textarea(attrs={
                "class": "textarea",
                "rows": 4,
                "placeholder": "Descripción general de la rutina...",
            }),
        }


class WorkoutMediaForm(forms.ModelForm):
    class Meta:
        model = WorkoutMedia
        fields = ["tipo", "url_video", "archivo_pdf", "texto", "imagen", "orden"]
        widgets = {
            "tipo": forms.Select(attrs={"class": "input-select"}),
            "url_video": forms.URLInput(attrs={
                "class": "input-text",
                "placeholder": "URL de YouTube (si aplica)",
            }),
            "archivo_pdf": forms.ClearableFileInput(attrs={"class": "input-file"}),
            "texto": forms.Textarea(attrs={
                "class": "textarea",
                "rows": 3,
                "placeholder": "Texto / instrucciones (si aplica)",
            }),
            "imagen": forms.ClearableFileInput(attrs={"class": "input-file"}),
            "orden": forms.NumberInput(attrs={"class": "input-number", "min": 0}),
        }


WorkoutMediaFormSet = inlineformset_factory(
    Workout,
    WorkoutMedia,
    form=WorkoutMediaForm,
    extra=1,
    can_delete=True,
)
