from rest_framework import serializers
from apps.usuarios.models import Usuario, Rol, Permiso
from apps.documentos.models import Documento, ClasificacionDocumento, HistorialDocumento, RevisionDocumento


class RolSerializer(serializers.ModelSerializer):
    class Meta:
        model = Rol
        fields = ['idRol', 'nombreRol']


class UsuarioSerializer(serializers.ModelSerializer):
    rol_nombre = serializers.CharField(source='idRol.nombreRol', read_only=True)

    class Meta:
        model = Usuario
        fields = ['idUsuario', 'nombre', 'correo', 'estado', 'idRol', 'rol_nombre']


class UsuarioCreateSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=6)

    class Meta:
        model = Usuario
        fields = ['nombre', 'correo', 'password', 'estado', 'idRol']

    def create(self, validated_data):
        password = validated_data.pop('password')
        user = Usuario(**validated_data)
        user.set_password(password)
        user.save()
        return user

    def update(self, instance, validated_data):
        password = validated_data.pop('password', None)
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        if password:
            instance.set_password(password)
        instance.save()
        return instance


class ClasificacionSerializer(serializers.ModelSerializer):
    class Meta:
        model = ClasificacionDocumento
        fields = ['idClasificacion', 'nombreClasificacion', 'descripcion']


class DocumentoSerializer(serializers.ModelSerializer):
    usuario_nombre = serializers.CharField(source='idUsuario.nombre', read_only=True)
    clasificacion_nombre = serializers.CharField(source='idClasificacion.nombreClasificacion', read_only=True)

    class Meta:
        model = Documento
        fields = ['idDocumento', 'titulo', 'descripcion', 'fechaCarga', 'estado',
                  'archivo', 'idUsuario', 'usuario_nombre', 'idClasificacion', 'clasificacion_nombre']
        read_only_fields = ['fechaCarga', 'idUsuario']

    def create(self, validated_data):
        request = self.context.get('request')
        validated_data['idUsuario'] = request.user
        return super().create(validated_data)


class HistorialSerializer(serializers.ModelSerializer):
    usuario_nombre = serializers.CharField(source='idUsuario.nombre', read_only=True)
    documento_titulo = serializers.CharField(source='idDocumento.titulo', read_only=True)

    class Meta:
        model = HistorialDocumento
        fields = ['idHistorial', 'idDocumento', 'documento_titulo', 'idUsuario',
                  'usuario_nombre', 'accion', 'fechaAccion']


class RevisionSerializer(serializers.ModelSerializer):
    usuario_nombre = serializers.CharField(source='idUsuario.nombre', read_only=True)

    class Meta:
        model = RevisionDocumento
        fields = ['idRevision', 'idDocumento', 'idUsuario', 'usuario_nombre',
                  'fechaRevision', 'comentario']
        read_only_fields = ['fechaRevision', 'idUsuario']

    def create(self, validated_data):
        request = self.context.get('request')
        validated_data['idUsuario'] = request.user
        return super().create(validated_data)
