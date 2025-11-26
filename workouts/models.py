from django.db import models
from django.conf import settings

User = settings.AUTH_USER_MODEL

class Workout(models.Model):
    instructor = models.ForeignKey(
        User, 
        on_delete=models.CASCADE, 
        limit_choices_to={'rol': 'instructor'}
    )
    titulo = models.CharField(max_length=200)
    descripcion = models.TextField(blank=True, null=True)
    video_url = models.URLField()
    creado = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.titulo


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
