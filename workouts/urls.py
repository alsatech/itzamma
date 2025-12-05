
from django.urls import path
from .views import complete_routine, instructor_workout_create, instructor_dashboard, assign_workout

urlpatterns = [
    path("instructor/dashboard/", instructor_dashboard, name="instructor_dashboard"),
    path("complete/<int:workout_id>/", complete_routine, name="complete_routine"),
    path("instructor/workouts/new/", instructor_workout_create, name="instructor_workout_create"),
    path("instructor/workouts/<int:workout_id>/assign/", assign_workout, name="assign_workout"),
]
