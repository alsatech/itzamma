from django.urls import path
from . import views

urlpatterns = [
    path("perfil/", views.completar_perfil, name="completar_perfil"),
    path("dashboard/", views.dashboard_cliente, name="dashboard_cliente"),
    path("rutinas/", views.ver_rutinas, name="ver_rutinas"),
    path("rutinas/semana/", views.rutinas_semana, name="rutinas_semana"),
    path("rutina/<int:assignment_id>/", views.detalle_rutina, name="detalle_rutina"),
    path("mi-perfil/", views.perfil, name="perfil"),
    path("suplementos/", views.suplementos, name="suplementos"),
    path("suplementos/proteinas/", views.suplementos_proteinas, name="suplementos_proteinas"),
    path("suplementos/preentreno/", views.suplementos_preentreno, name="suplementos_preentreno"),
    path("suplementos/creatina/", views.suplementos_creatina, name="suplementos_creatina"),
    path("suplementos/vitaminas/", views.suplementos_vitaminas, name="suplementos_vitaminas"),
    path("suplementos/aminoacidos/", views.suplementos_aminoacidos, name="suplementos_aminoacidos"),
    path("graficas/", views.graficas, name="graficas"),
    path("instructor/cliente/<int:cliente_id>/reportes/", views.reportes_cliente, name="reportes_cliente"),
    path("instructor/cliente/<int:cliente_id>/reportes/crear/", views.crear_reporte, name="crear_reporte"),
    path("imc/", views.masa_corporal, name="masa_corporal"),
]
