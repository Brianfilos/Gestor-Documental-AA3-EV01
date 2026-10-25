"""
Siembra datos de demostración en la base SQLite aislada (settings_demo), para
grabar el video de la evidencia GA9-220501096-AA3-EV01 sin tocar la base MySQL
real del proyecto.

Uso: python seed_demo.py
"""
import os
import django

# Por defecto usa la base SQLite de demostración; en el servidor se ejecuta con
# DJANGO_SETTINGS_MODULE=gestor_documental.settings_produccion para sembrar la base publicada.
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'gestor_documental.settings_demo')
django.setup()

from apps.usuarios.models import Rol, Permiso, RolPermiso, Usuario
from apps.documentos.models import ClasificacionDocumento, Documento, HistorialDocumento, RevisionDocumento

print("Creando roles...")
roles = {}
for nombre in ['Administrador', 'Editor', 'Visualizador', 'Revisor']:
    rol, _ = Rol.objects.get_or_create(nombreRol=nombre)
    roles[nombre] = rol

print("Creando permisos...")
permisos = {}
for nombre in ['ver_documentos', 'crear_documentos', 'editar_documentos', 'eliminar_documentos', 'gestionar_usuarios']:
    p, _ = Permiso.objects.get_or_create(nombrePermiso=nombre)
    permisos[nombre] = p

for perm in permisos.values():
    RolPermiso.objects.get_or_create(idRol=roles['Administrador'], idPermiso=perm)

print("Creando usuario administrador de demostración...")
admin, created = Usuario.objects.get_or_create(
    correo='admin@gestordoc.com',
    defaults=dict(nombre='Administrador Demo', idRol=roles['Administrador'], estado='activo'),
)
admin.set_password('Admin2024*')
admin.is_staff = True
admin.is_superuser = True
admin.save()

otros = [
    ('editor@gestordoc.com', 'Laura Editor', roles['Editor']),
    ('revisor@gestordoc.com', 'Carlos Revisor', roles['Revisor']),
    ('visualizador@gestordoc.com', 'Marta Visualizador', roles['Visualizador']),
]
for correo, nombre, rol in otros:
    u, _ = Usuario.objects.get_or_create(correo=correo, defaults=dict(nombre=nombre, idRol=rol, estado='activo'))
    u.set_password('Demo2024*')
    u.save()

print("Creando clasificaciones...")
clasif_data = [
    ('Administrativo', 'Documentos de gestión administrativa'),
    ('Técnico', 'Documentos técnicos del proyecto'),
    ('Financiero', 'Documentos de presupuesto y finanzas'),
    ('Contractual', 'Contratos y acuerdos'),
    ('Académico', 'Documentos académicos y de formación'),
    ('Legal', 'Documentos de carácter legal'),
]
clasifs = {}
for nombre, desc in clasif_data:
    c, _ = ClasificacionDocumento.objects.get_or_create(nombreClasificacion=nombre, defaults=dict(descripcion=desc))
    clasifs[nombre] = c

print("Creando documentos de demostración...")
docs_data = [
    ('Manual de procedimientos administrativos', 'Administrativo', 'activo'),
    ('Acta de reunión del comité técnico', 'Técnico', 'activo'),
    ('Presupuesto anual 2026', 'Financiero', 'revision'),
    ('Contrato de prestación de servicios N.º 014', 'Contractual', 'activo'),
    ('Informe de avance del proyecto formativo', 'Académico', 'activo'),
    ('Reglamento interno de trabajo', 'Legal', 'archivado'),
    ('Plan de mejoramiento institucional', 'Administrativo', 'activo'),
    ('Especificación técnica del módulo de reportes', 'Técnico', 'revision'),
    ('Estados financieros trimestrales', 'Financiero', 'activo'),
    ('Otrosí al contrato N.º 014', 'Contractual', 'inactivo'),
    ('Guía de aprendizaje N.º 9', 'Académico', 'activo'),
    ('Política de tratamiento de datos personales', 'Legal', 'activo'),
]
docs = []
for titulo, clasif, estado in docs_data:
    d, _ = Documento.objects.get_or_create(
        titulo=titulo,
        defaults=dict(descripcion=f'Documento de demostración: {titulo.lower()}.',
                      estado=estado, idUsuario=admin, idClasificacion=clasifs[clasif]),
    )
    docs.append(d)

print("Registrando historial de demostración...")
for d in docs:
    HistorialDocumento.objects.get_or_create(idDocumento=d, idUsuario=admin, accion='Documento creado')

doc_revision = docs[2]  # Presupuesto anual 2026, en revisión
RevisionDocumento.objects.get_or_create(
    idDocumento=doc_revision, idUsuario=admin,
    defaults=dict(comentario='Revisión de demostración: pendiente de aprobación del área financiera.'),
)
HistorialDocumento.objects.get_or_create(idDocumento=doc_revision, idUsuario=admin, accion='Revisión agregada')

print(f"Listo. Usuarios: {Usuario.objects.count()} | Clasificaciones: {ClasificacionDocumento.objects.count()} "
      f"| Documentos: {Documento.objects.count()} | Historial: {HistorialDocumento.objects.count()}")
