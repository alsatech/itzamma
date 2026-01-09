from django.urls import path
from . import views
from . views import instructor_cliente_detalle

urlpatterns = [
    path("perfil/", views.completar_perfil, name="completar_perfil"),
    path("dashboard/", views.dashboard_cliente, name="dashboard_cliente"),
    path("rutinas/", views.ver_rutinas, name="ver_rutinas"),
    path("rutinas/semana/", views.rutinas_semana, name="rutinas_semana"),  # NUEVO
    # path("rutina/<int:id>/", views.detalle_rutina, name="detalle_rutina"),
    path("rutina/<int:assignment_id>/", views.detalle_rutina, name="detalle_rutina"),
    path("mi-perfil/", views.perfil, name="perfil"),
    path("instructor/cliente/<int:cliente_id>/", instructor_cliente_detalle, name="instructor_cliente_detalle"),
    path("instructor/cliente/<int:cliente_id>/reportes/",views.reportes_cliente,name="reportes_cliente"),
    path("instructor/cliente/<int:cliente_id>/reportes/crear/",views.crear_reporte,name="crear_reporte"),
]

