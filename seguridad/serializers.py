"""
Serializers for Face Recognition API
"""

from rest_framework import serializers
from django.core.files.uploadedfile import InMemoryUploadedFile
from PIL import Image

from .models import Copropietarios, ReconocimientoFacial


class FaceEnrollSerializer(serializers.Serializer):
    """Serializer para enrolamiento de rostros (copropietario o inquilino)"""
    copropietario_id = serializers.IntegerField(required=False)
    inquilino_id = serializers.IntegerField(required=False)
    imagen = serializers.ImageField()

    def validate(self, attrs):
        copropietario_id = attrs.get('copropietario_id')
        inquilino_id = attrs.get('inquilino_id')
        if not copropietario_id and not inquilino_id:
            raise serializers.ValidationError("Debe proporcionar copropietario_id o inquilino_id")

        # Buscar copropietario (puede ser inquilino registrado como copropietario)
        if copropietario_id:
            try:
                copropietario = Copropietarios.objects.get(id=copropietario_id, activo=True)
            except Copropietarios.DoesNotExist:
                raise serializers.ValidationError("Copropietario no encontrado o inactivo")
        elif inquilino_id:
            try:
                copropietario = Copropietarios.objects.get(id=inquilino_id, tipo_residente="Inquilino", activo=True)
            except Copropietarios.DoesNotExist:
                raise serializers.ValidationError("Inquilino no encontrado o inactivo (debe estar registrado como copropietario tipo Inquilino)")
            attrs['copropietario_id'] = inquilino_id  # Unificar para lógica de backend
        else:
            raise serializers.ValidationError("Debe proporcionar copropietario_id o inquilino_id")

        # Validar imagen
        imagen = attrs.get('imagen')
        if not isinstance(imagen, InMemoryUploadedFile):
            raise serializers.ValidationError({"imagen": "Debe proporcionar un archivo de imagen válido"})
        if imagen.size > 5 * 1024 * 1024:
            raise serializers.ValidationError({"imagen": "La imagen no debe superar 5MB"})
        allowed_formats = ['JPEG', 'JPG', 'PNG', 'BMP', 'GIF']
        try:
            image = Image.open(imagen)
            if image.format not in allowed_formats:
                raise serializers.ValidationError({"imagen": f"Formato no soportado. Formatos permitidos: {', '.join(allowed_formats)}"})
        except Exception:
            raise serializers.ValidationError({"imagen": "Archivo de imagen inválido"})
        imagen.seek(0)

        # Verificar si ya tiene enrolamiento activo
        if ReconocimientoFacial.objects.filter(
            copropietario_id=attrs['copropietario_id'], 
            activo=True
        ).exists():
            attrs['update_existing'] = True
        else:
            attrs['update_existing'] = False
        return attrs


class FaceVerifySerializer(serializers.Serializer):
    """Serializer para verificación de rostros (copropietario o inquilino)"""
    copropietario_id = serializers.IntegerField(required=False)
    inquilino_id = serializers.IntegerField(required=False)
    imagen = serializers.ImageField()

    def validate(self, attrs):
        copropietario_id = attrs.get('copropietario_id')
        inquilino_id = attrs.get('inquilino_id')
        if not copropietario_id and not inquilino_id:
            raise serializers.ValidationError("Debe proporcionar copropietario_id o inquilino_id")

        # Buscar copropietario (puede ser inquilino registrado como copropietario)
        if copropietario_id:
            try:
                copropietario = Copropietarios.objects.get(id=copropietario_id, activo=True)
            except Copropietarios.DoesNotExist:
                raise serializers.ValidationError("Copropietario no encontrado o inactivo")
        elif inquilino_id:
            try:
                copropietario = Copropietarios.objects.get(id=inquilino_id, tipo_residente="Inquilino", activo=True)
            except Copropietarios.DoesNotExist:
                raise serializers.ValidationError("Inquilino no encontrado o inactivo (debe estar registrado como copropietario tipo Inquilino)")
            attrs['copropietario_id'] = inquilino_id  # Unificar para lógica de backend
        else:
            raise serializers.ValidationError("Debe proporcionar copropietario_id o inquilino_id")

        # Validar imagen
        imagen = attrs.get('imagen')
        if not isinstance(imagen, InMemoryUploadedFile):
            raise serializers.ValidationError({"imagen": "Debe proporcionar un archivo de imagen válido"})
        if imagen.size > 5 * 1024 * 1024:
            raise serializers.ValidationError({"imagen": "La imagen no debe superar 5MB"})
        allowed_formats = ['JPEG', 'JPG', 'PNG', 'BMP', 'GIF']
        try:
            image = Image.open(imagen)
            if image.format not in allowed_formats:
                raise serializers.ValidationError({"imagen": f"Formato no soportado. Formatos permitidos: {', '.join(allowed_formats)}"})
        except Exception:
            raise serializers.ValidationError({"imagen": "Archivo de imagen inválido"})
        imagen.seek(0)

        # Verificar enrolamiento activo
        if not ReconocimientoFacial.objects.filter(
            copropietario_id=attrs['copropietario_id'], 
            activo=True
        ).exists():
            raise serializers.ValidationError("No tiene enrolamiento facial activo")
        return attrs


class CopropietarioSerializer(serializers.ModelSerializer):
    """Serializer para información básica de copropietarios"""
    
    nombre_completo = serializers.ReadOnlyField()
    
    class Meta:
        model = Copropietarios
        fields = [
            'id', 'nombres', 'apellidos', 'nombre_completo',
            'numero_documento', 'tipo_documento', 'unidad_residencial'
        ]


class ReconocimientoFacialSerializer(serializers.ModelSerializer):
    """Serializer para información de reconocimiento facial"""
    
    copropietario = CopropietarioSerializer(read_only=True)
    
    class Meta:
        model = ReconocimientoFacial
        fields = [
            'id', 'copropietario', 'proveedor_ia', 'activo',
            'fecha_enrolamiento', 'fecha_modificacion',
            'confianza_enrolamiento', 'intentos_verificacion',
            'ultima_verificacion'
        ]


class FaceStatusSerializer(serializers.Serializer):
    """Serializer para estado de enrolamiento facial"""
    
    copropietario_id = serializers.IntegerField()
    enrolled = serializers.BooleanField()
    provider = serializers.CharField(max_length=20, allow_null=True)
    enrollment_date = serializers.DateTimeField(allow_null=True)
    verification_attempts = serializers.IntegerField()
    last_verification = serializers.DateTimeField(allow_null=True)
    confidence = serializers.FloatField(allow_null=True)


class FaceEnrollResponseSerializer(serializers.Serializer):
    """Serializer para respuesta de enrolamiento"""
    
    ok = serializers.BooleanField()
    proveedor = serializers.CharField()
    face_ref = serializers.CharField()
    imagen_url = serializers.URLField(allow_null=True)
    timestamp = serializers.DateTimeField()
    copropietario_id = serializers.IntegerField()
    updated = serializers.BooleanField()
    confidence = serializers.FloatField(allow_null=True)


class FaceVerifyResponseSerializer(serializers.Serializer):
    """Serializer para respuesta de verificación"""
    
    match = serializers.BooleanField()
    confianza = serializers.FloatField()
    proveedor = serializers.CharField()
    umbral = serializers.FloatField(allow_null=True)
    copropietario_id = serializers.IntegerField()
    timestamp = serializers.DateTimeField()
    distance = serializers.FloatField(allow_null=True)


class ErrorResponseSerializer(serializers.Serializer):
    """Serializer para respuestas de error"""
    
    error = serializers.CharField()
    detail = serializers.CharField(allow_null=True)
    code = serializers.CharField(allow_null=True)
