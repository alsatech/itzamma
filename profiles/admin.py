from django.contrib import admin
from .models import UserProfile, MedicionFisica

@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ("user", "nombre", "edad", "deporte")

@admin.register(MedicionFisica)
class MedicionFisicaAdmin(admin.ModelAdmin):
    list_display = ("user", "fecha", "peso", "masa_muscular", "masa_grasa")
