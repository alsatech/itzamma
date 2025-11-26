from django.db import models
from django.conf import settings

DEPORTES = [
    ("tenis", "Tenis"),
    ("boxeo", "Boxeo"),
    ("gym", "Gym"),
    ("yoga", "Yoga"),
    ("running", "Running"),
    ("natacion", "Natación"),
    ("hyrox", "Hyrox"),
    ("otros", "Otros"),
]

class UserProfile(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="profile"
    )

    # Datos básicos
    nombre = models.CharField(max_length=150)
    edad = models.IntegerField(null=True, blank=True)
    telefono = models.CharField(max_length=20, null=True, blank=True)
    correo = models.EmailField(null=True, blank=True)
    residencia = models.CharField(max_length=255, null=True, blank=True)
    # Datos físicos
    peso = models.DecimalField(max_digits=5, decimal_places=1, null=True, blank=True)
    estatura = models.DecimalField(max_digits=4, decimal_places=2, null=True, blank=True)
    masa_muscular = models.DecimalField(max_digits=5, decimal_places=1, null=True, blank=True)
    masa_grasa = models.DecimalField(max_digits=5, decimal_places=1, null=True, blank=True)
    # Historial clínico
    lesiones = models.TextField(null=True, blank=True)
    cirugias = models.TextField(null=True, blank=True)
    medicamentos = models.TextField(null=True, blank=True)
    suplementos = models.TextField(null=True, blank=True)
    # Objetivo
    objetivo = models.CharField(max_length=255, null=True, blank=True)
    # Deporte elegido
    deporte = models.CharField(max_length=50, choices=DEPORTES, default="gym")
    # Auditoría
    creado = models.DateTimeField(auto_now_add=True)
    actualizado = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Perfil de {self.user.username}"
