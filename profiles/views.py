from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import UserProfile
from .forms import UserProfileForm
from workouts.models import WorkoutAssignment
from workouts.models import Workout
from workouts.models import RoutineCompleted
from datetime import date, timedelta

@login_required
def completar_perfil(request):

    perfil, created = UserProfile.objects.get_or_create(user=request.user)

    if request.method == "POST":
        form = UserProfileForm(request.POST, instance=perfil)
        if form.is_valid():
            form.save()
            return redirect("dashboard_cliente")
    else:
        form = UserProfileForm(instance=perfil)

    return render(request, "profiles/perfil_form.html", {"form": form, "perfil": perfil})


@login_required
def dashboard_cliente(request):
    perfil = UserProfile.objects.filter(user=request.user).first()

    # Si no tiene perfil básico, mandarlo a completarlo
    if not perfil or not perfil.nombre:
        return redirect("completar_perfil")

    # 🔢 Aquí puedes calcular tus métricas reales
    # De momento uso valores de ejemplo (0–100)
    actividad = 70    # % actividad diaria
    fuerza = 55       # % fuerza/masa muscular
    constancia = 85   # % constancia/rutinas cumplidas
    rutinas_count = 5  # luego lo cambias por un count real

    contexto = {
        "perfil": perfil,
        "actividad": actividad,
        "fuerza": fuerza,
        "constancia": constancia,
        "rutinas_count": rutinas_count,
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

    media = workout.media.all().order_by("orden")

    video = media.filter(tipo="video").first()
    fotos = media.filter(tipo="foto")
    pdfs = media.filter(tipo="pdf")
    textos = media.filter(tipo="texto")

    return render(request, "dashboards/cliente/detalle_rutina.html", {
        "workout": workout,
        "video": video,
        "fotos": fotos,
        "pdfs": pdfs,
        "textos": textos,
    })



@login_required
def perfil(request):
    perfil = request.user.profile  # Ajusta si tu relación se llama diferente

    # Total completadas
    total_completed = RoutineCompleted.objects.filter(user=request.user).count()

    # Últimos 7 días
    last_week_completed = RoutineCompleted.objects.filter(
        user=request.user,
        completed_at__gte=date.today() - timedelta(days=7)
    ).count()

    return render(request, "dashboards/cliente/perfil.html", {
        "perfil": perfil,
        "total_completed": total_completed,
        "last_week_completed": last_week_completed,
    })

