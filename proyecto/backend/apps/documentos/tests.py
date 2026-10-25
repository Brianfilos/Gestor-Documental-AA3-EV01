"""
PRUEBAS DE LOS MÓDULOS DE DOCUMENTOS, CLASIFICACIONES, REVISIONES E HISTORIAL
(M2, M3, M4, M6, M7 y M8)

Cada prueba documenta:
    - Datos de entrada  : lo que recibe el módulo.
    - Salida esperada   : lo que debe devolver el módulo.
"""
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase
from django.urls import reverse

from apps.usuarios.models import Usuario, Rol
from .models import Documento, ClasificacionDocumento, HistorialDocumento, RevisionDocumento


class BaseDocumentosTest(TestCase):
    """Datos comunes: rol, usuario autenticado, clasificación y un documento base."""

    @classmethod
    def setUpTestData(cls):
        cls.rol = Rol.objects.create(nombreRol='Administrador')
        cls.usuario = Usuario.objects.create_user(
            correo='admin@gestordoc.com', nombre='Administrador',
            password='Admin2024*', idRol=cls.rol, estado='activo',
        )
        cls.clasificacion = ClasificacionDocumento.objects.create(
            nombreClasificacion='Administrativo',
            descripcion='Documentos de gestión administrativa',
        )
        cls.clasificacion_tec = ClasificacionDocumento.objects.create(
            nombreClasificacion='Técnico', descripcion='Documentos técnicos',
        )
        cls.documento = Documento.objects.create(
            titulo='Manual de procedimientos',
            descripcion='Documento base de pruebas',
            estado='activo',
            idUsuario=cls.usuario,
            idClasificacion=cls.clasificacion,
        )

    def setUp(self):
        self.client.force_login(self.usuario)


class PruebasGestionDocumentos(BaseDocumentosTest):
    """MÓDULO M3 - Gestión de documentos (CRUD)."""

    def test_listar_documentos(self):
        """Entrada: GET /documentos/ → Salida: 200 con el documento registrado."""
        respuesta = self.client.get(reverse('documento_list'))
        self.assertEqual(respuesta.status_code, 200)
        self.assertContains(respuesta, 'Manual de procedimientos')

    def test_crear_documento_registra_historial(self):
        """Entrada: título, descripción, estado y clasificación → Salida: documento + historial."""
        respuesta = self.client.post(reverse('documento_create'), {
            'titulo': 'Contrato de servicios',
            'descripcion': 'Contrato firmado con proveedor',
            'estado': 'activo',
            'idClasificacion': self.clasificacion.idClasificacion,
        })
        self.assertRedirects(respuesta, reverse('documento_list'))
        doc = Documento.objects.get(titulo='Contrato de servicios')
        self.assertEqual(doc.idUsuario, self.usuario)
        self.assertTrue(doc.historial.filter(accion='Documento creado').exists())

    def test_crear_documento_con_archivo_adjunto(self):
        """Entrada: formulario con archivo PDF → Salida: archivo almacenado en media/documentos/."""
        archivo = SimpleUploadedFile('acta.pdf', b'%PDF-1.4 contenido de prueba',
                                     content_type='application/pdf')
        self.client.post(reverse('documento_create'), {
            'titulo': 'Acta de reunión',
            'descripcion': 'Acta con archivo adjunto',
            'estado': 'activo',
            'idClasificacion': self.clasificacion.idClasificacion,
            'archivo': archivo,
        })
        doc = Documento.objects.get(titulo='Acta de reunión')
        self.assertIn('documentos/', doc.archivo.name)

    def test_ver_detalle_documento(self):
        """Entrada: GET /documentos/<id>/ → Salida: 200 con título, historial y revisiones."""
        respuesta = self.client.get(reverse('documento_detail', args=[self.documento.pk]))
        self.assertEqual(respuesta.status_code, 200)
        self.assertContains(respuesta, 'Manual de procedimientos')

    def test_editar_documento_registra_historial(self):
        """Entrada: documento existente con título modificado → Salida: cambio + traza en historial."""
        self.client.post(reverse('documento_edit', args=[self.documento.pk]), {
            'titulo': 'Manual de procedimientos v2',
            'descripcion': 'Documento base de pruebas',
            'estado': 'activo',
            'idClasificacion': self.clasificacion.idClasificacion,
        })
        self.documento.refresh_from_db()
        self.assertEqual(self.documento.titulo, 'Manual de procedimientos v2')
        self.assertTrue(self.documento.historial.filter(accion='Documento actualizado').exists())

    def test_eliminar_documento(self):
        """Entrada: POST a /documentos/<id>/eliminar/ → Salida: documento eliminado de la BD."""
        doc = Documento.objects.create(
            titulo='Documento temporal', estado='activo',
            idUsuario=self.usuario, idClasificacion=self.clasificacion,
        )
        self.client.post(reverse('documento_delete', args=[doc.pk]))
        self.assertFalse(Documento.objects.filter(pk=doc.pk).exists())

    def test_eliminar_documento_elimina_su_historial_en_cascada(self):
        """Entrada: documento con historial → Salida: historial eliminado en cascada (ON DELETE CASCADE)."""
        doc = Documento.objects.create(
            titulo='Documento con traza', estado='activo',
            idUsuario=self.usuario, idClasificacion=self.clasificacion,
        )
        HistorialDocumento.objects.create(idDocumento=doc, idUsuario=self.usuario,
                                          accion='Documento creado')
        doc.delete()
        self.assertEqual(HistorialDocumento.objects.filter(idDocumento_id=doc.pk).count(), 0)


class PruebasBusquedaYFiltros(BaseDocumentosTest):
    """MÓDULO M4 - Búsqueda y filtros."""

    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()
        Documento.objects.create(
            titulo='Informe financiero', descripcion='Balance anual', estado='archivado',
            idUsuario=cls.usuario, idClasificacion=cls.clasificacion_tec,
        )

    def test_busqueda_por_titulo(self):
        """Entrada: ?q=Informe → Salida: solo los documentos cuyo título contiene el término."""
        respuesta = self.client.get(reverse('documento_list'), {'q': 'Informe'})
        self.assertContains(respuesta, 'Informe financiero')
        self.assertNotContains(respuesta, 'Manual de procedimientos')

    def test_filtro_por_estado(self):
        """Entrada: ?estado=archivado → Salida: únicamente documentos en ese estado."""
        respuesta = self.client.get(reverse('documento_list'), {'estado': 'archivado'})
        self.assertEqual(len(respuesta.context['documentos']), 1)
        self.assertEqual(respuesta.context['documentos'][0].estado, 'archivado')

    def test_filtro_por_clasificacion(self):
        """Entrada: ?clasificacion=<id> → Salida: documentos de esa clasificación."""
        respuesta = self.client.get(reverse('documento_list'),
                                    {'clasificacion': self.clasificacion_tec.idClasificacion})
        self.assertEqual(len(respuesta.context['documentos']), 1)
        self.assertEqual(respuesta.context['documentos'][0].titulo, 'Informe financiero')


class PruebasClasificaciones(BaseDocumentosTest):
    """MÓDULO M6 - Clasificaciones documentales."""

    def test_listar_clasificaciones(self):
        """Entrada: GET /clasificaciones/ → Salida: 200 con las clasificaciones registradas."""
        respuesta = self.client.get(reverse('clasificacion_list'))
        self.assertEqual(respuesta.status_code, 200)
        self.assertContains(respuesta, 'Administrativo')

    def test_crear_clasificacion(self):
        """Entrada: nombre y descripción → Salida: clasificación persistida en la BD."""
        self.client.post(reverse('clasificacion_create'), {
            'nombreClasificacion': 'Legal',
            'descripcion': 'Documentos legales y contratos',
        })
        self.assertTrue(
            ClasificacionDocumento.objects.filter(nombreClasificacion='Legal').exists()
        )

    def test_editar_clasificacion(self):
        """Entrada: clasificación existente con descripción modificada → Salida: cambio persistido."""
        self.client.post(reverse('clasificacion_edit', args=[self.clasificacion.pk]), {
            'nombreClasificacion': 'Administrativo',
            'descripcion': 'Descripción actualizada',
        })
        self.clasificacion.refresh_from_db()
        self.assertEqual(self.clasificacion.descripcion, 'Descripción actualizada')


class PruebasRevisionesEHistorial(BaseDocumentosTest):
    """MÓDULOS M7 (revisiones) y M8 (historial y trazabilidad)."""

    def test_registrar_revision_cambia_estado_a_revision(self):
        """Entrada: comentario de revisión → Salida: revisión creada y documento en estado 'revision'."""
        self.client.post(reverse('revision_create', args=[self.documento.pk]), {
            'comentario': 'Se solicita corregir la numeración de páginas.',
        })
        self.documento.refresh_from_db()
        self.assertEqual(self.documento.estado, 'revision')
        self.assertEqual(self.documento.revisiones.count(), 1)
        self.assertTrue(self.documento.historial.filter(accion='Revisión agregada').exists())

    def test_historial_global_muestra_las_acciones(self):
        """Entrada: GET /historial/ → Salida: 200 con las acciones registradas sobre documentos."""
        HistorialDocumento.objects.create(idDocumento=self.documento, idUsuario=self.usuario,
                                          accion='Documento creado')
        respuesta = self.client.get(reverse('historial_list'))
        self.assertEqual(respuesta.status_code, 200)
        self.assertContains(respuesta, 'Documento creado')

    def test_historial_se_ordena_del_mas_reciente_al_mas_antiguo(self):
        """Entrada: dos acciones consecutivas → Salida: la más reciente aparece primero."""
        HistorialDocumento.objects.create(idDocumento=self.documento, idUsuario=self.usuario,
                                          accion='Documento creado')
        HistorialDocumento.objects.create(idDocumento=self.documento, idUsuario=self.usuario,
                                          accion='Documento actualizado')
        registros = list(HistorialDocumento.objects.all())
        self.assertEqual(registros[0].accion, 'Documento actualizado')

    def test_revision_queda_asociada_al_usuario_que_la_realiza(self):
        """Entrada: revisión creada por el usuario en sesión → Salida: revisión con ese autor."""
        self.client.post(reverse('revision_create', args=[self.documento.pk]),
                         {'comentario': 'Revisión de contenido aprobada.'})
        revision = RevisionDocumento.objects.get(idDocumento=self.documento)
        self.assertEqual(revision.idUsuario, self.usuario)


class PruebasDashboard(BaseDocumentosTest):
    """MÓDULO M2 - Dashboard / panel de control."""

    def test_dashboard_calcula_los_indicadores(self):
        """Entrada: GET /dashboard/ → Salida: totales de documentos, activos y usuarios."""
        respuesta = self.client.get(reverse('dashboard'))
        self.assertEqual(respuesta.status_code, 200)
        self.assertEqual(respuesta.context['total_docs'], Documento.objects.count())
        self.assertEqual(respuesta.context['docs_activos'],
                         Documento.objects.filter(estado='activo').count())
        self.assertEqual(respuesta.context['total_usuarios'], Usuario.objects.count())

    def test_dashboard_lista_maximo_cinco_documentos_recientes(self):
        """Entrada: 8 documentos registrados → Salida: la tabla de recientes muestra 5."""
        for i in range(7):
            Documento.objects.create(
                titulo=f'Documento {i}', estado='activo',
                idUsuario=self.usuario, idClasificacion=self.clasificacion,
            )
        respuesta = self.client.get(reverse('dashboard'))
        self.assertEqual(len(respuesta.context['docs_recientes']), 5)
