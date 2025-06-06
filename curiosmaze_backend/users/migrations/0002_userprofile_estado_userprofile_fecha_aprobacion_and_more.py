# Generated by Django 5.2 on 2025-04-24 00:14

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='userprofile',
            name='estado',
            field=models.CharField(choices=[('pendiente', 'Pendiente'), ('activo', 'Activo'), ('rechazado', 'Rechazado')], default='pendiente', max_length=20),
        ),
        migrations.AddField(
            model_name='userprofile',
            name='fecha_aprobacion',
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='userprofile',
            name='motivo_rechazo',
            field=models.TextField(blank=True, null=True),
        ),
    ]
