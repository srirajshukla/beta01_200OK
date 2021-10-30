# Generated by Django 3.2.8 on 2021-10-30 08:41

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('crops', '0001_initial'),
        ('soil_health', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='CropPlantation',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('planted_date', models.DateField()),
                ('harvested_date', models.DateField(blank=True, null=True)),
                ('crop', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='crops.crops')),
                ('farmer', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
                ('soil_type', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='soil_health.soilhealth')),
            ],
        ),
    ]
