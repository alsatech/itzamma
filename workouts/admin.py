from django.contrib import admin
from .models import Workout, WorkoutAssignment, ProgressReport, WorkoutMedia


@admin.register(Workout)
class WorkoutAdmin(admin.ModelAdmin):
    list_display = ("titulo", "instructor", "creado")
    search_fields = ("titulo", "instructor__username")
    autocomplete_fields = ("instructor",)


@admin.register(WorkoutMedia)
class WorkoutMediaAdmin(admin.ModelAdmin):
    list_display = ("workout", "tipo", "orden")
    list_filter = ("tipo",)
    search_fields = ("workout__titulo",)
    autocomplete_fields = ("workout",)


@admin.register(WorkoutAssignment)
class WorkoutAssignmentAdmin(admin.ModelAdmin):
    list_display = ("workout", "cliente", "fecha_asignacion")
    autocomplete_fields = ("workout", "cliente")


@admin.register(ProgressReport)
class ProgressReportAdmin(admin.ModelAdmin):
    list_display = ("cliente", "instructor", "fecha", "calificacion")
    list_filter = ("instructor", "fecha")
    search_fields = ("cliente__username", "instructor__username")
