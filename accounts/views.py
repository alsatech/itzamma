from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.http import JsonResponse, HttpResponse
from django.contrib import messages


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
                return redirect("dashboard_instructor")

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
