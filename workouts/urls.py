
from django.urls import path
from .views import complete_routine

urlpatterns = [
    path("complete/<int:workout_id>/", complete_routine, name="complete_routine"),
]
