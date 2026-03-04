from django.urls import path
from .views import (
    instructor_dashboard, instructor_perfil,
    instructor_clientes, instructor_cliente_detalle,
    ejercicio_list, ejercicio_create, ejercicio_delete, ejercicios_json,
    rutina_list, rutina_create, rutina_detail, rutina_assign,
    complete_rutina,
)

urlpatterns = [
    # Dashboard
    path("instructor/dashboard/", instructor_dashboard, name="instructor_dashboard"),
    path("instructor/perfil/", instructor_perfil, name="instructor_perfil"),
    path("instructor/clientes/", instructor_clientes, name="instructor_clientes"),
    path("instructor/clientes/<int:cliente_id>/", instructor_cliente_detalle, name="instructor_cliente_detalle"),

    # Ejercicios
    path("instructor/ejercicios/", ejercicio_list, name="ejercicio_list"),
    path("instructor/ejercicios/nuevo/", ejercicio_create, name="ejercicio_create"),
    path("instructor/ejercicios/<int:id>/eliminar/", ejercicio_delete, name="ejercicio_delete"),
    path("instructor/api/ejercicios/", ejercicios_json, name="ejercicios_json"),

    # Completar rutina (cliente)
    path("complete/<int:assignment_id>/", complete_rutina, name="complete_rutina"),

    # Rutinas
    path("instructor/rutinas/", rutina_list, name="rutina_list"),
    path("instructor/rutinas/nueva/", rutina_create, name="rutina_create"),
    path("instructor/rutinas/<int:id>/", rutina_detail, name="rutina_detail"),
    path("instructor/rutinas/<int:id>/asignar/", rutina_assign, name="rutina_assign"),
]
