from django.contrib import admin
from .models import (
    Ejercicio, EjercicioMedia,
    Rutina, RutinaDia, RutinaSeccion, RutinaEjercicio,
    RutinaAsignacion, RutinaCompletada, ProgressReport, MaximoEjercicio,
)


@admin.register(Ejercicio)
class EjercicioAdmin(admin.ModelAdmin):
    list_display = ("nombre", "categoria", "instructor", "creado")
    list_filter = ("categoria",)
    search_fields = ("nombre", "instructor__username")


@admin.register(EjercicioMedia)
class EjercicioMediaAdmin(admin.ModelAdmin):
    list_display = ("ejercicio", "tipo", "orden")
    list_filter = ("tipo",)


@admin.register(Rutina)
class RutinaAdmin(admin.ModelAdmin):
    list_display = ("nombre", "deporte", "instructor", "creado")
    list_filter = ("deporte",)
    search_fields = ("nombre", "instructor__username")


@admin.register(RutinaDia)
class RutinaDiaAdmin(admin.ModelAdmin):
    list_display = ("rutina", "dia", "orden")


@admin.register(RutinaSeccion)
class RutinaSeccionAdmin(admin.ModelAdmin):
    list_display = ("dia", "tipo", "orden")


@admin.register(RutinaEjercicio)
class RutinaEjercicioAdmin(admin.ModelAdmin):
    list_display = ("seccion", "ejercicio", "series", "repeticiones", "descanso")


@admin.register(RutinaAsignacion)
class RutinaAsignacionAdmin(admin.ModelAdmin):
    list_display = ("rutina", "cliente", "fecha_asignacion")


@admin.register(RutinaCompletada)
class RutinaCompletadaAdmin(admin.ModelAdmin):
    list_display = ("user", "rutina", "completed_at")


@admin.register(MaximoEjercicio)
class MaximoEjercicioAdmin(admin.ModelAdmin):
    list_display = ("user", "ejercicio", "peso_kg", "fecha")


@admin.register(ProgressReport)
class ProgressReportAdmin(admin.ModelAdmin):
    list_display = ("cliente", "instructor", "fecha", "calificacion")
    list_filter = ("instructor", "fecha")
    search_fields = ("cliente__username", "instructor__username")
