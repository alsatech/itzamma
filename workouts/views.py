from django.shortcuts import get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from .models import Workout, RoutineCompleted

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
