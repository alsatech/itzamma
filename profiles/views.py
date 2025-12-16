from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from .models import UserProfile
from .forms import UserProfileForm
from workouts.models import WorkoutAssignment
from workouts.models import Workout
from workouts.models import RoutineCompleted
from datetime import date, timedelta
from django.contrib.auth.decorators import login_required, user_passes_test
from accounts.models import CustomUser

@login_required
def detalle_rutina(request, id):
    workout = get_object_or_404(Workout, id=id)

    # Determinar si la rutina YA está completada por el usuario
    rutina_completada = RoutineCompleted.objects.filter(
        user=request.user,
        workout=workout
    ).exists()

    # Por si usas videos relacionados
    video = workout.media.first() if hasattr(workout, "media") else None

    return render(request, "dashboards/cliente/detalle_rutina.html", {
        "workout": workout,
        "video": video,
        "rutina_completada": rutina_completada,
    })


from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from .models import UserProfile
from .forms import UserProfileForm

@login_required
def completar_perfil(request):
    perfil, created = UserProfile.objects.get_or_create(user=request.user)

    if request.method == "POST":
        form = UserProfileForm(
            request.POST,
            request.FILES,
            instance=perfil
        )
        if form.is_valid():
            form.save()
            return redirect("dashboard_cliente")
        # opcional: si quieres ver en consola qué está fallando
        # print(form.errors)

    else:
        form = UserProfileForm(instance=perfil)

    return render(
        request,
        "profiles/perfil_form.html",
        {"form": form, "perfil": perfil}
    )



@login_required
def dashboard_cliente(request):
    perfil = UserProfile.objects.filter(user=request.user).first()

    # Si no tiene perfil básico completado → redirigir
    if not perfil or not perfil.nombre:
        return redirect("completar_perfil")

    user = request.user
    # 🔹 Rutinas asignadas al usuario
    asignaciones = WorkoutAssignment.objects.filter(cliente=user)
    # 🔹 Rutinas completadas (últimos 7 días)
    completadas = RoutineCompleted.objects.filter(user=user)

    completadas_semana = completadas.filter(
        completed_at__gte=date.today() - timedelta(days=7)
    )
    # 🔹 Rutinas pendientes
    pendientes = [
        a for a in asignaciones if not completadas.filter(workout=a.workout).exists()
    ]

    # 🔹 Progreso semanal (0–100)
    total_semana = asignaciones.count()
    completadas_count = completadas_semana.count()

    if total_semana > 0:
        progreso = int((completadas_count / total_semana) * 100)
    else:
        progreso = 0

    contexto = {
        "perfil": perfil,
        "pendientes": pendientes,
        "completadas_semana": completadas_count,
        "total_semana": total_semana,
        "progreso": progreso,
        "historial": completadas.order_by("-completed_at")[:5],  # últimas 5
    }
    return render(request, "dashboards/cliente/dashboard_cliente.html", contexto)



@login_required
def ver_rutinas(request):
    asignaciones = WorkoutAssignment.objects.filter(cliente=request.user).select_related("workout")

    return render(request, "dashboards/cliente/ver_rutinas.html", {
        "asignaciones": asignaciones
    })


@login_required
def detalle_rutina(request, id):
    workout = get_object_or_404(Workout, id=id)

    # Determinar si la rutina YA está completada por el usuario
    rutina_completada = RoutineCompleted.objects.filter(
        user=request.user,
        workout=workout
    ).exists()

    video = workout.media.filter(tipo="video").first()

    return render(request, "dashboards/cliente/detalle_rutina.html", {
        "workout": workout,
        "video": video,
        "rutina_completada": rutina_completada,
    })



def is_instructor(user):
    return getattr(user, "rol", None) == "instructor"


@login_required
@user_passes_test(is_instructor)
def instructor_cliente_detalle(request, cliente_id):

    cliente = get_object_or_404(CustomUser, id=cliente_id, rol="cliente")

    # Rutinas asignadas por el instructor
    asignadas = WorkoutAssignment.objects.filter(
        cliente=cliente,
        workout__instructor=request.user
    ).select_related("workout")

    # Rutinas completadas por el cliente
    completadas = RoutineCompleted.objects.filter(
        user=cliente,
        workout__instructor=request.user
    ).select_related("workout")

    # Últimos 7 días
    semana = completadas.filter(
        completed_at__gte=date.today() - timedelta(days=7)
    )

    contexto = {
        "cliente": cliente,
        "asignadas": asignadas,
        "completadas": completadas,
        "completadas_semana": semana.count(),
    }

    return render(request, "dashboards/instructor/cliente_detalle.html", contexto)



@login_required
def perfil(request):
    perfil = request.user.profile  # Ajusta si tu relación se llama diferente

    # 🔢 Total de rutinas completadas
    completadas_total = RoutineCompleted.objects.filter(
        user=request.user
    ).count()

    # 📅 Rutinas completadas en los últimos 7 días
    completadas_semana = RoutineCompleted.objects.filter(
        user=request.user,
        completed_at__gte=date.today() - timedelta(days=7)
    ).count()

    return render(request, "dashboards/cliente/perfil.html", {
        "perfil": perfil,
        "completadas_total": completadas_total,
        "completadas_semana": completadas_semana,
    })

