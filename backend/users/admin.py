# backend/users/admin.py

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils.translation import gettext_lazy as _

from .models import User, UserProfile


class UserProfileInline(admin.StackedInline):
    model = UserProfile
    can_delete = False
    verbose_name_plural = 'Perfil de usuario'


class UserAdmin(BaseUserAdmin):
    inlines = (UserProfileInline,)
    list_display = ('username', 'email', 'is_staff', 'is_active', 'get_rol')
    list_filter = ('is_active', 'is_staff', 'profile__rol')
    fieldsets = (
        (None, {'fields': ('username', 'email', 'password')}),
        (_('Permisos'), {'fields': ('is_active', 'is_staff', 'is_superuser')}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'email', 'password1', 'password2'),
        }),
    )
    search_fields = ('username', 'email', 'profile__nombres', 'profile__apellidos')
    ordering = ('username',)

    def get_rol(self, obj):
        try:
            return obj.profile.rol
        except UserProfile.DoesNotExist:
            return "Sin perfil"
    get_rol.short_description = 'Rol'


admin.site.register(User, UserAdmin)