"""
PRUEBAS DEL MÓDULO DE USUARIOS Y AUTENTICACIÓN (M1 y M5)

Cada prueba documenta:
    - Datos de entrada  : lo que recibe el módulo.
    - Salida esperada   : lo que debe devolver el módulo.
"""
from django.test import TestCase
from django.urls import reverse

from .models import Usuario, Rol, Permiso, RolPermiso


class BaseUsuariosTest(TestCase):
    """Datos comunes: roles, permisos y usuario administrador."""

    @classmethod
    def setUpTestData(cls):
        cls.rol_admin = Rol.objects.create(nombreRol='Administrador')
        cls.rol_editor = Rol.objects.create(nombreRol='Editor')
        cls.permiso = Permiso.objects.create(nombrePermiso='Ver documentos')
        RolPermiso.objects.create(idRol=cls.rol_admin, idPermiso=cls.permiso)

        cls.admin = Usuario.objects.create_user(
            correo='admin@gestordoc.com',
            nombre='Administrador',
            password='Admin2024*',
            idRol=cls.rol_admin,
            estado='activo',
        )


class PruebasAutenticacion(BaseUsuariosTest):
    """MÓDULO M1 - Autenticación y control de acceso."""

    def test_login_con_credenciales_validas_redirige_al_dashboard(self):
        """Entrada: correo y contraseña válidos → Salida: redirección 302 a /dashboard/."""
        respuesta = self.client.post(reverse('login'), {
            'username': 'admin@gestordoc.com',
            'password': 'Admin2024*',
        })
        self.assertRedirects(respuesta, reverse('dashboard'))

    def test_login_con_credenciales_invalidas_muestra_error(self):
        """Entrada: contraseña incorrecta → Salida: 200 con mensaje de error y sin sesión."""
        respuesta = self.client.post(reverse('login'), {
            'username': 'admin@gestordoc.com',
            'password': 'clave-incorrecta',
        })
        self.assertEqual(respuesta.status_code, 200)
        self.assertFalse(respuesta.wsgi_request.user.is_authenticated)

    def test_acceso_sin_sesion_es_redirigido_al_login(self):
        """Entrada: petición a /dashboard/ sin sesión → Salida: redirección a /login/."""
        respuesta = self.client.get(reverse('dashboard'))
        self.assertEqual(respuesta.status_code, 302)
        self.assertIn('/login/', respuesta.url)

    def test_logout_cierra_la_sesion(self):
        """Entrada: sesión activa + petición a /logout/ → Salida: redirección a /login/."""
        self.client.force_login(self.admin)
        respuesta = self.client.get(reverse('logout'))
        self.assertRedirects(respuesta, reverse('login'))

    def test_contrasena_se_almacena_cifrada(self):
        """Entrada: usuario creado con contraseña plana → Salida: hash distinto al texto plano."""
        self.assertNotEqual(self.admin.password, 'Admin2024*')
        self.assertTrue(self.admin.check_password('Admin2024*'))


class PruebasGestionUsuarios(BaseUsuariosTest):
    """MÓDULO M5 - Gestión de usuarios y roles (CRUD)."""

    def setUp(self):
        self.client.force_login(self.admin)

    def test_listar_usuarios(self):
        """Entrada: GET /usuarios/ → Salida: 200 y listado con el usuario administrador."""
        respuesta = self.client.get(reverse('usuario_list'))
        self.assertEqual(respuesta.status_code, 200)
        self.assertContains(respuesta, 'admin@gestordoc.com')

    def test_crear_usuario(self):
        """Entrada: nombre, correo, contraseña, estado y rol → Salida: usuario persistido en BD."""
        respuesta = self.client.post(reverse('usuario_create'), {
            'nombre': 'Editor de Prueba',
            'correo': 'editor@gestordoc.com',
            'password': 'Editor2024*',
            'estado': 'activo',
            'idRol': self.rol_editor.idRol,
        })
        self.assertRedirects(respuesta, reverse('usuario_list'))
        self.assertTrue(Usuario.objects.filter(correo='editor@gestordoc.com').exists())

    def test_editar_usuario(self):
        """Entrada: usuario existente con nombre modificado → Salida: nombre actualizado en BD."""
        usuario = Usuario.objects.create_user(
            correo='revisor@gestordoc.com', nombre='Revisor', password='Rev2024*',
            idRol=self.rol_editor, estado='activo',
        )
        self.client.post(reverse('usuario_edit', args=[usuario.pk]), {
            'nombre': 'Revisor Actualizado',
            'correo': 'revisor@gestordoc.com',
            'estado': 'activo',
            'idRol': self.rol_editor.idRol,
            'password': '',
        })
        usuario.refresh_from_db()
        self.assertEqual(usuario.nombre, 'Revisor Actualizado')

    def test_eliminar_usuario(self):
        """Entrada: POST a /usuarios/<id>/eliminar/ → Salida: registro eliminado de la BD."""
        usuario = Usuario.objects.create_user(
            correo='temporal@gestordoc.com', nombre='Temporal', password='Temp2024*',
            idRol=self.rol_editor, estado='activo',
        )
        self.client.post(reverse('usuario_delete', args=[usuario.pk]))
        self.assertFalse(Usuario.objects.filter(pk=usuario.pk).exists())

    def test_correo_debe_ser_unico(self):
        """Entrada: dos usuarios con el mismo correo → Salida: la restricción UNIQUE lo impide."""
        from django.db import IntegrityError, transaction
        with self.assertRaises(IntegrityError):
            with transaction.atomic():
                Usuario.objects.create_user(
                    correo='admin@gestordoc.com', nombre='Duplicado', password='Dup2024*',
                )

    def test_rol_tiene_permisos_asociados(self):
        """Entrada: rol Administrador → Salida: al menos un permiso asociado (rol_permiso)."""
        self.assertEqual(self.rol_admin.permisos.count(), 1)
