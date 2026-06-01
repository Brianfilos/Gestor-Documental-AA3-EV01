from django.db import models
from apps.usuarios.models import Usuario


class ClasificacionDocumento(models.Model):
    idClasificacion = models.AutoField(primary_key=True)
    nombreClasificacion = models.CharField(max_length=100)
    descripcion = models.CharField(max_length=255, null=True, blank=True)

    class Meta:
        db_table = 'clasificacion_documento'
        verbose_name = 'Clasificación'
        verbose_name_plural = 'Clasificaciones'

    def __str__(self):
        return self.nombreClasificacion


class Documento(models.Model):
    ESTADO_CHOICES = [
        ('activo', 'Activo'),
        ('inactivo', 'Inactivo'),
        ('revision', 'En revisión'),
        ('archivado', 'Archivado'),
    ]

    idDocumento = models.AutoField(primary_key=True)
    titulo = models.CharField(max_length=200)
    descripcion = models.TextField(null=True, blank=True)
    fechaCarga = models.DateField(auto_now_add=True)
    estado = models.CharField(max_length=20, choices=ESTADO_CHOICES, default='activo')
    archivo = models.FileField(upload_to='documentos/', null=True, blank=True)
    idUsuario = models.ForeignKey(Usuario, on_delete=models.RESTRICT, db_column='idUsuario',
                                   related_name='documentos')
    idClasificacion = models.ForeignKey(ClasificacionDocumento, on_delete=models.RESTRICT,
                                         db_column='idClasificacion', related_name='documentos')

    class Meta:
        db_table = 'documento'
        verbose_name = 'Documento'
        verbose_name_plural = 'Documentos'
        ordering = ['-fechaCarga']

    def __str__(self):
        return self.titulo


class HistorialDocumento(models.Model):
    idHistorial = models.AutoField(primary_key=True)
    idDocumento = models.ForeignKey(Documento, on_delete=models.CASCADE, db_column='idDocumento',
                                     related_name='historial')
    idUsuario = models.ForeignKey(Usuario, on_delete=models.RESTRICT, db_column='idUsuario',
                                   related_name='historial')
    accion = models.CharField(max_length=100)
    fechaAccion = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'historial_documento'
        verbose_name = 'Historial'
        verbose_name_plural = 'Historial de Documentos'
        ordering = ['-fechaAccion']

    def __str__(self):
        return f'{self.accion} - {self.idDocumento.titulo}'


class RevisionDocumento(models.Model):
    idRevision = models.AutoField(primary_key=True)
    idDocumento = models.ForeignKey(Documento, on_delete=models.CASCADE, db_column='idDocumento',
                                     related_name='revisiones')
    idUsuario = models.ForeignKey(Usuario, on_delete=models.RESTRICT, db_column='idUsuario',
                                   related_name='revisiones')
    fechaRevision = models.DateField(auto_now_add=True)
    comentario = models.TextField(null=True, blank=True)

    class Meta:
        db_table = 'revision_documento'
        verbose_name = 'Revisión'
        verbose_name_plural = 'Revisiones'
        ordering = ['-fechaRevision']

    def __str__(self):
        return f'Revisión {self.idRevision} - {self.idDocumento.titulo}'
