from django.db import models
from django.conf import settings
import re


User = settings.AUTH_USER_MODEL

class Workout(models.Model):
    instructor = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        limit_choices_to={'rol': 'instructor'}
    )
    titulo = models.CharField(max_length=200)
    descripcion = models.TextField(blank=True, null=True)
    creado = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.titulo



class WorkoutMedia(models.Model):

    class MediaType(models.TextChoices):
        VIDEO = "video", "Video"
        PDF = "pdf", "PDF"
        TEXTO = "texto", "Texto"
        FOTO = "foto", "Foto"

    workout = models.ForeignKey(
        Workout,
        on_delete=models.CASCADE,
        related_name="media"
    )

    tipo = models.CharField(max_length=10, choices=MediaType.choices)

    url_video = models.URLField(blank=True, null=True)
    archivo_pdf = models.FileField(upload_to="workouts/pdfs/", blank=True, null=True)
    texto = models.TextField(blank=True, null=True)
    imagen = models.ImageField(upload_to="workouts/fotos/", blank=True, null=True)

    orden = models.IntegerField(default=0)

    def __str__(self):
        return f"{self.workout.titulo} - {self.tipo} ({self.orden})"

    def get_youtube_id(self):
        if not self.url_video:
            return None

        url = self.url_video.strip()

        # watch?v=VIDEOID
        match = re.search(r"v=([^&]+)", url)
        if match:
            return match.group(1)

        # youtu.be/VIDEOID
        match = re.search(r"youtu\.be/([^?]+)", url)
        if match:
            return match.group(1)

        # embed/VIDEOID
        match = re.search(r"embed/([^?]+)", url)
        if match:
            return match.group(1)

        # shorts/VIDEOID
        match = re.search(r"shorts/([^?]+)", url)
        if match:
            return match.group(1)

        return None




class WorkoutAssignment(models.Model):
    workout = models.ForeignKey(Workout, on_delete=models.CASCADE)
    cliente = models.ForeignKey(
        User, 
        on_delete=models.CASCADE, 
        limit_choices_to={'rol': 'cliente'}
    )
    fecha_asignacion = models.DateField(auto_now_add=True)

    def __str__(self):
        return f"{self.workout.titulo} → {self.cliente.username}"


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

class RoutineCompleted(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="completed_routines"
    )
    workout = models.ForeignKey(
        Workout,
        on_delete=models.CASCADE,
        related_name="completed_by"
    )
    completed_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} completed {self.workout.titulo}"
