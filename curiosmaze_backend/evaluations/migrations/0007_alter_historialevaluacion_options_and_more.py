# Generated by Django 5.2 on 2025-05-04 21:10

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('evaluations', '0006_historialevaluacion'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='historialevaluacion',
            options={'ordering': ['-fecha_almacenamiento'], 'verbose_name': 'Historial de Evaluación', 'verbose_name_plural': 'Historiales de Evaluaciones'},
        ),
        migrations.RemoveField(
            model_name='historialevaluacion',
            name='estudiante_evaluacion',
        ),
        migrations.RemoveField(
            model_name='historialevaluacion',
            name='fecha_finalizacion',
        ),
        migrations.AddField(
            model_name='historialevaluacion',
            name='docente_id',
            field=models.IntegerField(default=0),
        ),
        migrations.AddField(
            model_name='historialevaluacion',
            name='docente_nombre',
            field=models.CharField(default='', max_length=200),
        ),
        migrations.AddField(
            model_name='historialevaluacion',
            name='estudiante_email',
            field=models.EmailField(default='', max_length=254),
        ),
        migrations.AddField(
            model_name='historialevaluacion',
            name='estudiante_id',
            field=models.IntegerField(default=0),
        ),
        migrations.AddField(
            model_name='historialevaluacion',
            name='estudiante_nombre',
            field=models.CharField(default='', max_length=200),
        ),
        migrations.AddField(
            model_name='historialevaluacion',
            name='evaluacion_activa',
            field=models.BooleanField(default=True),
        ),
        migrations.AddField(
            model_name='historialevaluacion',
            name='evaluacion_codigo_acceso',
            field=models.CharField(default='', max_length=8),
        ),
        migrations.AddField(
            model_name='historialevaluacion',
            name='evaluacion_descripcion',
            field=models.TextField(blank=True, default=''),
        ),
        migrations.AddField(
            model_name='historialevaluacion',
            name='evaluacion_id',
            field=models.IntegerField(default=0),
        ),
        migrations.AddField(
            model_name='historialevaluacion',
            name='evaluacion_puntaje_total',
            field=models.PositiveIntegerField(default=0),
        ),
        migrations.AddField(
            model_name='historialevaluacion',
            name='evaluacion_titulo',
            field=models.CharField(default='', max_length=200),
        ),
        migrations.AddField(
            model_name='historialevaluacion',
            name='fecha_almacenamiento',
            field=models.DateTimeField(auto_now_add=True, default=datetime.datetime(2025, 5, 4, 21, 10, 46, 418385, tzinfo=datetime.timezone.utc)),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='historialevaluacion',
            name='fecha_fin',
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='historialevaluacion',
            name='fecha_inicio',
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AddIndex(
            model_name='historialevaluacion',
            index=models.Index(fields=['estudiante_id', '-fecha_almacenamiento'], name='evaluations_estudia_e43edf_idx'),
        ),
        migrations.AddIndex(
            model_name='historialevaluacion',
            index=models.Index(fields=['evaluacion_id'], name='evaluations_evaluac_745ef4_idx'),
        ),
    ]
