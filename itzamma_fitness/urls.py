from django.contrib import admin
from django.urls import path, include
from accounts import views as accounts_views
from accounts.views import welcome_view


urlpatterns = [
    path('', welcome_view, name="welcome"),
    path("admin/", admin.site.urls),
    path("login/", accounts_views.login_view, name="login"),
    path("logout/", accounts_views.logout_view, name="logout"),
    path("accounts/", include("accounts.urls")),
    path("profiles/", include("profiles.urls")),
    path("workouts/", include("workouts.urls")),

]
