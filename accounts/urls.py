from django.urls import path
from . import views

urlpatterns = [
    path("login/", views.login_view, name="login"),
    path("login/validate/", views.validate_login, name="validate_login"),  # HTMX
]
