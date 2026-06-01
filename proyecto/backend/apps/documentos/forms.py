from django import forms
from .models import Documento, ClasificacionDocumento, RevisionDocumento


class DocumentoForm(forms.ModelForm):
    class Meta:
        model = Documento
        fields = ['titulo', 'descripcion', 'estado', 'idClasificacion', 'archivo']
        widgets = {
            'titulo': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Título del documento'}),
            'descripcion': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Descripción'}),
            'estado': forms.Select(attrs={'class': 'form-select'}),
            'idClasificacion': forms.Select(attrs={'class': 'form-select'}),
            'archivo': forms.FileInput(attrs={'class': 'form-control'}),
        }
        labels = {
            'titulo': 'Título',
            'descripcion': 'Descripción',
            'estado': 'Estado',
            'idClasificacion': 'Clasificación',
            'archivo': 'Archivo',
        }


class ClasificacionForm(forms.ModelForm):
    class Meta:
        model = ClasificacionDocumento
        fields = ['nombreClasificacion', 'descripcion']
        widgets = {
            'nombreClasificacion': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nombre'}),
            'descripcion': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Descripción'}),
        }
        labels = {
            'nombreClasificacion': 'Nombre de clasificación',
            'descripcion': 'Descripción',
        }


class RevisionForm(forms.ModelForm):
    class Meta:
        model = RevisionDocumento
        fields = ['comentario']
        widgets = {
            'comentario': forms.Textarea(attrs={'class': 'form-control', 'rows': 3,
                                                 'placeholder': 'Escriba su comentario de revisión...'}),
        }
        labels = {
            'comentario': 'Comentario',
        }
