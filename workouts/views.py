from pyexpat.errors import messages
from django.contrib import messages
from .models import Workout, RoutineCompleted
from django.contrib.auth.decorators import login_required, user_passes_test
from django.shortcuts import render, redirect, get_object_or_404
from .forms import WorkoutForm, WorkoutMediaFormSet
from accounts.models import CustomUser
from workouts.models import Workout, WorkoutAssignment
from django.utils import timezone
from datetime import timedelta


def is_instructor(user):
    return getattr(user, "rol", None) == "instructor"

@login_required
def complete_routine(request, workout_id):
    workout = get_object_or_404(Workout, id=workout_id)

    # Evita duplicados
    already = RoutineCompleted.objects.filter(
        user=request.user,
        workout=workout
    ).exists()

    if not already:
        RoutineCompleted.objects.create(
            user=request.user,
            workout=workout
        )

    return redirect("detalle_rutina", id=workout.id)

@login_required
@user_passes_test(is_instructor)
def instructor_dashboard(request):

    # Rutinas del instructor
    workouts = Workout.objects.filter(instructor=request.user)

    # Clientes asignados a cualquier rutina del instructor
    asignaciones = WorkoutAssignment.objects.filter(
        workout__instructor=request.user
    ).select_related("cliente").distinct()

    clientes_asignados = [a.cliente for a in asignaciones]

    # Métricas
    total_clients = len(clientes_asignados)

    total_completadas = RoutineCompleted.objects.filter(
        workout__instructor=request.user
    ).count()

    completadas_7dias = RoutineCompleted.objects.filter(
        workout__instructor=request.user,
        completed_at__gte=timezone.now() - timedelta(days=7)
    ).count()

    return render(request, "dashboards/instructor/dashboard_instructor.html", {
        "workouts": workouts,
        "clientes_asignados": clientes_asignados,
        "total_clients": total_clients,
        "total_completadas": total_completadas,
        "completadas_7dias": completadas_7dias,
    })




@login_required
@user_passes_test(is_instructor)
def instructor_clientes(request):

    # todos los clientes que tengan rutinas asignadas por este instructor
    clientes_ids = WorkoutAssignment.objects.filter(
        workout__instructor=request.user
    ).values_list("cliente_id", flat=True).distinct()

    clientes = CustomUser.objects.filter(id__in=clientes_ids)

    return render(request, "dashboards/instructor/clientes_lista.html", {
        "clientes": clientes,
    })




@login_required
@user_passes_test(is_instructor)
def instructor_workout_create(request):
    """
    Pantalla PREMIUM para que el instructor cree una nueva rutina.
    """
    if request.method == "POST":
        form = WorkoutForm(request.POST)
        formset = WorkoutMediaFormSet(request.POST, request.FILES, prefix="media")

        if form.is_valid() and formset.is_valid():
            workout = form.save(commit=False)
            workout.instructor = request.user
            workout.save()

            medias = formset.save(commit=False)
            for media in medias:
                media.workout = workout
                media.save()

            # Objetos marcados para eliminar
            for obj in formset.deleted_objects:
                obj.delete()

            # Redirigir al DASHBOARD del instructor, NO al detalle de rutina
            return redirect("instructor_dashboard")

    else:
        form = WorkoutForm()
        formset = WorkoutMediaFormSet(prefix="media")

    return render(
        request,
        "dashboards/instructor/workout_create.html",  # <-- tu template correcto
        {"form": form, "formset": formset},
    )


@login_required
@user_passes_test(is_instructor)
def assign_workout(request, workout_id):
    workout = get_object_or_404(Workout, id=workout_id)

    # SOLO clientes
    clientes = CustomUser.objects.filter(rol="cliente")

    if request.method == "POST":
        cliente_id = request.POST.get("cliente")

        try:
            cliente = CustomUser.objects.get(id=cliente_id, rol="cliente")
        except CustomUser.DoesNotExist:
            messages.error(request, "Cliente no válido.")
            return redirect("instructor_dashboard")

        # Crear asignación
        WorkoutAssignment.objects.create(
            workout=workout,
            cliente=cliente
        )

        messages.success(request, f"Rutina asignada a {cliente.username}.")
        return redirect("instructor_dashboard")

    return render(
        request,
        "dashboards/instructor/assign_workout.html",
        {
            "workout": workout,
            "clientes": clientes,
        }
    )


