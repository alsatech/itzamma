from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('profiles', '0003_alter_userprofile_estatura'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='MedicionFisica',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('fecha', models.DateField()),
                ('peso', models.DecimalField(blank=True, decimal_places=1, max_digits=5, null=True)),
                ('masa_muscular', models.DecimalField(blank=True, decimal_places=1, max_digits=5, null=True)),
                ('masa_grasa', models.DecimalField(blank=True, decimal_places=1, max_digits=5, null=True)),
                ('user', models.ForeignKey(
                    on_delete=django.db.models.deletion.CASCADE,
                    related_name='mediciones',
                    to=settings.AUTH_USER_MODEL,
                )),
            ],
            options={'ordering': ['fecha']},
        ),
    ]
