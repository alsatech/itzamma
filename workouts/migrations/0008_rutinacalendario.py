from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('workouts', '0007_maximoejercicio'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.AlterField(
            model_name='rutinadia',
            name='dia',
            field=models.CharField(
                choices=[
                    ('lunes', 'Lunes'),
                    ('martes', 'Martes'),
                    ('miercoles', 'Miércoles'),
                    ('jueves', 'Jueves'),
                    ('viernes', 'Viernes'),
                    ('sabado', 'Sábado'),
                    ('domingo', 'Domingo'),
                    ('general', 'Sesión'),
                ],
                max_length=20,
            ),
        ),
        migrations.CreateModel(
            name='RutinaCalendario',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('fecha', models.DateField()),
                ('instructor', models.ForeignKey(
                    limit_choices_to={'rol': 'instructor'},
                    on_delete=django.db.models.deletion.CASCADE,
                    related_name='calendario',
                    to=settings.AUTH_USER_MODEL,
                )),
                ('rutina', models.ForeignKey(
                    on_delete=django.db.models.deletion.CASCADE,
                    related_name='en_calendario',
                    to='workouts.rutina',
                )),
                ('clientes', models.ManyToManyField(
                    blank=True,
                    limit_choices_to={'rol': 'cliente'},
                    related_name='calendario_entries',
                    to=settings.AUTH_USER_MODEL,
                )),
            ],
            options={
                'ordering': ['fecha'],
                'unique_together': {('instructor', 'rutina', 'fecha')},
            },
        ),
    ]
