from django.urls import path
from . import views

urlpatterns = [
    path("perfil/", views.completar_perfil, name="completar_perfil"),
    path("dashboard/", views.dashboard_cliente, name="dashboard_cliente"),
    path("rutinas/", views.ver_rutinas, name="ver_rutinas"),
    path("rutina/<int:id>/", views.detalle_rutina, name="detalle_rutina"),

]
