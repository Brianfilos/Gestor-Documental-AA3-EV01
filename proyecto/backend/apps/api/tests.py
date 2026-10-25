"""
PRUEBAS DEL MÓDULO API REST (M9) — punto de integración entre el backend Django
y la aplicación móvil Android.

Cada prueba documenta:
    - Datos de entrada  : petición HTTP (método, ruta, cuerpo, token).
    - Salida esperada   : código de estado y estructura JSON devuelta.
"""
from rest_framework.test import APITestCase

from apps.usuarios.models import Usuario, Rol
from apps.documentos.models import Documento, ClasificacionDocumento, HistorialDocumento


class BaseAPITest(APITestCase):
    """Datos comunes y obtención del token JWT usado por la app Android."""

    @classmethod
    def setUpTestData(cls):
        cls.rol = Rol.objects.create(nombreRol='Administrador')
        cls.usuario = Usuario.objects.create_user(
            correo='admin@gestordoc.com', nombre='Administrador',
            password='Admin2024*', idRol=cls.rol, estado='activo',
        )
        cls.clasificacion = ClasificacionDocumento.objects.create(
            nombreClasificacion='Administrativo', descripcion='Gestión administrativa',
        )
        cls.documento = Documento.objects.create(
            titulo='Manual de procedimientos', descripcion='Documento base',
            estado='activo', idUsuario=cls.usuario, idClasificacion=cls.clasificacion,
        )

    def autenticar(self):
        """Obtiene el token JWT y lo deja configurado en la cabecera Authorization."""
        respuesta = self.client.post('/api/auth/login/', {
            'correo': 'admin@gestordoc.com', 'password': 'Admin2024*',
        }, format='json')
        token = respuesta.data['access']
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {token}')
        return respuesta


class PruebasAutenticacionAPI(BaseAPITest):
    """M9.1 - Autenticación JWT (módulo M1 sobre la capa de servicios)."""

    def test_login_devuelve_tokens_y_datos_del_usuario(self):
        """Entrada: {correo, password} → Salida: 200 con access, refresh y objeto usuario."""
        respuesta = self.autenticar()
        self.assertEqual(respuesta.status_code, 200)
        self.assertIn('access', respuesta.data)
        self.assertIn('refresh', respuesta.data)
        self.assertEqual(respuesta.data['usuario']['correo'], 'admin@gestordoc.com')
        self.assertEqual(respuesta.data['usuario']['rol'], 'Administrador')

    def test_login_con_credenciales_invalidas(self):
        """Entrada: contraseña incorrecta → Salida: 401 Unauthorized."""
        respuesta = self.client.post('/api/auth/login/', {
            'correo': 'admin@gestordoc.com', 'password': 'incorrecta',
        }, format='json')
        self.assertEqual(respuesta.status_code, 401)

    def test_endpoint_protegido_sin_token(self):
        """Entrada: GET /api/documentos/ sin token → Salida: 401 Unauthorized."""
        respuesta = self.client.get('/api/documentos/')
        self.assertEqual(respuesta.status_code, 401)

    def test_refresh_token_renueva_el_access(self):
        """Entrada: refresh token válido → Salida: 200 con un nuevo access token."""
        login = self.client.post('/api/auth/login/', {
            'correo': 'admin@gestordoc.com', 'password': 'Admin2024*',
        }, format='json')
        respuesta = self.client.post('/api/auth/refresh/',
                                     {'refresh': login.data['refresh']}, format='json')
        self.assertEqual(respuesta.status_code, 200)
        self.assertIn('access', respuesta.data)

    def test_usuario_actual_me(self):
        """Entrada: GET /api/usuarios/me/ con token → Salida: 200 con los datos del usuario en sesión."""
        self.autenticar()
        respuesta = self.client.get('/api/usuarios/me/')
        self.assertEqual(respuesta.status_code, 200)
        self.assertEqual(respuesta.data['correo'], 'admin@gestordoc.com')


class PruebasDocumentosAPI(BaseAPITest):
    """M9.2 - CRUD de documentos consumido por la app Android (módulos M3 y M4)."""

    def setUp(self):
        self.autenticar()

    def test_listar_documentos_paginado(self):
        """Entrada: GET /api/documentos/ → Salida: 200 con count, next, previous y results."""
        respuesta = self.client.get('/api/documentos/')
        self.assertEqual(respuesta.status_code, 200)
        for campo in ('count', 'next', 'previous', 'results'):
            self.assertIn(campo, respuesta.data)
        self.assertEqual(respuesta.data['count'], 1)

    def test_crear_documento_asigna_usuario_y_registra_historial(self):
        """Entrada: JSON con título, estado y clasificación → Salida: 201 y traza en historial."""
        respuesta = self.client.post('/api/documentos/', {
            'titulo': 'Documento desde Android',
            'descripcion': 'Creado desde la app móvil',
            'estado': 'activo',
            'idClasificacion': self.clasificacion.idClasificacion,
        }, format='json')
        self.assertEqual(respuesta.status_code, 201)
        doc = Documento.objects.get(titulo='Documento desde Android')
        self.assertEqual(doc.idUsuario, self.usuario)
        self.assertTrue(
            HistorialDocumento.objects.filter(idDocumento=doc, accion='Documento creado').exists()
        )

    def test_consultar_documento_por_id(self):
        """Entrada: GET /api/documentos/<id>/ → Salida: 200 con los datos del documento."""
        respuesta = self.client.get(f'/api/documentos/{self.documento.pk}/')
        self.assertEqual(respuesta.status_code, 200)
        self.assertEqual(respuesta.data['titulo'], 'Manual de procedimientos')
        self.assertEqual(respuesta.data['clasificacion_nombre'], 'Administrativo')

    def test_actualizar_documento(self):
        """Entrada: PUT con los campos modificados → Salida: 200 y cambio persistido."""
        respuesta = self.client.put(f'/api/documentos/{self.documento.pk}/', {
            'titulo': 'Manual actualizado',
            'descripcion': 'Actualizado desde la app móvil',
            'estado': 'activo',
            'idClasificacion': self.clasificacion.idClasificacion,
        }, format='json')
        self.assertEqual(respuesta.status_code, 200)
        self.documento.refresh_from_db()
        self.assertEqual(self.documento.titulo, 'Manual actualizado')

    def test_eliminar_documento(self):
        """Entrada: DELETE /api/documentos/<id>/ → Salida: 204 y registro eliminado."""
        doc = Documento.objects.create(
            titulo='Temporal', estado='activo',
            idUsuario=self.usuario, idClasificacion=self.clasificacion,
        )
        respuesta = self.client.delete(f'/api/documentos/{doc.pk}/')
        self.assertEqual(respuesta.status_code, 204)
        self.assertFalse(Documento.objects.filter(pk=doc.pk).exists())

    def test_busqueda_y_filtros_por_parametros(self):
        """Entrada: ?q= y ?estado= → Salida: 200 con los resultados filtrados."""
        Documento.objects.create(
            titulo='Informe financiero', estado='archivado',
            idUsuario=self.usuario, idClasificacion=self.clasificacion,
        )
        por_texto = self.client.get('/api/documentos/', {'q': 'Informe'})
        self.assertEqual(por_texto.data['count'], 1)

        por_estado = self.client.get('/api/documentos/', {'estado': 'archivado'})
        self.assertEqual(por_estado.data['count'], 1)


class PruebasRevisionesEHistorialAPI(BaseAPITest):
    """M9.3 - Revisiones e historial expuestos a la app móvil (módulos M7 y M8)."""

    def setUp(self):
        self.autenticar()

    def test_historial_de_un_documento(self):
        """Entrada: GET /api/documentos/<id>/historial/ → Salida: 200 con la lista de acciones."""
        HistorialDocumento.objects.create(idDocumento=self.documento, idUsuario=self.usuario,
                                          accion='Documento creado')
        respuesta = self.client.get(f'/api/documentos/{self.documento.pk}/historial/')
        self.assertEqual(respuesta.status_code, 200)
        self.assertEqual(respuesta.data[0]['accion'], 'Documento creado')

    def test_agregar_revision_cambia_estado_del_documento(self):
        """Entrada: POST con comentario → Salida: 201 y documento en estado 'revision'."""
        respuesta = self.client.post(f'/api/documentos/{self.documento.pk}/revisiones/',
                                     {'comentario': 'Revisión desde la app móvil'}, format='json')
        self.assertEqual(respuesta.status_code, 201)
        self.documento.refresh_from_db()
        self.assertEqual(self.documento.estado, 'revision')

    def test_listar_revisiones_de_un_documento(self):
        """Entrada: GET /api/documentos/<id>/revisiones/ → Salida: 200 con las revisiones."""
        self.client.post(f'/api/documentos/{self.documento.pk}/revisiones/',
                         {'comentario': 'Primera revisión'}, format='json')
        respuesta = self.client.get(f'/api/documentos/{self.documento.pk}/revisiones/')
        self.assertEqual(respuesta.status_code, 200)
        self.assertEqual(len(respuesta.data), 1)
        self.assertEqual(respuesta.data[0]['usuario_nombre'], 'Administrador')

    def test_historial_global(self):
        """Entrada: GET /api/historial/ → Salida: 200 con el historial paginado del sistema."""
        HistorialDocumento.objects.create(idDocumento=self.documento, idUsuario=self.usuario,
                                          accion='Documento actualizado')
        respuesta = self.client.get('/api/historial/')
        self.assertEqual(respuesta.status_code, 200)
        self.assertEqual(respuesta.data['count'], 1)


class PruebasCatalogosAPI(BaseAPITest):
    """M9.4 - Catálogos: clasificaciones, usuarios y roles (módulos M5 y M6)."""

    def setUp(self):
        self.autenticar()

    def test_listar_clasificaciones(self):
        """Entrada: GET /api/clasificaciones/ → Salida: 200 con el catálogo de clasificaciones."""
        respuesta = self.client.get('/api/clasificaciones/')
        self.assertEqual(respuesta.status_code, 200)
        self.assertEqual(respuesta.data['results'][0]['nombreClasificacion'], 'Administrativo')

    def test_listar_usuarios(self):
        """Entrada: GET /api/usuarios/ → Salida: 200 con los usuarios y su rol."""
        respuesta = self.client.get('/api/usuarios/')
        self.assertEqual(respuesta.status_code, 200)
        self.assertEqual(respuesta.data['results'][0]['rol_nombre'], 'Administrador')

    def test_listar_roles(self):
        """Entrada: GET /api/roles/ → Salida: 200 con los roles definidos en el sistema."""
        respuesta = self.client.get('/api/roles/')
        self.assertEqual(respuesta.status_code, 200)
        self.assertEqual(respuesta.data['results'][0]['nombreRol'], 'Administrador')
