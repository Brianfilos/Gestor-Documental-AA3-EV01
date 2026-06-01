from django.contrib import admin
from .models import ClasificacionDocumento, Documento, HistorialDocumento, RevisionDocumento


@admin.register(ClasificacionDocumento)
class ClasificacionAdmin(admin.ModelAdmin):
    list_display = ['idClasificacion', 'nombreClasificacion', 'descripcion']
    search_fields = ['nombreClasificacion']


@admin.register(Documento)
class DocumentoAdmin(admin.ModelAdmin):
    list_display = ['idDocumento', 'titulo', 'estado', 'fechaCarga', 'idUsuario', 'idClasificacion']
    list_filter = ['estado', 'idClasificacion', 'fechaCarga']
    search_fields = ['titulo', 'descripcion']
    date_hierarchy = 'fechaCarga'


@admin.register(HistorialDocumento)
class HistorialAdmin(admin.ModelAdmin):
    list_display = ['idHistorial', 'idDocumento', 'idUsuario', 'accion', 'fechaAccion']
    list_filter = ['accion', 'fechaAccion']
    readonly_fields = ['fechaAccion']


@admin.register(RevisionDocumento)
class RevisionAdmin(admin.ModelAdmin):
    list_display = ['idRevision', 'idDocumento', 'idUsuario', 'fechaRevision']
    readonly_fields = ['fechaRevision']
