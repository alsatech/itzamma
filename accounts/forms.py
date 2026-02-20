from django import forms
from django.contrib.auth import get_user_model

User = get_user_model()


class CrearClienteForm(forms.Form):
    username = forms.CharField(max_length=150, label="Usuario")
    email = forms.EmailField(label="Correo electrónico")
    password1 = forms.CharField(widget=forms.PasswordInput, label="Contraseña")
    password2 = forms.CharField(widget=forms.PasswordInput, label="Confirmar contraseña")

    def clean_username(self):
        username = self.cleaned_data.get("username")
        if User.objects.filter(username=username).exists():
            raise forms.ValidationError("Ese nombre de usuario ya está en uso.")
        return username

    def clean(self):
        cleaned_data = super().clean()
        p1 = cleaned_data.get("password1")
        p2 = cleaned_data.get("password2")
        if p1 and p2 and p1 != p2:
            raise forms.ValidationError("Las contraseñas no coinciden.")
        return cleaned_data


class CrearInstructorForm(forms.Form):
    username = forms.CharField(max_length=150, label="Usuario")
    email = forms.EmailField(label="Correo electrónico")
    password1 = forms.CharField(widget=forms.PasswordInput, label="Contraseña")
    password2 = forms.CharField(widget=forms.PasswordInput, label="Confirmar contraseña")
    deporte = forms.CharField(max_length=100, label="Deporte / Especialidad")
    biografia = forms.CharField(
        widget=forms.Textarea(attrs={"rows": 3}),
        label="Biografía",
        required=False
    )

    def clean_username(self):
        username = self.cleaned_data.get("username")
        if User.objects.filter(username=username).exists():
            raise forms.ValidationError("Ese nombre de usuario ya está en uso.")
        return username

    def clean(self):
        cleaned_data = super().clean()
        p1 = cleaned_data.get("password1")
        p2 = cleaned_data.get("password2")
        if p1 and p2 and p1 != p2:
            raise forms.ValidationError("Las contraseñas no coinciden.")
        return cleaned_data
