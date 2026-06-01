"""
Script para crear datos iniciales en la base de datos.
Ejecutar con: python setup_inicial.py
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'gestor_documental.settings')
django.setup()

from apps.usuarios.models import Rol, Permiso, RolPermiso, Usuario
from apps.documentos.models import ClasificacionDocumento

print("Creando roles...")
roles_data = ['Administrador', 'Editor', 'Visualizador', 'Revisor']
roles = {}
for nombre in roles_data:
    rol, _ = Rol.objects.get_or_create(nombreRol=nombre)
    roles[nombre] = rol
    print(f"  ✓ Rol: {nombre}")

print("\nCreando permisos...")
permisos_data = [
    'Ver documentos', 'Crear documentos', 'Editar documentos', 'Eliminar documentos',
    'Ver usuarios', 'Gestionar usuarios', 'Ver historial', 'Revisar documentos'
]
permisos = {}
for nombre in permisos_data:
    p, _ = Permiso.objects.get_or_create(nombrePermiso=nombre)
    permisos[nombre] = p
    print(f"  ✓ Permiso: {nombre}")

print("\nAsignando permisos a roles...")
# Administrador tiene todos los permisos
for perm in permisos.values():
    RolPermiso.objects.get_or_create(idRol=roles['Administrador'], idPermiso=perm)

# Editor: ver, crear, editar
for nombre in ['Ver documentos', 'Crear documentos', 'Editar documentos', 'Ver historial']:
    RolPermiso.objects.get_or_create(idRol=roles['Editor'], idPermiso=permisos[nombre])

# Visualizador: solo ver
RolPermiso.objects.get_or_create(idRol=roles['Visualizador'], idPermiso=permisos['Ver documentos'])

# Revisor: ver y revisar
for nombre in ['Ver documentos', 'Revisar documentos', 'Ver historial']:
    RolPermiso.objects.get_or_create(idRol=roles['Revisor'], idPermiso=permisos[nombre])

print("\nCreando clasificaciones...")
clases = [
    ('Administrativo', 'Documentos de gestión administrativa'),
    ('Técnico', 'Documentos técnicos y especificaciones'),
    ('Legal', 'Documentos legales y contratos'),
    ('Financiero', 'Documentos financieros y contables'),
    ('Recursos Humanos', 'Documentos de personal'),
    ('Académico', 'Documentos académicos y educativos'),
]
for nombre, desc in clases:
    c, _ = ClasificacionDocumento.objects.get_or_create(
        nombreClasificacion=nombre, defaults={'descripcion': desc}
    )
    print(f"  ✓ Clasificación: {nombre}")

print("\nCreando usuario administrador...")
if not Usuario.objects.filter(correo='admin@gestordoc.com').exists():
    admin = Usuario.objects.create_superuser(
        correo='admin@gestordoc.com',
        nombre='Administrador',
        password='Admin2024*',
        idRol=roles['Administrador'],
        estado='activo'
    )
    print("  ✓ Admin creado: admin@gestordoc.com / Admin2024*")
else:
    print("  ℹ  Admin ya existe")

print("\n✅ Configuración inicial completada.")
print("\nCredenciales de acceso:")
print("  Correo:    admin@gestordoc.com")
print("  Contraseña: Admin2024*")
print("\nInicia el servidor con:")
print("  python manage.py runserver")
