from django.contrib import admin
from .models import Workout, WorkoutAssignment, ProgressReport

admin.site.register(Workout)
admin.site.register(WorkoutAssignment)
admin.site.register(ProgressReport)
