from .models import Workout, RoutineCompleted
from django.contrib.auth.decorators import login_required, user_passes_test
from django.shortcuts import render, redirect, get_object_or_404
from .forms import WorkoutForm, WorkoutMediaFormSet

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

    return redirect("detalle_rutina", workout_id=workout.id)

@login_required
@user_passes_test(is_instructor)
def instructor_dashboard(request):
    # Rutinas creadas por este instructor
    workouts = Workout.objects.filter(instructor=request.user)

    total_workouts = workouts.count()

    # Total de clientes (si luego quieres limitar a clientes asignados, lo ajustamos)
    from accounts.models import CustomUser
    total_clients = CustomUser.objects.filter(rol="cliente").count()

    return render(
        request,
        "dashboards/instructor/dashboard_instructor.html",
        {
            "workouts": workouts,
            "total_workouts": total_workouts,
            "total_clients": total_clients,
        }
    )



@login_required
@user_passes_test(is_instructor)
def instructor_workout_create(request):
    """
    Pantalla PREMIUM para que el instructor cree una nueva rutina,
    con posibilidad de añadir distintos tipos de media.
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

            # Si el usuario marcó algunos para borrar
            for obj in formset.deleted_objects:
                obj.delete()

            # De momento lo mandamos a detalle_rutina del cliente
            return redirect("detalle_rutina", id=workout.id)
    else:
        form = WorkoutForm()
        formset = WorkoutMediaFormSet(prefix="media")

    return render(
        request,
        "dashboards/instructor/workout_create.html",
        {
            "form": form,
            "formset": formset,
        },
    )

@login_required
@user_passes_test(is_instructor)
def assign_workout(request, workout_id):
    from accounts.models import CustomUser
    from .models import WorkoutAssignment

    workout = get_object_or_404(Workout, id=workout_id)

    # Lista de clientes
    clients = CustomUser.objects.filter(rol="cliente")

    if request.method == "POST":
        client_id = request.POST.get("client_id")
        client = get_object_or_404(CustomUser, id=client_id)

        # Evita asignaciones duplicadas
        exists = WorkoutAssignment.objects.filter(
            workout=workout,
            cliente=client
        ).exists()

        if not exists:
            WorkoutAssignment.objects.create(
                workout=workout,
                cliente=client
            )

        return redirect("instructor_dashboard")

    return render(
        request,
        "dashboards/instructor/assign_workout.html",
        {
            "workout": workout,
            "clients": clients,
        }
    )
