from django.db import models
from django.conf import settings
from django.core.validators import FileExtensionValidator

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
    foto = models.ImageField(upload_to="profiles/", blank=True, null=True)
    # Datos físicos
    peso = models.DecimalField(max_digits=5, decimal_places=1, null=True, blank=True)
    estatura = models.PositiveIntegerField(null=True, blank=True, help_text="Estatura en cm")
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


class MedicionFisica(models.Model):
    """Historial de mediciones físicas del cliente."""
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='mediciones'
    )
    fecha = models.DateField()
    peso = models.DecimalField(max_digits=5, decimal_places=1, null=True, blank=True)
    masa_muscular = models.DecimalField(max_digits=5, decimal_places=1, null=True, blank=True)
    masa_grasa = models.DecimalField(max_digits=5, decimal_places=1, null=True, blank=True)

    class Meta:
        ordering = ['fecha']

    def __str__(self):
        return f"{self.user.username} - {self.fecha}"


class InbodyReport(models.Model):
    """Reporte InBody subido por el instructor para un cliente."""
    cliente = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='inbody_reports',
        limit_choices_to={'rol': 'cliente'},
    )
    instructor = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL, null=True, blank=True,
        related_name='inbody_reports_subidos',
        limit_choices_to={'rol': 'instructor'},
    )
    archivo = models.FileField(
        upload_to='inbody/',
        validators=[FileExtensionValidator(
            allowed_extensions=['csv', 'xlsx', 'xls']
        )],
    )
    fecha_test = models.DateField(help_text="Fecha del test InBody")

    # Métricas esenciales
    peso = models.DecimalField(max_digits=5, decimal_places=1, null=True, blank=True, help_text="kg")
    porcentaje_grasa = models.DecimalField(max_digits=4, decimal_places=1, null=True, blank=True, help_text="%")
    masa_muscular = models.DecimalField(max_digits=5, decimal_places=1, null=True, blank=True, help_text="kg, musculoesquelética")
    masa_grasa_kg = models.DecimalField(max_digits=5, decimal_places=1, null=True, blank=True, help_text="kg")
    imc = models.DecimalField(max_digits=4, decimal_places=1, null=True, blank=True, help_text="kg/m²")
    puntuacion_inbody = models.IntegerField(null=True, blank=True, help_text="/100")
    tasa_metabolica_basal = models.IntegerField(null=True, blank=True, help_text="kcal")
    agua_corporal = models.DecimalField(max_digits=4, decimal_places=1, null=True, blank=True, help_text="L")

    subido_en = models.DateTimeField(auto_now_add=True)
    actualizado = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-fecha_test', '-subido_en']

    def __str__(self):
        return f"InBody {self.cliente.username} - {self.fecha_test}"
