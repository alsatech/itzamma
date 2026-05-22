from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser, InstructorClient


class InstructorClientInline(admin.StackedInline):
    """Permite asignar/cambiar instructor desde la edición del cliente."""
    model = InstructorClient
    fk_name = "cliente"
    extra = 1
    max_num = 1
    autocomplete_fields = ["instructor"]
    verbose_name = "Instructor asignado"
    verbose_name_plural = "Instructor asignado"


class CustomUserAdmin(UserAdmin):
    model = CustomUser
    list_display = ("username", "email", "rol", "instructor_asignado", "telefono")
    list_filter = UserAdmin.list_filter + ("rol",)
    search_fields = ("username", "email", "first_name", "last_name")
    fieldsets = UserAdmin.fieldsets + (
        ("Información adicional", {
            "fields": ("telefono", "foto", "rol")
        }),
    )
    add_fieldsets = UserAdmin.add_fieldsets + (
        ("Información adicional", {
            "fields": ("email", "rol", "telefono")
        }),
    )

    def get_inlines(self, request, obj=None):
        # Sólo mostrar el inline cuando estamos editando un cliente existente.
        if obj and obj.rol == "cliente":
            return [InstructorClientInline]
        return []

    @admin.display(description="Instructor")
    def instructor_asignado(self, obj):
        if obj.rol != "cliente":
            return "—"
        link = getattr(obj, "mi_instructor", None)
        return link.instructor.username if link else "⚠ sin asignar"


@admin.register(InstructorClient)
class InstructorClientAdmin(admin.ModelAdmin):
    list_display = ("cliente", "instructor", "fecha_registro")
    list_filter = ("instructor",)
    search_fields = ("cliente__username", "cliente__email", "instructor__username")
    autocomplete_fields = ["instructor", "cliente"]


admin.site.register(CustomUser, CustomUserAdmin)
