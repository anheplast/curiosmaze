# Generated by Django 5.2 on 2025-04-04 21:27

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('auth', '0012_alter_user_first_name_max_length'),
    ]

    operations = [
        migrations.CreateModel(
            name='User',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('password', models.CharField(max_length=128, verbose_name='password')),
                ('last_login', models.DateTimeField(blank=True, null=True, verbose_name='last login')),
                ('is_superuser', models.BooleanField(default=False, help_text='Designates that this user has all permissions without explicitly assigning them.', verbose_name='superuser status')),
                ('username', models.CharField(max_length=50, unique=True, verbose_name='Número de identificación')),
                ('email', models.EmailField(max_length=254, unique=True, verbose_name='Correo electrónico')),
                ('is_active', models.BooleanField(default=True)),
                ('is_staff', models.BooleanField(default=False)),
                ('date_joined', models.DateTimeField(auto_now_add=True)),
                ('groups', models.ManyToManyField(blank=True, help_text='The groups this user belongs to. A user will get all permissions granted to each of their groups.', related_name='user_set', related_query_name='user', to='auth.group', verbose_name='groups')),
                ('user_permissions', models.ManyToManyField(blank=True, help_text='Specific permissions for this user.', related_name='user_set', related_query_name='user', to='auth.permission', verbose_name='user permissions')),
            ],
            options={
                'verbose_name': 'Usuario',
                'verbose_name_plural': 'Usuarios',
            },
        ),
        migrations.CreateModel(
            name='UserProfile',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('rol', models.CharField(choices=[('estudiante', 'Estudiante'), ('docente', 'Docente'), ('admin', 'Administrador')], default='estudiante', max_length=20)),
                ('nombres', models.CharField(max_length=100)),
                ('apellidos', models.CharField(max_length=100)),
                ('edad', models.PositiveIntegerField(blank=True, null=True)),
                ('genero', models.CharField(blank=True, choices=[('masculino', 'Masculino'), ('femenino', 'Femenino'), ('otro', 'Otro')], max_length=10, null=True)),
                ('fecha_nacimiento', models.DateField(blank=True, null=True)),
                ('identificacion', models.CharField(max_length=20, unique=True)),
                ('turno', models.CharField(blank=True, choices=[('mañana', 'Mañana'), ('tarde', 'Tarde')], max_length=10, null=True)),
                ('curso', models.CharField(blank=True, max_length=10, null=True)),
                ('paralelo', models.CharField(blank=True, max_length=5, null=True)),
                ('especializacion', models.CharField(blank=True, max_length=50, null=True)),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='profile', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'Perfil de Usuario',
                'verbose_name_plural': 'Perfiles de Usuario',
            },
        ),
    ]
