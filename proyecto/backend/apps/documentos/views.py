from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q
from .models import Documento, ClasificacionDocumento, HistorialDocumento, RevisionDocumento
from .forms import DocumentoForm, ClasificacionForm, RevisionForm


def _registrar_historial(documento, usuario, accion):
    HistorialDocumento.objects.create(
        idDocumento=documento,
        idUsuario=usuario,
        accion=accion
    )


@login_required
def documento_list(request):
    query = request.GET.get('q', '')
    clasificacion = request.GET.get('clasificacion', '')
    estado = request.GET.get('estado', '')

    documentos = Documento.objects.select_related('idUsuario', 'idClasificacion').all()

    if query:
        documentos = documentos.filter(
            Q(titulo__icontains=query) | Q(descripcion__icontains=query)
        )
    if clasificacion:
        documentos = documentos.filter(idClasificacion__idClasificacion=clasificacion)
    if estado:
        documentos = documentos.filter(estado=estado)

    clasificaciones = ClasificacionDocumento.objects.all()
    context = {
        'documentos': documentos,
        'clasificaciones': clasificaciones,
        'query': query,
        'clasificacion_sel': clasificacion,
        'estado_sel': estado,
    }
    return render(request, 'documentos/lista.html', context)


@login_required
def documento_detail(request, pk):
    documento = get_object_or_404(Documento.objects.select_related('idUsuario', 'idClasificacion'), pk=pk)
    historial = documento.historial.select_related('idUsuario').all()
    revisiones = documento.revisiones.select_related('idUsuario').all()
    form_revision = RevisionForm()
    return render(request, 'documentos/detalle.html', {
        'documento': documento,
        'historial': historial,
        'revisiones': revisiones,
        'form_revision': form_revision,
    })


@login_required
def documento_create(request):
    if request.method == 'POST':
        form = DocumentoForm(request.POST, request.FILES)
        if form.is_valid():
            doc = form.save(commit=False)
            doc.idUsuario = request.user
            doc.save()
            _registrar_historial(doc, request.user, 'Documento creado')
            messages.success(request, 'Documento creado correctamente.')
            return redirect('documento_list')
    else:
        form = DocumentoForm()
    return render(request, 'documentos/formulario.html', {'form': form, 'accion': 'Crear'})


@login_required
def documento_edit(request, pk):
    documento = get_object_or_404(Documento, pk=pk)
    if request.method == 'POST':
        form = DocumentoForm(request.POST, request.FILES, instance=documento)
        if form.is_valid():
            form.save()
            _registrar_historial(documento, request.user, 'Documento actualizado')
            messages.success(request, 'Documento actualizado correctamente.')
            return redirect('documento_list')
    else:
        form = DocumentoForm(instance=documento)
    return render(request, 'documentos/formulario.html', {'form': form, 'accion': 'Editar', 'objeto': documento})


@login_required
def documento_delete(request, pk):
    documento = get_object_or_404(Documento, pk=pk)
    if request.method == 'POST':
        documento.delete()
        messages.success(request, 'Documento eliminado correctamente.')
        return redirect('documento_list')
    return render(request, 'documentos/confirmar_eliminar.html', {'objeto': documento, 'tipo': 'documento'})


@login_required
def revision_create(request, pk):
    documento = get_object_or_404(Documento, pk=pk)
    if request.method == 'POST':
        form = RevisionForm(request.POST)
        if form.is_valid():
            revision = form.save(commit=False)
            revision.idDocumento = documento
            revision.idUsuario = request.user
            revision.save()
            documento.estado = 'revision'
            documento.save()
            _registrar_historial(documento, request.user, 'Revisión agregada')
            messages.success(request, 'Revisión registrada correctamente.')
    return redirect('documento_detail', pk=pk)


@login_required
def clasificacion_list(request):
    clasificaciones = ClasificacionDocumento.objects.all()
    return render(request, 'documentos/clasificaciones.html', {'clasificaciones': clasificaciones})


@login_required
def clasificacion_create(request):
    if request.method == 'POST':
        form = ClasificacionForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Clasificación creada correctamente.')
            return redirect('clasificacion_list')
    else:
        form = ClasificacionForm()
    return render(request, 'documentos/clasificacion_form.html', {'form': form, 'accion': 'Crear'})


@login_required
def clasificacion_edit(request, pk):
    clasificacion = get_object_or_404(ClasificacionDocumento, pk=pk)
    if request.method == 'POST':
        form = ClasificacionForm(request.POST, instance=clasificacion)
        if form.is_valid():
            form.save()
            messages.success(request, 'Clasificación actualizada.')
            return redirect('clasificacion_list')
    else:
        form = ClasificacionForm(instance=clasificacion)
    return render(request, 'documentos/clasificacion_form.html', {'form': form, 'accion': 'Editar'})


@login_required
def historial_list(request):
    historial = HistorialDocumento.objects.select_related('idDocumento', 'idUsuario').all()
    return render(request, 'documentos/historial.html', {'historial': historial})
