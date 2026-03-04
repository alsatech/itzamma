from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('workouts', '0005_workout_deporte'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        # ── Eliminar modelos viejos ──────────────────────────────────────────
        migrations.DeleteModel(name='RoutineCompleted'),
        migrations.DeleteModel(name='WorkoutAssignment'),
        migrations.DeleteModel(name='WorkoutMedia'),
        migrations.DeleteModel(name='Workout'),

        # ── Ejercicio ────────────────────────────────────────────────────────
        migrations.CreateModel(
            name='Ejercicio',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nombre', models.CharField(max_length=200)),
                ('categoria', models.CharField(
                    choices=[('fuerza', 'Fuerza'), ('funcional', 'Funcional'), ('potencia', 'Potencia')],
                    default='fuerza', max_length=20,
                )),
                ('descripcion', models.TextField(blank=True)),
                ('creado', models.DateTimeField(auto_now_add=True)),
                ('instructor', models.ForeignKey(
                    limit_choices_to={'rol': 'instructor'},
                    on_delete=django.db.models.deletion.CASCADE,
                    related_name='ejercicios',
                    to=settings.AUTH_USER_MODEL,
                )),
            ],
        ),

        # ── EjercicioMedia ───────────────────────────────────────────────────
        migrations.CreateModel(
            name='EjercicioMedia',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('tipo', models.CharField(
                    choices=[('video', 'Video'), ('foto', 'Foto')],
                    default='video', max_length=10,
                )),
                ('url_video', models.URLField(blank=True)),
                ('imagen', models.ImageField(blank=True, null=True, upload_to='ejercicios/fotos/')),
                ('orden', models.IntegerField(default=0)),
                ('ejercicio', models.ForeignKey(
                    on_delete=django.db.models.deletion.CASCADE,
                    related_name='media',
                    to='workouts.ejercicio',
                )),
            ],
            options={'ordering': ['orden']},
        ),

        # ── Rutina ───────────────────────────────────────────────────────────
        migrations.CreateModel(
            name='Rutina',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nombre', models.CharField(max_length=200)),
                ('descripcion', models.TextField(blank=True)),
                ('deporte', models.CharField(
                    choices=[
                        ('gym', 'Gym'), ('futbol', 'Fútbol'), ('tenis', 'Tenis'),
                        ('basketball', 'Basketball'), ('natacion', 'Natación'),
                        ('ciclismo', 'Ciclismo'), ('boxeo', 'Boxeo'), ('yoga', 'Yoga'),
                        ('running', 'Running'), ('voleibol', 'Voleibol'),
                        ('beisbol', 'Béisbol'), ('atletismo', 'Atletismo'),
                        ('pingpong', 'Ping Pong'), ('otro', 'Otro'),
                    ],
                    default='gym', max_length=20,
                )),
                ('creado', models.DateTimeField(auto_now_add=True)),
                ('instructor', models.ForeignKey(
                    limit_choices_to={'rol': 'instructor'},
                    on_delete=django.db.models.deletion.CASCADE,
                    related_name='rutinas',
                    to=settings.AUTH_USER_MODEL,
                )),
            ],
        ),

        # ── RutinaDia ────────────────────────────────────────────────────────
        migrations.CreateModel(
            name='RutinaDia',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('dia', models.CharField(
                    choices=[
                        ('lunes', 'Lunes'), ('martes', 'Martes'), ('miercoles', 'Miércoles'),
                        ('jueves', 'Jueves'), ('viernes', 'Viernes'),
                        ('sabado', 'Sábado'), ('domingo', 'Domingo'),
                    ],
                    max_length=20,
                )),
                ('orden', models.IntegerField(default=0)),
                ('rutina', models.ForeignKey(
                    on_delete=django.db.models.deletion.CASCADE,
                    related_name='dias',
                    to='workouts.rutina',
                )),
            ],
            options={'ordering': ['orden']},
        ),

        # ── RutinaSeccion ────────────────────────────────────────────────────
        migrations.CreateModel(
            name='RutinaSeccion',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('tipo', models.CharField(
                    choices=[
                        ('cardio', 'Subida de Frecuencia Cardiaca'),
                        ('calentamiento', 'Calentamiento'),
                        ('medular', 'Medular'),
                        ('cierre', 'Cierre'),
                    ],
                    max_length=20,
                )),
                ('orden', models.IntegerField(default=0)),
                ('dia', models.ForeignKey(
                    on_delete=django.db.models.deletion.CASCADE,
                    related_name='secciones',
                    to='workouts.rutinadia',
                )),
            ],
            options={'ordering': ['orden']},
        ),

        # ── RutinaEjercicio ──────────────────────────────────────────────────
        migrations.CreateModel(
            name='RutinaEjercicio',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('series', models.IntegerField(default=3)),
                ('repeticiones', models.CharField(default='12', max_length=50)),
                ('descanso', models.IntegerField(default=60)),
                ('porcentaje', models.IntegerField(blank=True, null=True)),
                ('orden', models.IntegerField(default=0)),
                ('ejercicio', models.ForeignKey(
                    on_delete=django.db.models.deletion.CASCADE,
                    to='workouts.ejercicio',
                )),
                ('seccion', models.ForeignKey(
                    on_delete=django.db.models.deletion.CASCADE,
                    related_name='ejercicios',
                    to='workouts.rutinaseccion',
                )),
            ],
            options={'ordering': ['orden']},
        ),

        # ── RutinaAsignacion ─────────────────────────────────────────────────
        migrations.CreateModel(
            name='RutinaAsignacion',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('fecha_asignacion', models.DateField(auto_now_add=True)),
                ('cliente', models.ForeignKey(
                    limit_choices_to={'rol': 'cliente'},
                    on_delete=django.db.models.deletion.CASCADE,
                    related_name='rutinas_asignadas',
                    to=settings.AUTH_USER_MODEL,
                )),
                ('rutina', models.ForeignKey(
                    on_delete=django.db.models.deletion.CASCADE,
                    related_name='asignaciones',
                    to='workouts.rutina',
                )),
            ],
        ),

        # ── RutinaCompletada ─────────────────────────────────────────────────
        migrations.CreateModel(
            name='RutinaCompletada',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('completed_at', models.DateTimeField(auto_now_add=True)),
                ('rutina', models.ForeignKey(
                    on_delete=django.db.models.deletion.CASCADE,
                    related_name='completadas_por',
                    to='workouts.rutina',
                )),
                ('user', models.ForeignKey(
                    on_delete=django.db.models.deletion.CASCADE,
                    related_name='rutinas_completadas',
                    to=settings.AUTH_USER_MODEL,
                )),
            ],
        ),
    ]
