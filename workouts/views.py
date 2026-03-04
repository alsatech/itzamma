import json
from django.contrib import messages
from django.contrib.auth.decorators import login_required, user_passes_test
from django.http import JsonResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.utils import timezone
from datetime import timedelta

from accounts.models import CustomUser, InstructorClient
from profiles.models import UserProfile
from .forms import EjercicioForm, EjercicioMediaFormSet, RutinaForm
from .models import (
    Ejercicio, EjercicioMedia,
    Rutina, RutinaDia, RutinaSeccion, RutinaEjercicio,
    RutinaAsignacion, RutinaCompletada,
)


def is_instructor(user):
    return getattr(user, "rol", None) == "instructor"


@login_required
def complete_rutina(request, assignment_id):
    assignment = get_object_or_404(RutinaAsignacion, id=assignment_id, cliente=request.user)
    RutinaCompletada.objects.get_or_create(user=request.user, rutina=assignment.rutina)
    return redirect("detalle_rutina", assignment_id=assignment_id)


# ── DASHBOARD ───────────────────────────────────────────────────────────────

@login_required
@user_passes_test(is_instructor)
def instructor_dashboard(request):
    rutinas = Rutina.objects.filter(instructor=request.user)
    clientes_asignados = CustomUser.objects.filter(
        mi_instructor__instructor=request.user
    )
    total_clients = clientes_asignados.count()
    total_ejercicios = Ejercicio.objects.filter(instructor=request.user).count()

    total_completadas = RutinaCompletada.objects.filter(
        rutina__instructor=request.user
    ).count()
    completadas_7dias = RutinaCompletada.objects.filter(
        rutina__instructor=request.user,
        completed_at__gte=timezone.now() - timedelta(days=7)
    ).count()

    return render(request, "dashboards/instructor/dashboard_instructor.html", {
        "rutinas": rutinas,
        "clientes_asignados": clientes_asignados,
        "total_clients": total_clients,
        "total_ejercicios": total_ejercicios,
        "total_completadas": total_completadas,
        "completadas_7dias": completadas_7dias,
    })


@login_required
@user_passes_test(is_instructor)
def instructor_perfil(request):
    total_clients = CustomUser.objects.filter(
        mi_instructor__instructor=request.user
    ).count()
    total_rutinas = Rutina.objects.filter(instructor=request.user).count()
    total_completadas = RutinaCompletada.objects.filter(
        rutina__instructor=request.user
    ).count()
    completadas_7dias = RutinaCompletada.objects.filter(
        rutina__instructor=request.user,
        completed_at__gte=timezone.now() - timedelta(days=7)
    ).count()

    return render(request, "dashboards/instructor/perfil_instructor.html", {
        "total_clients": total_clients,
        "total_workouts": total_rutinas,
        "total_completadas": total_completadas,
        "completadas_7dias": completadas_7dias,
    })


@login_required
@user_passes_test(is_instructor)
def instructor_clientes(request):
    clientes = CustomUser.objects.filter(
        mi_instructor__instructor=request.user
    )
    return render(request, "dashboards/instructor/clientes_lista.html", {
        "clientes": clientes,
    })


@login_required
@user_passes_test(is_instructor)
def instructor_cliente_detalle(request, cliente_id):
    cliente = get_object_or_404(CustomUser, id=cliente_id, rol="cliente")

    if not InstructorClient.objects.filter(instructor=request.user, cliente=cliente).exists():
        messages.error(request, "No tienes acceso a este cliente.")
        return redirect("instructor_dashboard")

    perfil = get_object_or_404(UserProfile, user=cliente)

    rutinas_asignadas = RutinaAsignacion.objects.filter(
        cliente=cliente,
        rutina__instructor=request.user
    ).select_related("rutina")

    rutinas_completadas = RutinaCompletada.objects.filter(
        user=cliente,
        rutina__instructor=request.user
    ).select_related("rutina")

    total_completadas = rutinas_completadas.count()
    ultimos_7_dias = rutinas_completadas.filter(
        completed_at__gte=timezone.now() - timedelta(days=7)
    ).count()

    return render(request, "dashboards/instructor/cliente_detalle.html", {
        "cliente": cliente,
        "perfil": perfil,
        "rutinas_asignadas": rutinas_asignadas,
        "rutinas_completadas": rutinas_completadas,
        "total_completadas": total_completadas,
        "ultimos_7_dias": ultimos_7_dias,
    })


# ── EJERCICIOS ───────────────────────────────────────────────────────────────

@login_required
@user_passes_test(is_instructor)
def ejercicio_list(request):
    cat = request.GET.get("cat", "")
    qs = Ejercicio.objects.filter(instructor=request.user)
    if cat:
        qs = qs.filter(categoria=cat)
    return render(request, "dashboards/instructor/ejercicio_list.html", {
        "ejercicios": qs,
        "cat_activa": cat,
    })


@login_required
@user_passes_test(is_instructor)
def ejercicio_create(request):
    if request.method == "POST":
        form = EjercicioForm(request.POST)
        formset = EjercicioMediaFormSet(request.POST, request.FILES, prefix="media")

        if form.is_valid() and formset.is_valid():
            ejercicio = form.save(commit=False)
            ejercicio.instructor = request.user
            ejercicio.save()

            medias = formset.save(commit=False)
            for i, media in enumerate(medias):
                media.ejercicio = ejercicio
                media.orden = i
                media.save()
            for obj in formset.deleted_objects:
                obj.delete()

            messages.success(request, f"Ejercicio '{ejercicio.nombre}' creado.")
            return redirect("ejercicio_list")
    else:
        form = EjercicioForm()
        formset = EjercicioMediaFormSet(prefix="media")

    return render(request, "dashboards/instructor/ejercicio_create.html", {
        "form": form,
        "formset": formset,
    })


@login_required
@user_passes_test(is_instructor)
def ejercicio_delete(request, id):
    ejercicio = get_object_or_404(Ejercicio, id=id, instructor=request.user)
    if request.method == "POST":
        ejercicio.delete()
        messages.success(request, "Ejercicio eliminado.")
    return redirect("ejercicio_list")


@login_required
@user_passes_test(is_instructor)
def ejercicios_json(request):
    """API endpoint: devuelve ejercicios del instructor filtrados por categoría."""
    cat = request.GET.get("cat", "")
    qs = Ejercicio.objects.filter(instructor=request.user)
    if cat:
        qs = qs.filter(categoria=cat)
    data = [
        {
            "id": e.id,
            "nombre": e.nombre,
            "categoria": e.categoria,
            "categoria_display": e.get_categoria_display(),
        }
        for e in qs
    ]
    return JsonResponse(data, safe=False)


# ── RUTINAS ──────────────────────────────────────────────────────────────────

@login_required
@user_passes_test(is_instructor)
def rutina_list(request):
    rutinas = Rutina.objects.filter(instructor=request.user).prefetch_related("dias")
    return render(request, "dashboards/instructor/rutina_list.html", {
        "rutinas": rutinas,
    })


@login_required
@user_passes_test(is_instructor)
def rutina_create(request):
    if request.method == "POST":
        try:
            payload = json.loads(request.body)
        except json.JSONDecodeError:
            return JsonResponse({"error": "JSON inválido"}, status=400)

        nombre = payload.get("nombre", "").strip()
        descripcion = payload.get("descripcion", "").strip()
        deporte = payload.get("deporte", "gym")
        dias_data = payload.get("dias", [])

        if not nombre:
            return JsonResponse({"error": "El nombre es requerido"}, status=400)

        rutina = Rutina.objects.create(
            instructor=request.user,
            nombre=nombre,
            descripcion=descripcion,
            deporte=deporte,
        )

        for dia_ord, dia_info in enumerate(dias_data):
            dia_obj = RutinaDia.objects.create(
                rutina=rutina,
                dia=dia_info["dia"],
                orden=dia_ord,
            )
            for sec_ord, sec_info in enumerate(dia_info.get("secciones", [])):
                sec_obj = RutinaSeccion.objects.create(
                    dia=dia_obj,
                    tipo=sec_info["tipo"],
                    orden=sec_ord,
                )
                for ej_ord, ej_info in enumerate(sec_info.get("ejercicios", [])):
                    ejercicio = get_object_or_404(
                        Ejercicio, id=ej_info["ejercicio_id"], instructor=request.user
                    )
                    RutinaEjercicio.objects.create(
                        seccion=sec_obj,
                        ejercicio=ejercicio,
                        series=ej_info.get("series", 3),
                        repeticiones=str(ej_info.get("repeticiones", "12")),
                        descanso=ej_info.get("descanso", 60),
                        porcentaje=ej_info.get("porcentaje") or None,
                        orden=ej_ord,
                    )

        return JsonResponse({"ok": True, "rutina_id": rutina.id})

    # GET
    form = RutinaForm()
    return render(request, "dashboards/instructor/rutina_create.html", {"form": form})


@login_required
@user_passes_test(is_instructor)
def rutina_detail(request, id):
    rutina = get_object_or_404(Rutina, id=id, instructor=request.user)
    dias = rutina.dias.prefetch_related(
        "secciones__ejercicios__ejercicio__media"
    )
    return render(request, "dashboards/instructor/rutina_detail.html", {
        "rutina": rutina,
        "dias": dias,
    })


@login_required
@user_passes_test(is_instructor)
def rutina_assign(request, id):
    rutina = get_object_or_404(Rutina, id=id, instructor=request.user)
    clientes = CustomUser.objects.filter(mi_instructor__instructor=request.user)

    if request.method == "POST":
        cliente_ids = request.POST.getlist("clientes")
        for cid in cliente_ids:
            try:
                cliente = CustomUser.objects.get(id=cid, rol="cliente")
                if InstructorClient.objects.filter(
                    instructor=request.user, cliente=cliente
                ).exists():
                    RutinaAsignacion.objects.get_or_create(
                        rutina=rutina, cliente=cliente
                    )
            except CustomUser.DoesNotExist:
                pass
        messages.success(request, "Rutina asignada correctamente.")
        return redirect("rutina_detail", id=rutina.id)

    return render(request, "dashboards/instructor/rutina_assign.html", {
        "rutina": rutina,
        "clientes": clientes,
    })
