# Generated by Django 5.1.5 on 2025-02-16 01:14

import apps.pacientes.models
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('pacientes', '0004_alter_paciente_numero_processo'),
    ]

    operations = [
        migrations.AlterField(
            model_name='paciente',
            name='foto',
            field=models.ImageField(blank=True, null=True, upload_to=apps.pacientes.models.paciente_foto_path, verbose_name='Foto'),
        ),
    ]
