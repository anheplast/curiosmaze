# Generated by Django 5.2 on 2025-04-28 02:38

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('evaluations', '0005_ejercicio_credito_ejercicio_dificultad'),
    ]

    operations = [
        migrations.CreateModel(
            name='HistorialEvaluacion',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('fecha_finalizacion', models.DateTimeField(auto_now_add=True)),
                ('puntaje_total', models.FloatField(default=0)),
                ('porcentaje_aprobacion', models.FloatField(default=0)),
                ('tiempo_total', models.DurationField(blank=True, null=True)),
                ('detalles', models.JSONField(default=dict, help_text='Detalles completos de la evaluación incluyendo respuestas')),
                ('estudiante_evaluacion', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='historial', to='evaluations.estudianteevaluacion')),
            ],
            options={
                'verbose_name': 'Historial de Evaluación',
                'verbose_name_plural': 'Historiales de Evaluaciones',
                'ordering': ['-fecha_finalizacion'],
            },
        ),
    ]
