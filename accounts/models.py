from django.contrib.auth.models import AbstractUser
from django.db import models

class Roles(models.TextChoices):
    CLIENTE = "cliente", "Cliente"
    INSTRUCTOR = "instructor", "Instructor"
    SUPERADMIN = "superadmin", "Super Admin"


class CustomUser(AbstractUser):
    telefono = models.CharField(max_length=20, blank=True, null=True)
    foto = models.ImageField(upload_to="usuarios/", blank=True, null=True)
    rol = models.CharField(
        max_length=20,
        choices=Roles.choices,
        default=Roles.CLIENTE
    )

    def __str__(self):
        return self.username


class InstructorProfile(models.Model):
    user = models.OneToOneField(
        CustomUser, 
        on_delete=models.CASCADE,
        limit_choices_to={'rol': 'instructor'},
        related_name="instructor_profile"
    )
    deporte = models.CharField(max_length=100)
    biografia = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.user.username


class ClientProfile(models.Model):
    user = models.OneToOneField(
        CustomUser, 
        on_delete=models.CASCADE,
        limit_choices_to={'rol': 'cliente'},
        related_name="client_profile"
    )
    fecha_inicio = models.DateField(auto_now_add=True)

    def __str__(self):
        return self.user.username


class Workout(models.Model):
    instructor = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE,
        limit_choices_to={'rol': 'instructor'},
        related_name="workouts"
    )
    titulo = models.CharField(max_length=200)
    descripcion = models.TextField(blank=True, null=True)
    video_url = models.URLField()
    creado = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.titulo


class WorkoutAssignment(models.Model):
    workout = models.ForeignKey(
        Workout,
        on_delete=models.CASCADE,
        related_name="asignaciones"
    )
    cliente = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE,
        limit_choices_to={'rol': 'cliente'},
        related_name="workouts_asignados"
    )
    fecha_asignacion = models.DateField(auto_now_add=True)

    def __str__(self):
        return f"{self.workout.titulo} asignado a {self.cliente.username}"
