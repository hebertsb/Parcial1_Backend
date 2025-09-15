"""
Serializers for Face Recognition API
"""

from rest_framework import serializers
from django.core.files.uploadedfile import InMemoryUploadedFile
from PIL import Image
import io

from .models import Copropietarios, ReconocimientoFacial


class FaceEnrollSerializer(serializers.Serializer):
    """Serializer para enrolamiento de rostros"""
    
    copropietario_id = serializers.IntegerField()
    imagen = serializers.ImageField()
    
    def validate_copropietario_id(self, value):
        """Valida que el copropietario exista"""
        try:
            copropietario = Copropietarios.objects.get(id=value, activo=True)
            return value
        except Copropietarios.DoesNotExist:
            raise serializers.ValidationError("Copropietario no encontrado o inactivo")
    
    def validate_imagen(self, value):
        """Valida la imagen"""
        if not isinstance(value, InMemoryUploadedFile):
            raise serializers.ValidationError("Debe proporcionar un archivo de imagen válido")
        
        # Validar tamaño (máximo 5MB)
        if value.size > 5 * 1024 * 1024:
            raise serializers.ValidationError("La imagen no debe superar 5MB")
        
        # Validar formato
        allowed_formats = ['JPEG', 'JPG', 'PNG', 'BMP', 'GIF']
        try:
            image = Image.open(value)
            if image.format not in allowed_formats:
                raise serializers.ValidationError(
                    f"Formato no soportado. Formatos permitidos: {', '.join(allowed_formats)}"
                )
        except Exception:
            raise serializers.ValidationError("Archivo de imagen inválido")
        
        # Resetear puntero del archivo
        value.seek(0)
        return value
    
    def validate(self, attrs):
        """Validaciones a nivel de objeto"""
        copropietario_id = attrs['copropietario_id']
        
        # Verificar si ya tiene enrolamiento activo
        if ReconocimientoFacial.objects.filter(
            copropietario_id=copropietario_id, 
            activo=True
        ).exists():
            # Permitir actualización, pero informar
            attrs['update_existing'] = True
        else:
            attrs['update_existing'] = False
        
        return attrs


class FaceVerifySerializer(serializers.Serializer):
    """Serializer para verificación de rostros"""
    
    copropietario_id = serializers.IntegerField()
    imagen = serializers.ImageField()
    
    def validate_copropietario_id(self, value):
        """Valida que el copropietario exista y tenga enrolamiento"""
        try:
            copropietario = Copropietarios.objects.get(id=value, activo=True)
        except Copropietarios.DoesNotExist:
            raise serializers.ValidationError("Copropietario no encontrado o inactivo")
        
        # Verificar que tenga enrolamiento activo
        if not ReconocimientoFacial.objects.filter(
            copropietario_id=value, 
            activo=True
        ).exists():
            raise serializers.ValidationError("Copropietario no tiene enrolamiento facial activo")
        
        return value
    
    def validate_imagen(self, value):
        """Valida la imagen"""
        if not isinstance(value, InMemoryUploadedFile):
            raise serializers.ValidationError("Debe proporcionar un archivo de imagen válido")
        
        # Validar tamaño (máximo 5MB)
        if value.size > 5 * 1024 * 1024:
            raise serializers.ValidationError("La imagen no debe superar 5MB")
        
        # Validar formato
        allowed_formats = ['JPEG', 'JPG', 'PNG', 'BMP', 'GIF']
        try:
            image = Image.open(value)
            if image.format not in allowed_formats:
                raise serializers.ValidationError(
                    f"Formato no soportado. Formatos permitidos: {', '.join(allowed_formats)}"
                )
        except Exception:
            raise serializers.ValidationError("Archivo de imagen inválido")
        
        # Resetear puntero del archivo
        value.seek(0)
        return value


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
