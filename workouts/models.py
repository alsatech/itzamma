from django.db import models
from django.conf import settings
import re

User = settings.AUTH_USER_MODEL

DEPORTES = [
    ("gym",        "Gym"),
    ("futbol",     "Fútbol"),
    ("tenis",      "Tenis"),
    ("basketball", "Basketball"),
    ("natacion",   "Natación"),
    ("ciclismo",   "Ciclismo"),
    ("boxeo",      "Boxeo"),
    ("yoga",       "Yoga"),
    ("running",    "Running"),
    ("voleibol",   "Voleibol"),
    ("beisbol",    "Béisbol"),
    ("atletismo",  "Atletismo"),
    ("pingpong",   "Ping Pong"),
    ("otro",       "Otro"),
]

DEPORTE_EMOJIS = {
    "gym":        "🏋️",
    "futbol":     "⚽",
    "tenis":      "🎾",
    "basketball": "🏀",
    "natacion":   "🏊",
    "ciclismo":   "🚴",
    "boxeo":      "🥊",
    "yoga":       "🧘",
    "running":    "🏃",
    "voleibol":   "🏐",
    "beisbol":    "⚾",
    "atletismo":  "🎽",
    "pingpong":   "🏓",
    "otro":       "🏅",
}


class Ejercicio(models.Model):
    CATEGORIAS = [
        ("fuerza",    "Fuerza"),
        ("funcional", "Funcional"),
        ("potencia",  "Potencia"),
    ]

    instructor = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        limit_choices_to={'rol': 'instructor'},
        related_name='ejercicios'
    )
    nombre = models.CharField(max_length=200)
    categoria = models.CharField(max_length=20, choices=CATEGORIAS, default="fuerza")
    descripcion = models.TextField(blank=True)
    creado = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.nombre} ({self.get_categoria_display()})"


class EjercicioMedia(models.Model):
    TIPOS = [
        ('video', 'Video'),
        ('foto',  'Foto'),
    ]

    ejercicio = models.ForeignKey(Ejercicio, on_delete=models.CASCADE, related_name='media')
    tipo = models.CharField(max_length=10, choices=TIPOS, default='video')
    url_video = models.URLField(blank=True)
    imagen = models.ImageField(upload_to="ejercicios/fotos/", blank=True, null=True)
    orden = models.IntegerField(default=0)

    class Meta:
        ordering = ['orden']

    def __str__(self):
        return f"{self.ejercicio.nombre} - {self.tipo} ({self.orden})"

    def get_youtube_id(self):
        if not self.url_video:
            return None
        url = self.url_video.strip()
        for pattern in [r"v=([^&]+)", r"youtu\.be/([^?]+)", r"embed/([^?]+)", r"shorts/([^?]+)"]:
            match = re.search(pattern, url)
            if match:
                return match.group(1)
        return None


class Rutina(models.Model):
    instructor = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        limit_choices_to={'rol': 'instructor'},
        related_name='rutinas'
    )
    nombre = models.CharField(max_length=200)
    descripcion = models.TextField(blank=True)
    deporte = models.CharField(max_length=20, choices=DEPORTES, default="gym")
    creado = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.nombre

    @property
    def emoji(self):
        return DEPORTE_EMOJIS.get(self.deporte, "🏅")


class RutinaDia(models.Model):
    DIAS = [
        ('lunes',     'Lunes'),
        ('martes',    'Martes'),
        ('miercoles', 'Miércoles'),
        ('jueves',    'Jueves'),
        ('viernes',   'Viernes'),
        ('sabado',    'Sábado'),
        ('domingo',   'Domingo'),
    ]

    rutina = models.ForeignKey(Rutina, on_delete=models.CASCADE, related_name='dias')
    dia = models.CharField(max_length=20, choices=DIAS)
    orden = models.IntegerField(default=0)

    class Meta:
        ordering = ['orden']

    def __str__(self):
        return f"{self.rutina.nombre} - {self.get_dia_display()}"


class RutinaSeccion(models.Model):
    SECCIONES = [
        ('cardio',        'Subida de Frecuencia Cardiaca'),
        ('calentamiento', 'Calentamiento'),
        ('medular',       'Medular'),
        ('cierre',        'Cierre'),
    ]

    dia = models.ForeignKey(RutinaDia, on_delete=models.CASCADE, related_name='secciones')
    tipo = models.CharField(max_length=20, choices=SECCIONES)
    orden = models.IntegerField(default=0)

    class Meta:
        ordering = ['orden']

    def __str__(self):
        return f"{self.dia} - {self.get_tipo_display()}"


class RutinaEjercicio(models.Model):
    seccion = models.ForeignKey(RutinaSeccion, on_delete=models.CASCADE, related_name='ejercicios')
    ejercicio = models.ForeignKey(Ejercicio, on_delete=models.CASCADE)
    series = models.IntegerField(default=3)
    repeticiones = models.CharField(max_length=50, default="12")
    descanso = models.IntegerField(default=60)  # segundos
    porcentaje = models.IntegerField(null=True, blank=True)
    orden = models.IntegerField(default=0)

    class Meta:
        ordering = ['orden']

    def __str__(self):
        return f"{self.seccion} - {self.ejercicio.nombre}"


class RutinaAsignacion(models.Model):
    rutina = models.ForeignKey(Rutina, on_delete=models.CASCADE, related_name='asignaciones')
    cliente = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        limit_choices_to={'rol': 'cliente'},
        related_name='rutinas_asignadas'
    )
    fecha_asignacion = models.DateField(auto_now_add=True)

    def __str__(self):
        return f"{self.rutina.nombre} → {self.cliente.username}"


class RutinaCompletada(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='rutinas_completadas')
    rutina = models.ForeignKey(Rutina, on_delete=models.CASCADE, related_name='completadas_por')
    completed_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} completó {self.rutina.nombre}"


class MaximoEjercicio(models.Model):
    """Registro del peso máximo levantado en un ejercicio por el cliente."""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='maximos')
    ejercicio = models.ForeignKey(Ejercicio, on_delete=models.CASCADE, related_name='maximos')
    peso_kg = models.DecimalField(max_digits=6, decimal_places=1)
    fecha = models.DateField()

    class Meta:
        ordering = ['fecha']

    def __str__(self):
        return f"{self.user.username} - {self.ejercicio.nombre} - {self.peso_kg}kg"


class ProgressReport(models.Model):
    cliente = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        limit_choices_to={'rol': 'cliente'},
        related_name="reportes_cliente"
    )
    instructor = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        limit_choices_to={'rol': 'instructor'},
        related_name="reportes_instructor"
    )
    fecha = models.DateField(auto_now_add=True)
    comentario = models.TextField()
    calificacion = models.IntegerField(null=True, blank=True)

    def __str__(self):
        return f"Reporte {self.fecha} - {self.cliente.username}"
