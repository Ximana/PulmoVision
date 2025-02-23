# Generated by Django 5.1.5 on 2025-02-01 09:18

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('usuarios', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='usuario',
            name='especializacao',
            field=models.CharField(blank=True, help_text='Área de especialização', max_length=100, verbose_name='Especialização'),
        ),
        migrations.AlterField(
            model_name='usuario',
            name='foto_perfil',
            field=models.ImageField(blank=True, help_text='Foto de perfil do usuário', null=True, upload_to='usuarios/perfil', verbose_name='Foto de Perfil'),
        ),
        migrations.AlterField(
            model_name='usuario',
            name='funcao',
            field=models.CharField(choices=[('admin', 'Administrador'), ('medico', 'Médico'), ('tecnico', 'Técnico'), ('pesquisador', 'Pesquisador')], help_text='Função do usuário no sistema', max_length=20, verbose_name='Função'),
        ),
        migrations.AlterField(
            model_name='usuario',
            name='registro_profissional',
            field=models.CharField(blank=True, help_text='Número de ordem/registro profissional', max_length=20, verbose_name='Registro Profissional'),
        ),
        migrations.AlterField(
            model_name='usuario',
            name='telefone',
            field=models.CharField(blank=True, help_text='Número de telefone para contato', max_length=20, verbose_name='Telefone'),
        ),
    ]
