from django.urls import path
from django.contrib.auth.views import LogoutView
from . import views

urlpatterns = [
    path("login/", views.login_view, name="login"),
    path("login/validate/", views.validate_login, name="validate_login"),

]