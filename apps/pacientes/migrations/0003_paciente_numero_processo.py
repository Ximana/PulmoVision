# Generated by Django 5.1.5 on 2025-02-16 00:47

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('pacientes', '0002_alter_paciente_genero'),
    ]

    operations = [
        migrations.AddField(
            model_name='paciente',
            name='numero_processo',
            field=models.CharField(blank=True, editable=False, help_text='Formato: pv[ano][número sequencial]', max_length=12, null=True, unique=True, verbose_name='Número de Processo'),
        ),
    ]
