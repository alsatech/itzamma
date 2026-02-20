from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.http import JsonResponse, HttpResponse
from django.contrib import messages
from django.contrib.auth.decorators import login_required


def welcome_view(request):
    return render(request, "accounts/welcome.html")


def login_view(request):
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")

        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)

            # REDIRECCIÓN SEGÚN EL ROL
            if user.rol == "cliente":
                return redirect("dashboard_cliente")

            elif user.rol == "instructor":
                return redirect("instructor_dashboard")

            elif user.rol == "superadmin":
                return redirect("dashboard_admin")

            # fallback por si algo falla
            return redirect("dashboard_cliente")

        else:
            messages.error(request, "Usuario o contraseña incorrectos")

    return render(request, "accounts/login.html")


def logout_view(request):
    logout(request)
    return redirect("login")


# Validación HTMX
def validate_login(request):
    username = request.POST.get("username")

    from django.contrib.auth import get_user_model
    User = get_user_model()

    exists = User.objects.filter(username=username).exists()

    if not exists:
        return HttpResponse(
            "<p class='text-red-600 text-sm mt-1'>El usuario no existe.</p>"
        )

    return HttpResponse(
        "<p class='text-green-600 text-sm mt-1'>Usuario encontrado.</p>"
    )


@login_required
def crear_cliente(request):
    if request.user.rol != "instructor":
        return redirect("login")

    from .forms import CrearClienteForm
    from .models import InstructorClient
    from django.contrib.auth import get_user_model
    User = get_user_model()

    if request.method == "POST":
        form = CrearClienteForm(request.POST)
        if form.is_valid():
            nuevo_cliente = User.objects.create_user(
                username=form.cleaned_data["username"],
                email=form.cleaned_data["email"],
                password=form.cleaned_data["password1"],
                rol="cliente"
            )
            InstructorClient.objects.create(
                instructor=request.user,
                cliente=nuevo_cliente
            )
            messages.success(request, f"Cliente {nuevo_cliente.username} creado exitosamente.")
            return redirect("instructor_dashboard")
    else:
        form = CrearClienteForm()

    return render(request, "dashboards/instructor/crear_cliente.html", {"form": form})


@login_required
def dashboard_admin(request):
    if request.user.rol != "superadmin":
        return redirect("login")

    from django.contrib.auth import get_user_model
    from workouts.models import RoutineCompleted, Workout
    User = get_user_model()

    instructores = User.objects.filter(rol="instructor")
    total_clientes = User.objects.filter(rol="cliente").count()
    total_rutinas = Workout.objects.count()
    total_completadas = RoutineCompleted.objects.count()

    return render(request, "dashboards/admin/dashboard_admin.html", {
        "instructores": instructores,
        "total_clientes": total_clientes,
        "total_rutinas": total_rutinas,
        "total_completadas": total_completadas,
    })


@login_required
def crear_instructor(request):
    if request.user.rol != "superadmin":
        return redirect("login")

    from .forms import CrearInstructorForm
    from .models import InstructorProfile
    from django.contrib.auth import get_user_model
    User = get_user_model()

    if request.method == "POST":
        form = CrearInstructorForm(request.POST)
        if form.is_valid():
            nuevo_instructor = User.objects.create_user(
                username=form.cleaned_data["username"],
                email=form.cleaned_data["email"],
                password=form.cleaned_data["password1"],
                rol="instructor"
            )
            InstructorProfile.objects.create(
                user=nuevo_instructor,
                deporte=form.cleaned_data["deporte"],
                biografia=form.cleaned_data.get("biografia", "")
            )
            messages.success(request, f"Instructor {nuevo_instructor.username} creado exitosamente.")
            return redirect("dashboard_admin")
    else:
        form = CrearInstructorForm()

    return render(request, "dashboards/admin/crear_instructor.html", {"form": form})
