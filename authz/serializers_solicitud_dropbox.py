# -*- coding: utf-8 -*-
"""
Serializers específicos para el sistema de solicitudes con Dropbox
"""
from rest_framework import serializers
from .models import SolicitudRegistroPropietario
from .serializers_propietario import SolicitudRegistroPropietarioSerializer


class SolicitudRegistroPropietarioDropboxSerializer(SolicitudRegistroPropietarioSerializer):
    """
    Serializer extendido para solicitudes con integración Dropbox
    Hereda toda la funcionalidad del serializer base pero con lógica específica para Dropbox
    """
    
    def create(self, validated_data):
        # Extraer datos que no van al modelo principal
        validated_data.pop('password', None)
        validated_data.pop('password_confirm', None)
        validated_data.pop('confirm_password', None)
        validated_data.pop('foto_base64', None)
        validated_data.pop('familiares', [])
        validated_data.pop('acepta_terminos', None)
        validated_data.pop('acepta_tratamiento_datos', None)
        fotos_base64 = validated_data.pop('fotos_base64', None)

        # Subir fotos a Dropbox en carpeta temporal para solicitudes pendientes
        fotos_urls = []
        if fotos_base64:
            import logging
            logger = logging.getLogger(__name__)
            logger.info(f"🔄 INICIANDO SUBIDA DE {len(fotos_base64)} FOTOS A DROPBOX")
            
            # Verificar si Dropbox está disponible
            from django.conf import settings
            if not hasattr(settings, 'DROPBOX_ACCESS_TOKEN') or not settings.DROPBOX_ACCESS_TOKEN:
                logger.warning("⚠️ DROPBOX_ACCESS_TOKEN no configurado, simulando URLs")
                for idx in range(len(fotos_base64)):
                    fotos_urls.append(f"https://dropbox.com/sim/foto_{idx+1}.jpg")
                validated_data['fotos_reconocimiento_urls'] = fotos_urls
                logger.info(f"🎯 MODO SIMULACIÓN: {len(fotos_urls)} URLs generadas")
                # Crear solicitud sin subir a Dropbox
                solicitud = SolicitudRegistroPropietario.objects.create(**validated_data)
                return solicitud
            
            from core.utils.dropbox_upload import upload_image_to_dropbox
            import base64
            from django.core.files.base import ContentFile
            from uuid import uuid4
            
            for idx, foto_b64 in enumerate(fotos_base64):
                try:
                    # Manejar diferentes formatos de base64 del frontend
                    if ';base64,' in foto_b64:
                        # Formato completo: "data:image/jpeg;base64,/9j/4AAQ..."
                        header, b64data = foto_b64.split(';base64,')
                        ext = header.split('/')[-1].lower()
                        if ext == 'jpeg':
                            ext = 'jpg'
                    else:
                        # Formato simple: solo la cadena base64 sin prefijo
                        b64data = foto_b64
                        ext = 'jpg'  # Asumir JPG por defecto
                        logger.info(f"📷 Foto {idx+1}: Formato base64 simple detectado, asumiendo JPG")
                    
                    img_data = base64.b64decode(b64data)
                    documento_identidad = validated_data.get('documento_identidad', '')
                    file_name = f"solicitud_propietario_reconocimiento_{documento_identidad}_{uuid4().hex[:8]}_{idx}.{ext}"
                    file = ContentFile(img_data, name=file_name)
                    
                    # CARPETA TEMPORAL para solicitudes pendientes - según tu especificación
                    folder_path = f"/ParcialSI2/SolicitudesPendientes/{documento_identidad}"
                    logger.info(f"📤 Subiendo foto {idx+1}/{len(fotos_base64)} a Dropbox: {folder_path}/{file_name}")
                    
                    url_foto = upload_image_to_dropbox(file, file_name, folder=folder_path)
                    if url_foto:
                        fotos_urls.append(url_foto)
                        logger.info(f"✅ Foto {idx+1} subida exitosamente: {url_foto}")
                    else:
                        logger.error(f"❌ Error subiendo foto {idx+1}")
                except Exception as e:
                    # Log del error pero continuar con otras fotos
                    logger.error(f"❌ ERROR SUBIENDO FOTO {idx+1}: {str(e)}")
                    
                    # Si es error de permisos, generar URL simulada para desarrollo
                    error_str = str(e)
                    if 'missing_scope' in error_str or 'files.content.write' in error_str:
                        logger.warning(f"🔧 MODO DESARROLLO: Generando URL simulada para foto {idx+1}")
                        documento_identidad = validated_data.get('documento_identidad', '')
                        simulated_url = f"https://dropbox.com/sim/ParcialSI2/SolicitudesPendientes/{documento_identidad}/foto_{idx+1}.jpg"
                        fotos_urls.append(simulated_url)
                        logger.info(f"🔗 URL simulada generada: {simulated_url}")
                    else:
                        import traceback
                        logger.error(f"📋 Traceback: {traceback.format_exc()}")
                    
        validated_data['fotos_reconocimiento_urls'] = fotos_urls
        
        # Log del resultado de la subida
        import logging
        logger = logging.getLogger(__name__)
        logger.info(f"🎯 RESULTADO SUBIDA DROPBOX: {len(fotos_urls)} fotos subidas de {len(fotos_base64) if fotos_base64 else 0} enviadas")
        if fotos_urls:
            for i, url in enumerate(fotos_urls):
                logger.info(f"   📎 Foto {i+1}: {url}")

        # Crear solicitud
        solicitud = SolicitudRegistroPropietario.objects.create(**validated_data)

        # Validar vivienda automáticamente
        try:
            es_valida, mensaje = solicitud.validar_vivienda()
            if not es_valida:
                # Si no es válida, eliminar la solicitud y lanzar error
                solicitud.delete()
                raise serializers.ValidationError({
                    'numero_casa': mensaje
                })
        except Exception as e:
            # Si hay error en validación, eliminar solicitud
            solicitud.delete()
            raise serializers.ValidationError({
                'numero_casa': f'Error validando vivienda: {str(e)}'
            })

        return solicitud


class SolicitudRegistroResponseSerializer(serializers.ModelSerializer):
    """Serializer para respuesta de solicitud creada"""
    
    class Meta:
        model = SolicitudRegistroPropietario
        fields = [
            'id', 'nombres', 'apellidos', 'documento_identidad', 
            'numero_casa', 'email', 'estado', 'token_seguimiento',
            'created_at'
        ]
        read_only_fields = ['id', 'estado', 'token_seguimiento', 'created_at']


class FotosPropietarioPanelSerializer(serializers.Serializer):
    """Serializer para mostrar fotos en el panel del propietario"""
    id = serializers.IntegerField()
    url = serializers.URLField()
    es_perfil = serializers.BooleanField()
    orden = serializers.IntegerField()
    fecha_subida = serializers.DateTimeField()


class SubirFotoPropietarioSerializer(serializers.Serializer):
    """Serializer para subir fotos adicionales por el propietario"""
    foto_base64 = serializers.CharField(
        help_text="Imagen en formato base64 (data:image/jpeg;base64,...)"
    )
    es_perfil = serializers.BooleanField(
        default=False,
        help_text="Marcar como foto de perfil principal"
    )
    
    def validate_foto_base64(self, value):
        """Validar formato base64"""
        if not value.startswith('data:image/'):
            raise serializers.ValidationError("Formato de imagen inválido. Debe ser base64.")
        
        try:
            # Intentar decodificar para validar
            if ';base64,' in value:
                header, b64data = value.split(';base64,')
                import base64
                base64.b64decode(b64data)
            else:
                raise serializers.ValidationError("Formato base64 inválido.")
        except Exception:
            raise serializers.ValidationError("Error decodificando imagen base64.")
            
        return value


class UsuariosReconocimientoSeguridadSerializer(serializers.Serializer):
    """Serializer para listar usuarios con reconocimiento facial para seguridad"""
    id = serializers.IntegerField()
    nombre = serializers.CharField()
    documento = serializers.CharField()
    email = serializers.EmailField()
    numero_casa = serializers.CharField()
    bloque = serializers.CharField(required=False, allow_blank=True)
    tipo_vivienda = serializers.CharField(required=False)
    fotos_urls = serializers.ListField(child=serializers.URLField())
    total_fotos = serializers.IntegerField()
    fecha_registro = serializers.DateTimeField()
    estado_reconocimiento = serializers.CharField()