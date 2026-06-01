from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import Usuario, Rol, Permiso, RolPermiso


@admin.register(Rol)
class RolAdmin(admin.ModelAdmin):
    list_display = ['idRol', 'nombreRol']


@admin.register(Permiso)
class PermisoAdmin(admin.ModelAdmin):
    list_display = ['idPermiso', 'nombrePermiso']


@admin.register(Usuario)
class UsuarioAdmin(UserAdmin):
    list_display = ['idUsuario', 'nombre', 'correo', 'estado', 'idRol', 'is_staff']
    list_filter = ['estado', 'idRol', 'is_staff']
    search_fields = ['nombre', 'correo']
    ordering = ['nombre']
    fieldsets = (
        (None, {'fields': ('correo', 'password')}),
        ('Información Personal', {'fields': ('nombre', 'estado', 'idRol')}),
        ('Permisos', {'fields': ('is_staff', 'is_active', 'is_superuser', 'groups', 'user_permissions')}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('correo', 'nombre', 'estado', 'idRol', 'password1', 'password2'),
        }),
    )


@admin.register(RolPermiso)
class RolPermisoAdmin(admin.ModelAdmin):
    list_display = ['idRol_Permiso', 'idRol', 'idPermiso']
