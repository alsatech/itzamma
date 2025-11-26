from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser

class CustomUserAdmin(UserAdmin):
    model = CustomUser
    list_display = ("username", "email", "rol", "telefono")
    fieldsets = UserAdmin.fieldsets + (
        ("Información adicional", {
            "fields": ("telefono", "foto", "rol")
        }),
    )

admin.site.register(CustomUser, CustomUserAdmin)
