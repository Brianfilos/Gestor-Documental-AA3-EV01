from rest_framework import viewsets, permissions, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from django.db.models import Q

from apps.usuarios.models import Usuario, Rol
from apps.documentos.models import Documento, ClasificacionDocumento, HistorialDocumento, RevisionDocumento
from .serializers import (
    UsuarioSerializer, UsuarioCreateSerializer, RolSerializer,
    DocumentoSerializer, ClasificacionSerializer, HistorialSerializer, RevisionSerializer
)


class CustomTokenSerializer(TokenObtainPairSerializer):
    def validate(self, attrs):
        data = super().validate(attrs)
        data['usuario'] = {
            'id': self.user.idUsuario,
            'nombre': self.user.nombre,
            'correo': self.user.correo,
            'rol': self.user.idRol.nombreRol if self.user.idRol else None,
        }
        return data


class LoginAPIView(TokenObtainPairView):
    serializer_class = CustomTokenSerializer


class RolViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Rol.objects.all()
    serializer_class = RolSerializer
    permission_classes = [permissions.IsAuthenticated]


class UsuarioViewSet(viewsets.ModelViewSet):
    queryset = Usuario.objects.select_related('idRol').all()
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [filters.SearchFilter]
    search_fields = ['nombre', 'correo']

    def get_serializer_class(self):
        if self.action in ['create', 'update', 'partial_update']:
            return UsuarioCreateSerializer
        return UsuarioSerializer

    @action(detail=False, methods=['get'])
    def me(self, request):
        serializer = UsuarioSerializer(request.user)
        return Response(serializer.data)


class ClasificacionViewSet(viewsets.ModelViewSet):
    queryset = ClasificacionDocumento.objects.all()
    serializer_class = ClasificacionSerializer
    permission_classes = [permissions.IsAuthenticated]


class DocumentoViewSet(viewsets.ModelViewSet):
    serializer_class = DocumentoSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        queryset = Documento.objects.select_related('idUsuario', 'idClasificacion').all()
        q = self.request.query_params.get('q', '')
        estado = self.request.query_params.get('estado', '')
        clasificacion = self.request.query_params.get('clasificacion', '')

        if q:
            queryset = queryset.filter(Q(titulo__icontains=q) | Q(descripcion__icontains=q))
        if estado:
            queryset = queryset.filter(estado=estado)
        if clasificacion:
            queryset = queryset.filter(idClasificacion__idClasificacion=clasificacion)
        return queryset

    def perform_create(self, serializer):
        doc = serializer.save()
        HistorialDocumento.objects.create(
            idDocumento=doc, idUsuario=self.request.user, accion='Documento creado'
        )

    def perform_update(self, serializer):
        doc = serializer.save()
        HistorialDocumento.objects.create(
            idDocumento=doc, idUsuario=self.request.user, accion='Documento actualizado'
        )

    def perform_destroy(self, instance):
        HistorialDocumento.objects.create(
            idDocumento=instance, idUsuario=self.request.user, accion='Documento eliminado'
        )
        instance.delete()

    @action(detail=True, methods=['get'])
    def historial(self, request, pk=None):
        documento = self.get_object()
        historial = documento.historial.select_related('idUsuario').all()
        serializer = HistorialSerializer(historial, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['get', 'post'])
    def revisiones(self, request, pk=None):
        documento = self.get_object()
        if request.method == 'GET':
            revisiones = documento.revisiones.select_related('idUsuario').all()
            serializer = RevisionSerializer(revisiones, many=True)
            return Response(serializer.data)
        elif request.method == 'POST':
            serializer = RevisionSerializer(data=request.data, context={'request': request})
            if serializer.is_valid():
                serializer.save(idDocumento=documento)
                documento.estado = 'revision'
                documento.save()
                HistorialDocumento.objects.create(
                    idDocumento=documento, idUsuario=request.user, accion='Revisión agregada'
                )
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class HistorialViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = HistorialDocumento.objects.select_related('idDocumento', 'idUsuario').all()
    serializer_class = HistorialSerializer
    permission_classes = [permissions.IsAuthenticated]
