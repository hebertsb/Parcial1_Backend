# -*- coding: utf-8 -*-
"""
Views para el sistema de solicitudes de propietarios con integración Dropbox
Incluye endpoints para registro público, panel de propietarios, panel de seguridad y administración
"""

import logging
from typing import cast
from django.shortcuts import get_object_or_404
from django.db import transaction
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser
from drf_spectacular.utils import extend_schema, OpenApiResponse

# Modelos
from .models import SolicitudRegistroPropietario

# Serializers
from .serializers_solicitud_dropbox import (
    SolicitudRegistroPropietarioDropboxSerializer,
    SolicitudRegistroResponseSerializer,
    FotosPropietarioPanelSerializer,
    SubirFotoPropietarioSerializer,
    UsuariosReconocimientoSeguridadSerializer
)

# Permisos personalizados
from .permissions import IsPropietario, IsSeguridad, IsAdministrador

logger = logging.getLogger(__name__)

class CrearSolicitudRegistroDropboxView(APIView):
    """
    Vista pública para crear solicitudes de registro con fotos en Dropbox
    Endpoint principal del formulario de registro de propietarios
    """
    permission_classes = [AllowAny]
    parser_classes = [MultiPartParser, FormParser, JSONParser]
    
    @extend_schema(
        request=SolicitudRegistroPropietarioDropboxSerializer,
        responses={
            201: SolicitudRegistroResponseSerializer,
            400: OpenApiResponse(description="Datos inválidos")
        },
        summary="Crear solicitud de registro de propietario con fotos",
        description="""
        Endpoint principal para registro de propietarios.
        
        Flujo:
        1. Recibe datos del formulario y fotos en base64
        2. Valida que vivienda, email y documento sean únicos
        3. Sube fotos a Dropbox automáticamente
        4. Crea solicitud pendiente de aprobación
        5. Procesa reconocimiento facial (opcional)
        
        Formato de fotos_base64:
        [
            "data:image/jpeg;base64,/9j/4AAQ...",
            "data:image/png;base64,iVBORw0K...",
            "data:image/jpg;base64,/9j/4AAQ..."
        ]
        
        Mínimo 3 fotos, máximo 10.
        """
    )
    def post(self, request):
        """Crear nueva solicitud de registro"""
        logger.info(f"🚀 DROPBOX VIEW: Nueva solicitud de registro desde IP: {request.META.get('REMOTE_ADDR')}")
        logger.info(f"📊 Datos recibidos: {list(request.data.keys())}")
        logger.info(f"🔍 Payload completo: {request.data}")
        
        if 'fotos_base64' in request.data:
            fotos_data = request.data['fotos_base64']
            if isinstance(fotos_data, list):
                fotos_count = len(fotos_data)
                logger.info(f"📷 Fotos recibidas (array): {fotos_count}")
                for i, foto in enumerate(fotos_data):
                    if isinstance(foto, str):
                        if foto.startswith('data:'):
                            logger.info(f"   📸 Foto {i+1}: Formato completo (con prefijo data:)")
                        else:
                            logger.info(f"   📸 Foto {i+1}: Formato base64 puro, tamaño: {len(foto)} chars")
                    else:
                        logger.info(f"   📸 Foto {i+1}: Tipo inesperado: {type(foto)}")
            else:
                logger.info(f"📷 Fotos recibidas (individual): {type(fotos_data)}")
        else:
            logger.warning("⚠️ No se encontró 'fotos_base64' en los datos")
        
        try:
            # Validar y crear solicitud
            serializer = SolicitudRegistroPropietarioDropboxSerializer(data=request.data)
            
            if serializer.is_valid():
                with transaction.atomic():
                    solicitud = cast(SolicitudRegistroPropietario, serializer.save())
                    
                    # Respuesta con datos de la solicitud creada
                    response_serializer = SolicitudRegistroResponseSerializer(solicitud)
                    
                    logger.info(f"Solicitud creada exitosamente: ID={solicitud.pk}, Token={solicitud.token_seguimiento}")
                    
                    return Response({
                        'success': True,
                        'message': 'Solicitud creada exitosamente. Recibirá un email de confirmación.',
                        'data': response_serializer.data
                    }, status=status.HTTP_201_CREATED)
            else:
                logger.warning(f"Datos inválidos en solicitud: {serializer.errors}")
                return Response({
                    'success': False,
                    'message': 'Datos inválidos. Revise los errores.',
                    'errors': serializer.errors
                }, status=status.HTTP_400_BAD_REQUEST)
                
        except Exception as e:
            logger.error(f"Error creando solicitud: {str(e)}")
            return Response({
                'success': False,
                'message': f'Error interno del servidor: {str(e)}',
                'errors': {}
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class MisFotosPropietarioDropboxView(APIView):
    """Vista para que el propietario vea y gestione sus fotos de reconocimiento"""
    permission_classes = [IsAuthenticated, IsPropietario]
    
    @extend_schema(
        responses={
            200: OpenApiResponse(description="Fotos del propietario obtenidas exitosamente"),
            404: OpenApiResponse(description="No se encontraron fotos")
        },
        summary="Obtener fotos del propietario",
        description="Obtiene todas las fotos de reconocimiento facial del propietario autenticado"
    )
    def get(self, request):
        """Obtener fotos del propietario autenticado"""
        try:
            # Buscar solicitud aprobada del usuario
            solicitud = SolicitudRegistroPropietario.objects.filter(
                usuario_creado=request.user,
                estado='APROBADA'
            ).first()
            
            if not solicitud:
                return Response({
                    'success': False,
                    'message': 'No se encontró una solicitud aprobada para este usuario',
                    'data': []
                }, status=status.HTTP_404_NOT_FOUND)
            
            # Preparar datos de fotos
            fotos_data = []
            for foto in solicitud.fotos_reconocimiento_urls:
                if foto.get('url'):
                    fotos_data.append({
                        'id': foto.get('orden', 1),
                        'url': foto['url'],
                        'es_perfil': foto.get('es_perfil', False),
                        'orden': foto.get('orden', 1),
                        'fecha_subida': solicitud.created_at
                    })
            
            # Serializar fotos
            fotos_serializer = FotosPropietarioPanelSerializer(fotos_data, many=True)
            
            return Response({
                'success': True,
                'message': f'Se encontraron {len(fotos_data)} fotos',
                'data': {
                    'usuario_id': request.user.id,
                    'documento': solicitud.documento_identidad,
                    'numero_casa': solicitud.numero_casa,
                    'total_fotos': len(fotos_data),
                    'fotos': fotos_serializer.data
                }
            }, status=status.HTTP_200_OK)
            
        except Exception as e:
            logger.error(f"Error obteniendo fotos del propietario {request.user.id}: {str(e)}")
            return Response({
                'success': False,
                'message': f'Error obteniendo fotos: {str(e)}',
                'data': []
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class SubirFotoPropietarioDropboxView(APIView):
    """Vista para que el propietario suba nuevas fotos"""
    permission_classes = [IsAuthenticated, IsPropietario]
    parser_classes = [JSONParser]
    
    @extend_schema(
        request=SubirFotoPropietarioSerializer,
        responses={
            201: OpenApiResponse(description="Foto subida exitosamente"),
            400: OpenApiResponse(description="Datos inválidos")
        },
        summary="Subir nueva foto de reconocimiento",
        description="Permite al propietario subir una nueva foto para reconocimiento facial"
    )
    def post(self, request):
        """Subir nueva foto de reconocimiento"""
        try:
            # Validar datos
            serializer = SubirFotoPropietarioSerializer(data=request.data)
            
            if not serializer.is_valid():
                return Response({
                    'success': False,
                    'message': 'Datos inválidos',
                    'errors': serializer.errors
                }, status=status.HTTP_400_BAD_REQUEST)
            
            # Buscar solicitud del usuario
            solicitud = SolicitudRegistroPropietario.objects.filter(
                usuario_creado=request.user,
                estado='APROBADA'
            ).first()
            
            if not solicitud:
                return Response({
                    'success': False,
                    'message': 'No se encontró solicitud aprobada para este usuario',
                    'data': None
                }, status=status.HTTP_404_NOT_FOUND)
            
            # Procesar nueva foto
            validated_data = serializer.validated_data
            if not validated_data:
                return Response({
                    'success': False,
                    'message': 'Error en los datos validados',
                    'data': None
                }, status=status.HTTP_400_BAD_REQUEST)
            
            foto_base64 = request.data.get('foto_base64')
            es_perfil = request.data.get('es_perfil', False)
            
            # Subir foto a Dropbox
            nueva_foto = self._subir_foto_dropbox(foto_base64, solicitud, es_perfil)
            
            if nueva_foto:
                # Agregar a la lista de fotos existentes
                fotos_actuales = solicitud.fotos_reconocimiento_urls or []
                
                # Si es foto de perfil, desmarcar las anteriores
                if es_perfil:
                    for foto in fotos_actuales:
                        foto['es_perfil'] = False
                
                fotos_actuales.append(nueva_foto)
                solicitud.fotos_reconocimiento_urls = fotos_actuales
                solicitud.save()
                
                return Response({
                    'success': True,
                    'message': 'Foto subida exitosamente',
                    'data': {
                        'foto_id': nueva_foto['orden'],
                        'url': nueva_foto['url'],
                        'es_perfil': nueva_foto['es_perfil']
                    }
                }, status=status.HTTP_201_CREATED)
            else:
                return Response({
                    'success': False,
                    'message': 'Error subiendo foto a Dropbox',
                    'data': None
                }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
                
        except Exception as e:
            logger.error(f"Error subiendo foto para usuario {request.user.id}: {str(e)}")
            return Response({
                'success': False,
                'message': f'Error subiendo foto: {str(e)}',
                'data': None
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    def _subir_foto_dropbox(self, foto_base64, solicitud, es_perfil=False):
        """Sube una foto individual a Dropbox"""
        try:
            from core.utils.dropbox_upload import upload_image_to_dropbox
            from django.core.files.base import ContentFile
            from uuid import uuid4
            import base64
            
            # Decodificar base64
            if ';base64,' in foto_base64:
                header, b64data = foto_base64.split(';base64,')
                ext = header.split('/')[-1].lower()
                if ext == 'jpeg':
                    ext = 'jpg'
            else:
                b64data = foto_base64
                ext = 'jpg'
            
            img_data = base64.b64decode(b64data)
            
            # Crear archivo
            documento = solicitud.documento_identidad
            file_name = f"adicional_{documento}_{uuid4().hex[:8]}.{ext}"
            file_obj = ContentFile(img_data, name=file_name)
            
            # Subir a carpeta definitiva del propietario - usando ParcialSI2 según especificación
            folder_definitivo = f"/ParcialSI2/Propietarios/{documento}"
            resultado = upload_image_to_dropbox(file_obj, file_name, folder=folder_definitivo)
            
            if resultado and resultado.get('url'):
                # Calcular nuevo orden
                orden_actual = len(solicitud.fotos_reconocimiento_urls or []) + 1
                
                return {
                    'path': resultado['path'],
                    'url': resultado['url'],
                    'orden': orden_actual,
                    'es_perfil': es_perfil,
                    'nombre_archivo': file_name
                }
            
            return None
            
        except Exception as e:
            logger.error(f"Error subiendo foto a Dropbox: {str(e)}")
            return None

class UsuariosReconocimientoSeguridadView(APIView):
    """Vista para que seguridad obtenga usuarios con reconocimiento facial"""
    permission_classes = [IsAuthenticated, IsSeguridad]
    
    @extend_schema(
        responses={
            200: OpenApiResponse(description="Lista de usuarios con reconocimiento facial"),
        },
        summary="Obtener usuarios con reconocimiento facial para seguridad",
        description="""
        Obtiene todos los usuarios con fotos de reconocimiento facial 
        para el panel de seguridad. Incluye URLs públicas de Dropbox.
        """
    )
    def get(self, request):
        """Obtener todos los usuarios con reconocimiento facial"""
        try:
            usuarios_reconocimiento = []
            
            # Obtener solicitudes aprobadas con fotos
            solicitudes = SolicitudRegistroPropietario.objects.filter(
                estado='APROBADA',
                usuario_creado__isnull=False
            ).select_related('usuario_creado')
            
            for solicitud in solicitudes:
                # Filtrar solo fotos con URL válida
                fotos_urls = [
                    foto['url'] for foto in solicitud.fotos_reconocimiento_urls 
                    if foto.get('url')
                ]
                
                if fotos_urls and solicitud.usuario_creado:  # Solo incluir usuarios con fotos
                    usuario_data = {
                        'id': solicitud.usuario_creado.id,
                        'nombre': f"{solicitud.nombres} {solicitud.apellidos}",
                        'documento': solicitud.documento_identidad,
                        'email': solicitud.email,
                        'numero_casa': solicitud.numero_casa,
                        'fotos_urls': fotos_urls,
                        'total_fotos': len(fotos_urls),
                        'fecha_registro': solicitud.fecha_aprobacion,
                        'estado_reconocimiento': 'activo',
                        'bloque': '',  # Campo por defecto
                        'tipo_vivienda': 'Casa'  # Campo por defecto
                    }
                    
                    usuarios_reconocimiento.append(usuario_data)
            
            # Serializar datos
            serializer = UsuariosReconocimientoSeguridadSerializer(usuarios_reconocimiento, many=True)
            
            return Response({
                'success': True,
                'message': f'Se encontraron {len(usuarios_reconocimiento)} usuarios con reconocimiento facial',
                'data': {
                    'total_usuarios': len(usuarios_reconocimiento),
                    'usuarios': serializer.data
                }
            }, status=status.HTTP_200_OK)
            
        except Exception as e:
            logger.error(f"Error obteniendo usuarios para seguridad: {str(e)}")
            return Response({
                'success': False,
                'message': f'Error obteniendo usuarios: {str(e)}',
                'data': {'total_usuarios': 0, 'usuarios': []}
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class AprobarSolicitudDropboxView(APIView):
    """Vista para aprobar solicitudes (admin)"""
    permission_classes = [IsAuthenticated, IsAdministrador]
    
    @extend_schema(
        responses={
            200: OpenApiResponse(description="Solicitud aprobada exitosamente"),
            404: OpenApiResponse(description="Solicitud no encontrada")
        },
        summary="Aprobar solicitud de registro",
        description="Aprueba una solicitud y mueve las fotos a carpeta definitiva en Dropbox"
    )
    def post(self, request, solicitud_id):
        """Aprobar solicitud de registro"""
        try:
            solicitud = get_object_or_404(SolicitudRegistroPropietario, id=solicitud_id)
            
            if solicitud.estado != 'PENDIENTE':
                return Response({
                    'success': False,
                    'message': f'La solicitud ya está en estado: {solicitud.estado}',
                    'data': None
                }, status=status.HTTP_400_BAD_REQUEST)
            
            # Usar el método del modelo para aprobar
            resultado = solicitud.aprobar_solicitud(request.user)
            
            # Refrescar solicitud para obtener datos actualizados
            solicitud.refresh_from_db()
            
            if hasattr(resultado, 'email'):  # Si devuelve el usuario creado
                return Response({
                    'success': True,
                    'message': 'Solicitud aprobada exitosamente',
                    'data': {
                        'solicitud_id': solicitud.pk,
                        'usuario_email': resultado.email,
                        'fecha_aprobacion': solicitud.fecha_aprobacion.isoformat() if solicitud.fecha_aprobacion else None
                    }
                }, status=status.HTTP_200_OK)
            else:
                return Response({
                    'success': False,
                    'message': 'Error aprobando solicitud',
                    'data': None
                }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
                
        except Exception as e:
            logger.error(f"Error aprobando solicitud {solicitud_id}: {str(e)}")
            return Response({
                'success': False,
                'message': f'Error aprobando solicitud: {str(e)}',
                'data': None
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class ConsultarEstadoSolicitudView(APIView):
    """Vista pública para consultar estado de solicitud por token"""
    permission_classes = [AllowAny]
    
    @extend_schema(
        responses={
            200: OpenApiResponse(description="Estado de solicitud obtenido"),
            404: OpenApiResponse(description="Solicitud no encontrada")
        },
        summary="Consultar estado de solicitud por token",
        description="Permite consultar el estado de una solicitud usando el token de seguimiento"
    )
    def get(self, request, token):
        """Consultar estado de solicitud por token"""
        try:
            solicitud = get_object_or_404(SolicitudRegistroPropietario, token_seguimiento=token)
            
            response_data = {
                'token_seguimiento': solicitud.token_seguimiento,
                'estado': solicitud.estado,
                'nombres': solicitud.nombres,
                'apellidos': solicitud.apellidos,
                'numero_casa': solicitud.numero_casa,
                'fecha_solicitud': solicitud.created_at.isoformat(),
                'fecha_actualizacion': solicitud.updated_at.isoformat()
            }
            
            # Agregar información adicional según el estado
            if solicitud.estado == 'APROBADA':
                if solicitud.fecha_aprobacion:
                    response_data['fecha_aprobacion'] = solicitud.fecha_aprobacion.isoformat()
                response_data['mensaje'] = 'Su solicitud ha sido aprobada. Puede acceder al sistema.'
            elif solicitud.estado == 'RECHAZADA':
                response_data['motivo_rechazo'] = getattr(solicitud, 'motivo_rechazo', '')
                if hasattr(solicitud, 'fecha_rechazo') and solicitud.fecha_rechazo:
                    response_data['fecha_rechazo'] = solicitud.fecha_rechazo.isoformat()
                response_data['mensaje'] = 'Su solicitud ha sido rechazada. Puede contactar con administración.'
            else:
                response_data['mensaje'] = 'Su solicitud está siendo revisada. Le notificaremos por email.'
            
            return Response({
                'success': True,
                'message': 'Estado de solicitud obtenido exitosamente',
                'data': response_data
            }, status=status.HTTP_200_OK)
            
        except Exception as e:
            logger.error(f"Error consultando solicitud {token}: {str(e)}")
            return Response({
                'success': False,
                'message': f'Error consultando solicitud: {str(e)}',
                'data': None
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)