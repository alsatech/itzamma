from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.utils.timezone import localdate
from datetime import date, timedelta

from .forms import UserProfileForm
from accounts.models import CustomUser, InstructorClient
import json
from django.core.serializers.json import DjangoJSONEncoder
from workouts.models import (
    RutinaAsignacion, RutinaCompletada, Rutina, ProgressReport,
    Ejercicio, MaximoEjercicio,
)
from .models import UserProfile, MedicionFisica


def is_instructor(user):
    return getattr(user, "rol", None) == "instructor"


@login_required
def detalle_rutina(request, assignment_id):
    assignment = get_object_or_404(
        RutinaAsignacion,
        id=assignment_id,
        cliente=request.user
    )
    rutina = assignment.rutina
    rutina_completada = RutinaCompletada.objects.filter(
        user=request.user,
        rutina=rutina
    ).exists()

    return render(request, "dashboards/cliente/detalle_rutina.html", {
        "rutina": rutina,
        "assignment": assignment,
        "rutina_completada": rutina_completada,
    })


@login_required
def completar_perfil(request):
    perfil, _ = UserProfile.objects.get_or_create(user=request.user)

    if request.method == "POST":
        form = UserProfileForm(request.POST, request.FILES, instance=perfil)
        if form.is_valid():
            form.save()
            return redirect("dashboard_cliente")
    else:
        form = UserProfileForm(instance=perfil)

    return render(request, "profiles/perfil_form.html", {"form": form, "perfil": perfil})


@login_required
def dashboard_cliente(request):
    perfil = UserProfile.objects.filter(user=request.user).first()

    if not perfil or not perfil.nombre:
        return redirect("completar_perfil")

    user = request.user

    asignaciones = RutinaAsignacion.objects.filter(
        cliente=user
    ).select_related("rutina")

    completadas = RutinaCompletada.objects.filter(user=user)

    completadas_semana = completadas.filter(
        completed_at__gte=date.today() - timedelta(days=7)
    )

    pendientes = [
        a for a in asignaciones
        if not completadas.filter(rutina=a.rutina).exists()
    ]

    total_semana = asignaciones.count()
    completadas_count = completadas_semana.count()
    progreso = int((completadas_count / total_semana) * 100) if total_semana > 0 else 0

    return render(request, "dashboards/cliente/dashboard_cliente.html", {
        "perfil": perfil,
        "asignaciones": asignaciones,
        "pendientes": pendientes,
        "completadas_semana": completadas_count,
        "total_semana": total_semana,
        "progreso": progreso,
        "historial": completadas.order_by("-completed_at")[:5],
    })


@login_required
def ver_rutinas(request):
    asignaciones = RutinaAsignacion.objects.filter(
        cliente=request.user
    ).select_related("rutina")

    return render(request, "dashboards/cliente/ver_rutinas.html", {
        "asignaciones": asignaciones
    })


@login_required
def rutinas_semana(request):
    today = localdate()
    start_week = today - timedelta(days=today.weekday())  # lunes

    # índice → nombre en RutinaDia.dia
    DIAS_KEY = ["lunes", "martes", "miercoles", "jueves", "viernes", "sabado", "domingo"]
    DIAS_DISPLAY = ["LUNES", "MARTES", "MIERCOLES", "JUEVES", "VIERNES", "SABADO", "DOMINGO"]

    assignments = (
        RutinaAsignacion.objects
        .filter(cliente=request.user)
        .select_related("rutina")
        .prefetch_related("rutina__dias")
    )

    completed_ids = set(
        RutinaCompletada.objects.filter(user=request.user)
        .values_list("rutina_id", flat=True)
    )

    week = []
    for i in range(7):
        day_date = start_week + timedelta(days=i)
        dia_key = DIAS_KEY[i]  # e.g. "jueves"

        # Mostrar rutinas que tienen ese día configurado
        day_assignments = [
            {
                "rutina": a.rutina,
                "assignment": a,
                "completed": a.rutina.id in completed_ids,
            }
            for a in assignments
            if a.rutina.dias.filter(dia=dia_key).exists()
        ]

        week.append({
            "date": day_date,
            "day_number": i + 1,
            "day": DIAS_DISPLAY[i],
            "is_today": day_date == today,
            "assignments": day_assignments,
            "is_rest": len(day_assignments) == 0,
        })

    return render(request, "dashboards/cliente/rutinas_semana.html", {
        "week_schedule": week
    })


@login_required
@user_passes_test(is_instructor)
def reportes_cliente(request, cliente_id):
    cliente = get_object_or_404(CustomUser, id=cliente_id, rol="cliente")

    if not InstructorClient.objects.filter(instructor=request.user, cliente=cliente).exists():
        messages.error(request, "No tienes permiso para ver reportes de este cliente.")
        return redirect("instructor_dashboard")

    reportes = ProgressReport.objects.filter(
        cliente=cliente,
        instructor=request.user
    ).order_by("-fecha")

    today = localdate()
    start_week = today - timedelta(days=today.weekday())
    end_week = start_week + timedelta(days=6)

    reporte_semana = ProgressReport.objects.filter(
        cliente=cliente,
        instructor=request.user,
        fecha__range=(start_week, end_week)
    ).exists()

    return render(request, "dashboards/instructor/reportes_cliente.html", {
        "cliente": cliente,
        "reportes": reportes,
        "start_week": start_week,
        "end_week": end_week,
        "reporte_semana": reporte_semana,
    })


@login_required
@user_passes_test(is_instructor)
def crear_reporte(request, cliente_id):
    cliente = get_object_or_404(CustomUser, id=cliente_id, rol="cliente")

    if not InstructorClient.objects.filter(instructor=request.user, cliente=cliente).exists():
        messages.error(request, "No tienes permiso para crear reportes de este cliente.")
        return redirect("instructor_dashboard")

    today = localdate()
    start_week = today - timedelta(days=today.weekday())
    end_week = start_week + timedelta(days=6)

    if ProgressReport.objects.filter(
        cliente=cliente,
        instructor=request.user,
        fecha__range=(start_week, end_week)
    ).exists():
        messages.warning(request, "Ya existe un reporte para esta semana.")
        return redirect("reportes_cliente", cliente_id=cliente.id)

    if request.method == "POST":
        comentario = (request.POST.get("comentario") or "").strip()
        calificacion_raw = request.POST.get("calificacion")
        try:
            calificacion = int(calificacion_raw)
        except (TypeError, ValueError):
            calificacion = None

        errores = []
        if not comentario:
            errores.append("El comentario es obligatorio.")
        if calificacion is None or not (1 <= calificacion <= 10):
            errores.append("La calificación debe ser un número del 1 al 10.")

        if errores:
            for e in errores:
                messages.error(request, e)
        else:
            ProgressReport.objects.create(
                cliente=cliente,
                instructor=request.user,
                comentario=comentario,
                calificacion=calificacion
            )
            messages.success(request, "Reporte creado correctamente.")
            return redirect("reportes_cliente", cliente_id=cliente.id)

    return render(request, "dashboards/instructor/reporte_form.html", {
        "cliente": cliente,
        "start_week": start_week,
        "end_week": end_week,
    })


@login_required
def perfil(request):
    perfil = request.user.profile

    completadas_total = RutinaCompletada.objects.filter(user=request.user).count()
    completadas_semana = RutinaCompletada.objects.filter(
        user=request.user,
        completed_at__gte=date.today() - timedelta(days=7)
    ).count()

    return render(request, "dashboards/cliente/perfil.html", {
        "perfil": perfil,
        "completadas_total": completadas_total,
        "completadas_semana": completadas_semana,
    })


@login_required
def suplementos(request):
    perfil = UserProfile.objects.filter(user=request.user).first()
    upsell = []
    if perfil and perfil.suplementos:
        texto = perfil.suplementos.lower()
        if any(k in texto for k in ['proteina', 'whey', 'caseina', 'protein']):
            upsell.append('proteinas')
        if any(k in texto for k in ['pre', 'preentreno', 'cafeina', 'energia', 'preworkout']):
            upsell.append('preentreno')
        if any(k in texto for k in ['creatina', 'creatine']):
            upsell.append('creatina')
        if any(k in texto for k in ['vitamina', 'zinc', 'omega', 'magnesio', 'vitamin']):
            upsell.append('vitaminas')
        if any(k in texto for k in ['aminoacido', 'bcaa', 'glutamina', 'leucina', 'amino']):
            upsell.append('aminoacidos')
    return render(request, "dashboards/cliente/suplementos.html", {'upsell': upsell})

@login_required
def suplementos_proteinas(request):
    return render(request, "dashboards/cliente/suplementos_proteinas.html")

@login_required
def suplementos_preentreno(request):
    return render(request, "dashboards/cliente/suplementos_preentreno.html")

@login_required
def suplementos_creatina(request):
    return render(request, "dashboards/cliente/suplementos_creatina.html")

@login_required
def suplementos_vitaminas(request):
    return render(request, "dashboards/cliente/suplementos_vitaminas.html")

@login_required
def suplementos_aminoacidos(request):
    return render(request, "dashboards/cliente/suplementos_aminoacidos.html")


@login_required
def graficas(request):
    user = request.user
    today = date.today()

    # ── Guardar nueva medición ──
    if request.method == "POST" and request.POST.get("action") == "medicion":
        MedicionFisica.objects.create(
            user=user,
            fecha=today,
            peso=request.POST.get("peso") or None,
            masa_muscular=request.POST.get("masa_muscular") or None,
            masa_grasa=request.POST.get("masa_grasa") or None,
        )
        return redirect("graficas")

    if request.method == "POST" and request.POST.get("action") == "maximo":
        ej_id = request.POST.get("ejercicio_id")
        peso_kg = request.POST.get("peso_kg")
        if ej_id and peso_kg:
            ejercicio = get_object_or_404(Ejercicio, id=ej_id)
            MaximoEjercicio.objects.create(
                user=user, ejercicio=ejercicio,
                peso_kg=peso_kg, fecha=today,
            )
        return redirect("graficas")

    # ── Datos para gráficas ──
    mediciones = list(MedicionFisica.objects.filter(user=user).values(
        'fecha', 'peso', 'masa_muscular', 'masa_grasa'
    ))

    # Ejercicios disponibles del instructor del cliente
    ejercicios = Ejercicio.objects.filter(
        rutinas__asignaciones__cliente=user
    ).distinct()

    # Máximos por ejercicio seleccionado
    ej_sel_id = request.GET.get("ejercicio")
    maximos = []
    ej_seleccionado = None
    if ej_sel_id:
        try:
            ej_seleccionado = ejercicios.get(id=ej_sel_id)
            maximos = list(MaximoEjercicio.objects.filter(
                user=user, ejercicio=ej_seleccionado
            ).values('fecha', 'peso_kg'))
        except Ejercicio.DoesNotExist:
            pass

    return render(request, "dashboards/cliente/graficas.html", {
        "mediciones_json": json.dumps(mediciones, cls=DjangoJSONEncoder),
        "maximos_json":    json.dumps(maximos,    cls=DjangoJSONEncoder),
        "ejercicios":      ejercicios,
        "ej_seleccionado": ej_seleccionado,
    })


@login_required
def masa_corporal(request):
    perfil = UserProfile.objects.filter(user=request.user).first()
    return render(request, "dashboards/cliente/masa_corporal.html", {
        "perfil": perfil,
    })
