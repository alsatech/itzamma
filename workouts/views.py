import json
from django.contrib import messages
from django.contrib.auth.decorators import login_required, user_passes_test
from django.http import JsonResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.utils import timezone
from datetime import timedelta, date

from accounts.models import CustomUser, InstructorClient
from profiles.models import UserProfile
from .forms import EjercicioForm, EjercicioMediaFormSet, RutinaForm
from .models import (
    Ejercicio, EjercicioMedia,
    Rutina, RutinaDia, RutinaSeccion, RutinaEjercicio,
    RutinaAsignacion, RutinaCompletada, RutinaCalendario,
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

    rutinas_completadas = RutinaCompletada.objects.filter(
        user=cliente,
        rutina__instructor=request.user
    ).select_related("rutina").order_by("-completed_at")

    total_completadas = rutinas_completadas.count()
    ultimos_7_dias = rutinas_completadas.filter(
        completed_at__gte=timezone.now() - timedelta(days=7)
    ).count()

    # ── Semana actual (lunes → domingo) ──────────────────────────
    today = date.today()
    week_start = today - timedelta(days=today.weekday())
    week_end   = week_start + timedelta(days=6)

    calendario_qs = RutinaCalendario.objects.filter(
        instructor=request.user,
        clientes=cliente,
        fecha__range=[week_start, week_end],
    ).select_related("rutina")
    cal_por_fecha = {c.fecha: c for c in calendario_qs}

    completadas_set = set(
        RutinaCompletada.objects.filter(
            user=cliente,
            rutina__instructor=request.user,
            completed_at__date__range=[week_start, week_end],
        ).values_list("rutina_id", "completed_at__date")
    )

    dia_nombres  = ["Lunes", "Martes", "Miércoles", "Jueves", "Viernes", "Sábado", "Domingo"]
    dia_abrevs   = ["Lun",   "Mar",    "Mié",        "Jue",    "Vie",     "Sáb",    "Dom"]

    semana = []
    for i in range(7):
        fecha = week_start + timedelta(days=i)
        cal   = cal_por_fecha.get(fecha)
        semana.append({
            "fecha":      fecha,
            "dia":        dia_nombres[i],
            "dia_abbr":   dia_abrevs[i],
            "calendario": cal,
            "completada": (cal.rutina_id, fecha) in completadas_set if cal else False,
            "es_hoy":     fecha == today,
            "pasado":     fecha < today,
        })

    return render(request, "dashboards/instructor/cliente_detalle.html", {
        "cliente":             cliente,
        "perfil":              perfil,
        "rutinas_completadas": rutinas_completadas,
        "total_completadas":   total_completadas,
        "ultimos_7_dias":      ultimos_7_dias,
        "semana":              semana,
        "week_start":          week_start,
        "week_end":            week_end,
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


# ── PLANIFICAR SEMANA (flujo unificado: construir + asignar) ──────────────────

_DIA_NOMBRES = {
    'lunes': 'Lunes', 'martes': 'Martes', 'miercoles': 'Miércoles',
    'jueves': 'Jueves', 'viernes': 'Viernes', 'sabado': 'Sábado', 'domingo': 'Domingo',
}

_DAY_ORDER = {'lunes': 0, 'martes': 1, 'miercoles': 2, 'jueves': 3,
              'viernes': 4, 'sabado': 5, 'domingo': 6}


@login_required
@user_passes_test(is_instructor)
def planificar_semana(request):
    """Flujo unificado: construye los días con ejercicios Y asigna a clientes."""
    if request.method == "POST":
        try:
            payload = json.loads(request.body)
        except json.JSONDecodeError:
            return JsonResponse({"error": "JSON inválido"}, status=400)

        cliente_ids = payload.get("cliente_ids", [])
        dias_data   = payload.get("dias", {})   # {dia_key: [secciones]}

        if not cliente_ids:
            return JsonResponse({"error": "Selecciona al menos un cliente"}, status=400)

        clientes_sel = CustomUser.objects.filter(
            id__in=cliente_ids,
            mi_instructor__instructor=request.user,
        )

        today      = date.today()
        week_start = today - timedelta(days=today.weekday())
        dias_creados = 0

        for dia_key, secciones_data in dias_data.items():
            if dia_key not in _DIA_NOMBRES or not secciones_data:
                continue

            # Secciones sin ejercicios → ignorar ese día
            total_ej = sum(len(s.get("ejercicios", [])) for s in secciones_data)
            if total_ej == 0:
                continue

            rutina = Rutina.objects.create(
                instructor=request.user,
                nombre=f"Rutina {_DIA_NOMBRES[dia_key]}",
                deporte="gym",
            )
            dia_obj = RutinaDia.objects.create(
                rutina=rutina, dia=dia_key, orden=0
            )

            for sec_ord, sec_info in enumerate(secciones_data):
                sec_obj = RutinaSeccion.objects.create(
                    dia=dia_obj, tipo=sec_info["tipo"], orden=sec_ord
                )
                # Agrupar ejercicios consecutivos con mismo grupo_tipo no-individual
                grupo_contador = 0
                prev_grupo = None
                for ej_ord, ej_info in enumerate(sec_info.get("ejercicios", [])):
                    ejercicio = get_object_or_404(
                        Ejercicio, id=ej_info["ejercicio_id"], instructor=request.user
                    )
                    grupo_tipo = ej_info.get("grupo_tipo", "individual") or "individual"
                    if grupo_tipo == "individual":
                        grupo_indice = 0
                        prev_grupo = None
                    else:
                        if grupo_tipo != prev_grupo:
                            grupo_contador += 1
                            prev_grupo = grupo_tipo
                        grupo_indice = grupo_contador

                    RutinaEjercicio.objects.create(
                        seccion=sec_obj,
                        ejercicio=ejercicio,
                        series=ej_info.get("series", 3),
                        repeticiones=str(ej_info.get("repeticiones", "12")),
                        descanso=60,
                        orden=ej_ord,
                        tiempo=ej_info.get("tiempo", "") or "",
                        intensidad=ej_info.get("intensidad", "") or "",
                        velocidad=ej_info.get("velocidad", "") or "",
                        grupo_tipo=grupo_tipo,
                        grupo_indice=grupo_indice,
                    )

            fecha = week_start + timedelta(days=_DAY_ORDER[dia_key])
            for cliente in clientes_sel:
                RutinaAsignacion.objects.get_or_create(rutina=rutina, cliente=cliente)
                entrada, _ = RutinaCalendario.objects.get_or_create(
                    instructor=request.user, rutina=rutina, fecha=fecha
                )
                entrada.clientes.add(cliente)

            dias_creados += 1

        if dias_creados == 0:
            return JsonResponse({"error": "Agrega ejercicios a al menos un día"}, status=400)

        n = clientes_sel.count()
        return JsonResponse({
            "ok": True,
            "message": f"Semana creada y asignada a {n} cliente{'s' if n != 1 else ''} · {dias_creados} días",
        })

    # GET
    ejercicios = Ejercicio.objects.filter(instructor=request.user)
    clientes   = CustomUser.objects.filter(mi_instructor__instructor=request.user)

    day_rows = [
        ("lunes",     "Lunes",     "Lun"),
        ("martes",    "Martes",    "Mar"),
        ("miercoles", "Miércoles", "Mié"),
        ("jueves",    "Jueves",    "Jue"),
        ("viernes",   "Viernes",   "Vie"),
        ("sabado",    "Sábado",    "Sáb"),
        ("domingo",   "Domingo",   "Dom"),
    ]

    return render(request, "dashboards/instructor/planificar_semana.html", {
        "ejercicios_json": json.dumps([
            {"id": e.id, "nombre": e.nombre,
             "categoria": e.categoria, "categoria_display": e.get_categoria_display()}
            for e in ejercicios
        ]),
        "clientes":  clientes,
        "day_rows":  day_rows,
    })

@login_required
@user_passes_test(is_instructor)
def crear_semana(request):
    if request.method == "POST":
        try:
            payload = json.loads(request.body)
        except json.JSONDecodeError:
            return JsonResponse({"error": "JSON inválido"}, status=400)

        dia = payload.get("dia", "").strip()
        secciones_data = payload.get("secciones", [])

        if dia not in _DIA_NOMBRES:
            return JsonResponse({"error": "Día inválido"}, status=400)

        nombre = f"Rutina {_DIA_NOMBRES[dia]}"

        rutina = Rutina.objects.create(
            instructor=request.user,
            nombre=nombre,
            deporte="gym",
        )

        dia_obj = RutinaDia.objects.create(rutina=rutina, dia=dia, orden=0)

        for sec_ord, sec_info in enumerate(secciones_data):
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
                    orden=ej_ord,
                )

        return JsonResponse({"ok": True, "rutina_id": rutina.id, "nombre": nombre})

    # GET
    ejercicios = Ejercicio.objects.filter(instructor=request.user)
    ejercicios_data = json.dumps([
        {
            "id": e.id,
            "nombre": e.nombre,
            "categoria": e.categoria,
            "categoria_display": e.get_categoria_display(),
        }
        for e in ejercicios
    ])

    return render(request, "dashboards/instructor/crear_semana.html", {
        "ejercicios_json": ejercicios_data,
    })


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


# ── CALENDARIO ────────────────────────────────────────────────────────────────

@login_required
@user_passes_test(is_instructor)
def rutina_calendario(request):
    rutinas = Rutina.objects.filter(instructor=request.user).order_by('nombre')
    clientes = CustomUser.objects.filter(mi_instructor__instructor=request.user)
    return render(request, "dashboards/instructor/rutina_calendario.html", {
        "rutinas": rutinas,
        "clientes": clientes,
    })


@login_required
@user_passes_test(is_instructor)
def rutina_calendario_api(request):
    if request.method == "GET":
        desde = request.GET.get("desde", "")
        hasta = request.GET.get("hasta", "")
        qs = RutinaCalendario.objects.filter(
            instructor=request.user,
            fecha__gte=desde,
            fecha__lte=hasta,
        ).prefetch_related("clientes").select_related("rutina")
        data = [
            {
                "id": e.id,
                "fecha": e.fecha.isoformat(),
                "rutina_id": e.rutina.id,
                "rutina_nombre": e.rutina.nombre,
                "rutina_emoji": e.rutina.emoji,
                "clientes": [
                    {"id": c.id, "nombre": c.get_full_name() or c.username}
                    for c in e.clientes.all()
                ],
            }
            for e in qs
        ]
        return JsonResponse(data, safe=False)

    if request.method == "POST":
        try:
            payload = json.loads(request.body)
        except json.JSONDecodeError:
            return JsonResponse({"error": "JSON inválido"}, status=400)

        fecha = payload.get("fecha")
        rutina_id = payload.get("rutina_id")
        cliente_ids = payload.get("cliente_ids", [])

        if not fecha or not rutina_id:
            return JsonResponse({"error": "Faltan datos"}, status=400)

        rutina = get_object_or_404(Rutina, id=rutina_id, instructor=request.user)
        entrada, _ = RutinaCalendario.objects.get_or_create(
            instructor=request.user,
            rutina=rutina,
            fecha=fecha,
        )
        clientes_qs = CustomUser.objects.filter(
            id__in=cliente_ids,
            mi_instructor__instructor=request.user,
        )
        entrada.clientes.set(clientes_qs)
        for cliente in clientes_qs:
            RutinaAsignacion.objects.get_or_create(rutina=rutina, cliente=cliente)

        return JsonResponse({
            "ok": True,
            "id": entrada.id,
            "clientes": [
                {"id": c.id, "nombre": c.get_full_name() or c.username}
                for c in entrada.clientes.all()
            ],
        })

    return JsonResponse({"error": "Método no permitido"}, status=405)


@login_required
@user_passes_test(is_instructor)
def asignar_semana_multi(request):
    """Asignar la misma semana de rutinas a varios clientes a la vez."""
    rutinas  = Rutina.objects.filter(instructor=request.user)
    clientes = CustomUser.objects.filter(mi_instructor__instructor=request.user)

    if request.method == "POST":
        day_map = {
            'lunes': 0, 'martes': 1, 'miercoles': 2,
            'jueves': 3, 'viernes': 4, 'sabado': 5, 'domingo': 6,
        }

        cliente_ids = request.POST.getlist("clientes")
        if not cliente_ids:
            messages.error(request, "Selecciona al menos un cliente.")
            return redirect("asignar_semana_multi")

        clientes_sel = CustomUser.objects.filter(
            id__in=cliente_ids,
            mi_instructor__instructor=request.user,
        )

        today      = date.today()
        week_start = today - timedelta(days=today.weekday())
        dias_count = 0

        for dia_nombre, weekday_num in day_map.items():
            rutina_id = request.POST.get(f"rutina_{dia_nombre}")
            if not rutina_id:
                continue
            rutina = get_object_or_404(Rutina, id=rutina_id, instructor=request.user)
            fecha  = week_start + timedelta(days=weekday_num)

            for cliente in clientes_sel:
                RutinaAsignacion.objects.get_or_create(rutina=rutina, cliente=cliente)
                entrada, _ = RutinaCalendario.objects.get_or_create(
                    instructor=request.user,
                    rutina=rutina,
                    fecha=fecha,
                )
                entrada.clientes.add(cliente)
            dias_count += 1

        if dias_count == 0:
            messages.error(request, "Asigna rutina a al menos un día.")
            return redirect("asignar_semana_multi")

        n = clientes_sel.count()
        messages.success(request, f"Semana asignada a {n} cliente{'s' if n != 1 else ''} ({dias_count} días).")
        return redirect("instructor_dashboard")

    rutinas_data = json.dumps([
        {"id": r.id, "nombre": r.nombre, "deporte": r.deporte, "emoji": r.emoji}
        for r in rutinas
    ])

    return render(request, "dashboards/instructor/asignar_semana_multi.html", {
        "clientes":    clientes,
        "rutinas_json": rutinas_data,
    })



@login_required
@user_passes_test(is_instructor)
def rutina_calendario_delete(request, id):
    if request.method == "POST":
        entrada = get_object_or_404(RutinaCalendario, id=id, instructor=request.user)
        entrada.delete()
        return JsonResponse({"ok": True})
    return JsonResponse({"error": "Método no permitido"}, status=405)
