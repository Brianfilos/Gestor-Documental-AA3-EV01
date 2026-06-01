from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin


class Rol(models.Model):
    idRol = models.AutoField(primary_key=True)
    nombreRol = models.CharField(max_length=50)

    class Meta:
        db_table = 'rol'
        verbose_name = 'Rol'
        verbose_name_plural = 'Roles'

    def __str__(self):
        return self.nombreRol


class Permiso(models.Model):
    idPermiso = models.AutoField(primary_key=True)
    nombrePermiso = models.CharField(max_length=100)

    class Meta:
        db_table = 'permiso'
        verbose_name = 'Permiso'
        verbose_name_plural = 'Permisos'

    def __str__(self):
        return self.nombrePermiso


class RolPermiso(models.Model):
    idRol_Permiso = models.AutoField(primary_key=True)
    idRol = models.ForeignKey(Rol, on_delete=models.CASCADE, db_column='idRol', related_name='permisos')
    idPermiso = models.ForeignKey(Permiso, on_delete=models.CASCADE, db_column='idPermiso', related_name='roles')

    class Meta:
        db_table = 'rol_permiso'
        verbose_name = 'Rol Permiso'
        verbose_name_plural = 'Roles Permisos'


class UsuarioManager(BaseUserManager):
    def create_user(self, correo, nombre, password=None, **extra_fields):
        if not correo:
            raise ValueError('El correo es obligatorio')
        correo = self.normalize_email(correo)
        user = self.model(correo=correo, nombre=nombre, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, correo, nombre, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('estado', 'activo')
        return self.create_user(correo, nombre, password, **extra_fields)


class Usuario(AbstractBaseUser, PermissionsMixin):
    ESTADO_CHOICES = [('activo', 'Activo'), ('inactivo', 'Inactivo')]

    idUsuario = models.AutoField(primary_key=True)
    nombre = models.CharField(max_length=100)
    correo = models.EmailField(max_length=100, unique=True)
    estado = models.CharField(max_length=20, choices=ESTADO_CHOICES, default='activo')
    idRol = models.ForeignKey(Rol, on_delete=models.SET_NULL, null=True, blank=True,
                               db_column='idRol', related_name='usuarios')
    is_staff = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)

    objects = UsuarioManager()

    USERNAME_FIELD = 'correo'
    REQUIRED_FIELDS = ['nombre']

    class Meta:
        db_table = 'usuario'
        verbose_name = 'Usuario'
        verbose_name_plural = 'Usuarios'

    def __str__(self):
        return f'{self.nombre} ({self.correo})'
