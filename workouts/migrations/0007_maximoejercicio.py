from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('workouts', '0006_replace_workout_with_ejercicio_rutina'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='MaximoEjercicio',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('peso_kg', models.DecimalField(decimal_places=1, max_digits=6)),
                ('fecha', models.DateField()),
                ('ejercicio', models.ForeignKey(
                    on_delete=django.db.models.deletion.CASCADE,
                    related_name='maximos',
                    to='workouts.ejercicio',
                )),
                ('user', models.ForeignKey(
                    on_delete=django.db.models.deletion.CASCADE,
                    related_name='maximos',
                    to=settings.AUTH_USER_MODEL,
                )),
            ],
            options={'ordering': ['fecha']},
        ),
    ]
