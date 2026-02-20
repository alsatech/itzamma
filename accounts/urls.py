from django.urls import path
from . import views

urlpatterns = [
    path("login/", views.login_view, name="login"),
    path("login/validate/", views.validate_login, name="validate_login"),
    path("instructor/crear-cliente/", views.crear_cliente, name="crear_cliente"),
    path("admin-panel/", views.dashboard_admin, name="dashboard_admin"),
    path("admin-panel/crear-instructor/", views.crear_instructor, name="crear_instructor"),
]
