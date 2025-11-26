from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .models import UserProfile
from .forms import UserProfileForm
from workouts.models import WorkoutAssignment
from workouts.models import Workout

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
    workout = Workout.objects.get(id=id)
    
    return render(request, "dashboards/cliente/detalle_rutina.html", {
        "workout": workout
    })

