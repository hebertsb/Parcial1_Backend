"""
Face Recognition API Views
"""

import json
import logging
from typing import Dict, Any, cast
from django.utils import timezone
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.throttling import UserRateThrottle
from rest_framework.parsers import FormParser, MultiPartParser
from rest_framework.permissions import IsAuthenticated
from drf_spectacular.utils import extend_schema, OpenApiExample

from .models import Copropietarios, ReconocimientoFacial, fn_bitacora_log
from .serializers import (
    FaceEnrollSerializer, FaceVerifySerializer, FaceStatusSerializer,
    FaceEnrollResponseSerializer, FaceVerifyResponseSerializer,
    ErrorResponseSerializer, ReconocimientoFacialSerializer
)
from .services.face_provider import (
    FaceProviderFactory, FaceDetectionError, FaceVerificationError, 
    FaceEnrollmentError
)

logger = logging.getLogger('seguridad')


class FaceEnrollThrottle(UserRateThrottle):
    """Rate limiting específico para enrolamiento facial"""
    scope = 'face_enroll'


class FaceVerifyThrottle(UserRateThrottle):
    """Rate limiting específico para verificación facial"""
    scope = 'face_verify'


def get_client_ip(request):
    """Obtiene la IP del cliente"""
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip


class FaceEnrollView(APIView):
    """
    Endpoint para enrolamiento de rostros
    
    POST /api/faces/enroll/
    """
    
    permission_classes = [IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser]
    throttle_classes = [FaceEnrollThrottle]
    
    @extend_schema(
        operation_id='face_enroll',
        summary='Enrolamiento de rostro facial',
        description='Enrola un rostro facial para un copropietario específico',
        request=FaceEnrollSerializer,
        responses={
            201: FaceEnrollResponseSerializer,
            200: FaceEnrollResponseSerializer,  # Para actualizaciones
            400: ErrorResponseSerializer,
            404: ErrorResponseSerializer,
            422: ErrorResponseSerializer,
            500: ErrorResponseSerializer,
        },
        examples=[
            OpenApiExample(
                'Ejemplo de enrolamiento',
                description='Ejemplo de request para enrolamiento',
                value={
                    'copropietario_id': 1,
                    'imagen': 'archivo_imagen.jpg'
                }
            )
        ]
    )
    def post(self, request):
        """Enrolar rostro facial"""
        try:
            # Validar datos
            serializer = FaceEnrollSerializer(data=request.data)
            if not serializer.is_valid():
                return Response(
                    {'error': 'Datos inválidos', 'detail': serializer.errors},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            validated_data = cast(Dict[str, Any], serializer.validated_data)
            if not validated_data:
                return Response(
                    {'error': 'No se pudieron validar los datos'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            copropietario_id = validated_data['copropietario_id']
            imagen = validated_data['imagen']
            update_existing = validated_data.get('update_existing', False)
            # Buscar copropietario (puede ser inquilino registrado como copropietario)
            try:
                copropietario = Copropietarios.objects.get(id=copropietario_id, activo=True)
            except Copropietarios.DoesNotExist:
                return Response(
                    {'error': 'Copropietario/Inquilino no encontrado'},
                    status=status.HTTP_404_NOT_FOUND
                )
            
            # Leer bytes de la imagen
            imagen_bytes = imagen.read()
            
            # Crear proveedor de reconocimiento facial
            face_provider = FaceProviderFactory.create_provider()
            
            # Enrolar rostro
            try:
                enroll_result = face_provider.enroll_face(imagen_bytes)
            except FaceDetectionError as e:
                logger.warning(f"No se detectó rostro en enrolamiento: {str(e)}")
                
                # Registrar en bitácora
                fn_bitacora_log(
                    tipo_accion='ENROLL_FACE',
                    descripcion=f'Error: No se detectó rostro para copropietario {copropietario.nombre_completo}',
                    usuario=request.user,  # Usar directamente el usuario del nuevo sistema
                    copropietario=copropietario,
                    direccion_ip=get_client_ip(request),
                    user_agent=request.META.get('HTTP_USER_AGENT'),
                    proveedor_ia=face_provider.provider_name,
                    resultado_match=False
                )
                
                return Response(
                    {'error': 'No se detectó rostro en la imagen', 'detail': str(e)},
                    status=status.HTTP_422_UNPROCESSABLE_ENTITY
                )
            except FaceEnrollmentError as e:
                logger.error(f"Error en enrolamiento: {str(e)}")
                
                # Registrar en bitácora
                fn_bitacora_log(
                    tipo_accion='ENROLL_FACE',
                    descripcion=f'Error de enrolamiento para copropietario {copropietario.nombre_completo}: {str(e)}',
                    usuario=request.user,
                    copropietario=copropietario,
                    direccion_ip=get_client_ip(request),
                    user_agent=request.META.get('HTTP_USER_AGENT'),
                    proveedor_ia=face_provider.provider_name
                )
                
                return Response(
                    {'error': 'Error en el enrolamiento', 'detail': str(e)},
                    status=status.HTTP_422_UNPROCESSABLE_ENTITY
                )
            
            # ===== INTEGRACIÓN CON DROPBOX =====
            # Subir imagen a Dropbox para mantener consistencia con otros sistemas
            from core.utils.dropbox_upload import upload_image_to_dropbox
            
            # Generar nombre único para el archivo
            now = timezone.now()
            timestamp = now.strftime('%Y%m%d_%H%M%S')
            extension = imagen.name.split('.')[-1] if '.' in imagen.name else 'jpg'
            nombre_archivo = f"seguridad_{copropietario.id}_{timestamp}.{extension}"
            
            # Subir a Dropbox en carpeta específica de seguridad
            folder_path = f"/SeguridadReconocimiento/{copropietario.id}"
            
            try:
                # Resetear el puntero del archivo para poder leerlo de nuevo
                imagen.seek(0)
                resultado_upload = upload_image_to_dropbox(imagen, nombre_archivo, folder_path)
                dropbox_url = resultado_upload.get('url') if resultado_upload else None
                
                logger.info(f"Imagen subida a Dropbox: {dropbox_url}")
            except Exception as e:
                logger.warning(f"Error subiendo a Dropbox: {str(e)}")
                dropbox_url = None
            
            # Guardar o actualizar en base de datos
            now = timezone.now()
            
            if update_existing:
                # Actualizar existente
                reconocimiento = ReconocimientoFacial.objects.get(
                    copropietario=copropietario,
                    activo=True
                )
                reconocimiento.proveedor_ia = enroll_result['provider']
                reconocimiento.vector_facial = enroll_result['face_reference']
                reconocimiento.imagen_referencia_url = dropbox_url or enroll_result.get('image_url')
                reconocimiento.confianza_enrolamiento = enroll_result.get('confidence')
                reconocimiento.fecha_modificacion = now
                
                # CAPTURAR URLs EXISTENTES DE DROPBOX del propietario
                fotos_existentes = []
                if reconocimiento.fotos_urls:
                    try:
                        fotos_existentes = json.loads(reconocimiento.fotos_urls)
                        if not isinstance(fotos_existentes, list):
                            fotos_existentes = []
                    except (json.JSONDecodeError, TypeError):
                        fotos_existentes = []
                
                # Agregar nueva URL si se subió correctamente
                if dropbox_url and dropbox_url not in fotos_existentes:
                    fotos_existentes.append(dropbox_url)
                    reconocimiento.fotos_urls = json.dumps(fotos_existentes)
                
                reconocimiento.save()
                response_status = status.HTTP_200_OK
                
            else:
                # Crear nuevo registro
                fotos_urls_inicial = []
                if dropbox_url:
                    fotos_urls_inicial.append(dropbox_url)
                
                reconocimiento = ReconocimientoFacial.objects.create(
                    copropietario=copropietario,
                    proveedor_ia=enroll_result['provider'],
                    vector_facial=enroll_result['face_reference'],
                    imagen_referencia_url=dropbox_url or enroll_result.get('image_url'),
                    fotos_urls=json.dumps(fotos_urls_inicial),  # Inicializar con la nueva foto
                    confianza_enrolamiento=enroll_result.get('confidence'),
                    activo=True
                )
                
                response_status = status.HTTP_201_CREATED
            
            # Registrar en bitácora
            fn_bitacora_log(
                tipo_accion='ENROLL_FACE',
                descripcion=f'Enrolamiento biométrico exitoso para copropietario {copropietario.nombre_completo}',
                usuario=request.user,
                copropietario=copropietario,
                direccion_ip=get_client_ip(request),
                user_agent=request.META.get('HTTP_USER_AGENT'),
                proveedor_ia=enroll_result['provider'],
                confianza=enroll_result.get('confidence'),
                resultado_match=True
            )
            
            # Preparar respuesta
            response_data = {
                'ok': True,
                'proveedor': enroll_result['provider'],
                'face_ref': enroll_result['face_reference'][:50] + '...',  # Truncar para respuesta
                'imagen_url': enroll_result.get('image_url'),
                'timestamp': now,
                'copropietario_id': copropietario_id,
                'updated': update_existing,
                'confidence': enroll_result.get('confidence')
            }
            
            logger.info(f"Enrolamiento exitoso para copropietario {copropietario_id}")
            
            return Response(response_data, status=response_status)
            
        except Exception as e:
            logger.error(f"Error inesperado en enrolamiento: {str(e)}")
            
            # Registrar error en bitácora
            fn_bitacora_log(
                tipo_accion='SYSTEM_ERROR',
                descripcion=f'Error del sistema en enrolamiento: {str(e)}',
                usuario=request.user,
                direccion_ip=get_client_ip(request),
                user_agent=request.META.get('HTTP_USER_AGENT')
            )
            
            return Response(
                {'error': 'Error interno del servidor', 'detail': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class FaceVerifyView(APIView):
    """
    Endpoint para verificación de rostros
    
    POST /api/faces/verify/
    """
    
    permission_classes = [IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser]
    throttle_classes = [FaceVerifyThrottle]
    
    @extend_schema(
        operation_id='face_verify',
        summary='Verificación de rostro facial',
        description='Verifica un rostro facial contra el enrolamiento de un copropietario',
        request=FaceVerifySerializer,
        responses={
            200: FaceVerifyResponseSerializer,
            400: ErrorResponseSerializer,
            404: ErrorResponseSerializer,
            422: ErrorResponseSerializer,
            500: ErrorResponseSerializer,
        }
    )
    def post(self, request):
        """Verificar rostro facial"""
        try:
            # Validar datos
            serializer = FaceVerifySerializer(data=request.data)
            if not serializer.is_valid():
                return Response(
                    {'error': 'Datos inválidos', 'detail': serializer.errors},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            validated_data = cast(Dict[str, Any], serializer.validated_data)
            if not validated_data:
                return Response(
                    {'error': 'No se pudieron validar los datos'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            copropietario_id = validated_data['copropietario_id']
            imagen = validated_data['imagen']
            # Buscar copropietario (puede ser inquilino registrado como copropietario)
            try:
                copropietario = Copropietarios.objects.get(id=copropietario_id, activo=True)
                reconocimiento = ReconocimientoFacial.objects.get(
                    copropietario=copropietario,
                    activo=True
                )
            except Copropietarios.DoesNotExist:
                return Response(
                    {'error': 'Copropietario/Inquilino no encontrado'},
                    status=status.HTTP_404_NOT_FOUND
                )
            except ReconocimientoFacial.DoesNotExist:
                return Response(
                    {'error': 'No tiene enrolamiento facial activo'},
                    status=status.HTTP_404_NOT_FOUND
                )
            
            # Leer bytes de la imagen
            imagen_bytes = imagen.read()
            
            # Crear proveedor de reconocimiento facial
            face_provider = FaceProviderFactory.create_provider()
            
            # Verificar rostro
            try:
                verify_result = face_provider.verify_faces(
                    reconocimiento.vector_facial,
                    imagen_bytes
                )
            except FaceDetectionError as e:
                logger.warning(f"No se detectó rostro en verificación: {str(e)}")
                
                # Registrar en bitácora
                fn_bitacora_log(
                    tipo_accion='VERIFY_FACE',
                    descripcion=f'Error: No se detectó rostro en verificación para copropietario {copropietario.nombre_completo}',
                    usuario=request.user,
                    copropietario=copropietario,
                    direccion_ip=get_client_ip(request),
                    user_agent=request.META.get('HTTP_USER_AGENT'),
                    proveedor_ia=face_provider.provider_name,
                    resultado_match=False
                )
                
                return Response(
                    {'error': 'No se detectó rostro en la imagen', 'detail': str(e)},
                    status=status.HTTP_422_UNPROCESSABLE_ENTITY
                )
            except FaceVerificationError as e:
                logger.error(f"Error en verificación: {str(e)}")
                
                # Registrar en bitácora
                fn_bitacora_log(
                    tipo_accion='VERIFY_FACE',
                    descripcion=f'Error de verificación para copropietario {copropietario.nombre_completo}: {str(e)}',
                    usuario=request.user,
                    copropietario=copropietario,
                    direccion_ip=get_client_ip(request),
                    user_agent=request.META.get('HTTP_USER_AGENT'),
                    proveedor_ia=face_provider.provider_name
                )
                
                return Response(
                    {'error': 'Error en la verificación', 'detail': str(e)},
                    status=status.HTTP_422_UNPROCESSABLE_ENTITY
                )
            
            # Actualizar estadísticas
            now = timezone.now()
            reconocimiento.intentos_verificacion += 1
            reconocimiento.ultima_verificacion = now
            reconocimiento.save()
            
            # Registrar en bitácora
            resultado_texto = "match" if verify_result.get('isIdentical', False) else "no-match"
            confianza = verify_result.get('confidence', 0.0)
            
            fn_bitacora_log(
                tipo_accion='VERIFY_FACE',
                descripcion=f'Verificación biométrica para copropietario {copropietario.nombre_completo} ({resultado_texto}, conf={confianza:.3f})',
                usuario=request.user,
                copropietario=copropietario,
                direccion_ip=get_client_ip(request),
                user_agent=request.META.get('HTTP_USER_AGENT'),
                proveedor_ia=verify_result.get('provider'),
                confianza=confianza,
                resultado_match=verify_result.get('isIdentical', False)
            )
            
            # Preparar respuesta
            response_data = {
                'match': verify_result.get('isIdentical', False),
                'confianza': verify_result.get('confidence', 0.0),
                'proveedor': verify_result.get('provider'),
                'umbral': verify_result.get('threshold'),
                'copropietario_id': copropietario_id,
                'timestamp': now,
                'distance': verify_result.get('distance')
            }
            
            logger.info(f"Verificación completada para copropietario {copropietario_id}: {resultado_texto}")
            
            return Response(response_data, status=status.HTTP_200_OK)
            
        except Exception as e:
            logger.error(f"Error inesperado en verificación: {str(e)}")
            
            # Registrar error en bitácora
            fn_bitacora_log(
                tipo_accion='SYSTEM_ERROR',
                descripcion=f'Error del sistema en verificación: {str(e)}',
                usuario=request.user,
                direccion_ip=get_client_ip(request),
                user_agent=request.META.get('HTTP_USER_AGENT')
            )
            
            return Response(
                {'error': 'Error interno del servidor', 'detail': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class FaceDeleteView(APIView):
    """
    Endpoint para eliminar enrolamiento facial
    
    DELETE /api/faces/enroll/<copropietario_id>/
    """
    
    permission_classes = [IsAuthenticated]
    
    @extend_schema(
        operation_id='face_delete',
        summary='Eliminar enrolamiento facial',
        description='Elimina (desactiva) el enrolamiento facial de un copropietario',
        responses={
            200: {'description': 'Enrolamiento eliminado exitosamente'},
            404: ErrorResponseSerializer,
            500: ErrorResponseSerializer,
        }
    )
    def delete(self, request, copropietario_id):
        """Eliminar enrolamiento facial"""
        try:
            # Obtener copropietario y reconocimiento facial
            try:
                copropietario = Copropietarios.objects.get(id=copropietario_id, activo=True)
                reconocimiento = ReconocimientoFacial.objects.get(
                    copropietario=copropietario,
                    activo=True
                )
            except Copropietarios.DoesNotExist:
                return Response(
                    {'error': 'Copropietario/Inquilino no encontrado'},
                    status=status.HTTP_404_NOT_FOUND
                )
            except ReconocimientoFacial.DoesNotExist:
                return Response(
                    {'error': 'No tiene enrolamiento facial activo'},
                    status=status.HTTP_404_NOT_FOUND
                )
            
            # Desactivar enrolamiento
            reconocimiento.activo = False
            reconocimiento.fecha_modificacion = timezone.now()
            reconocimiento.save()
            
            # Registrar en bitácora
            fn_bitacora_log(
                tipo_accion='DELETE_FACE',
                descripcion=f'Baja de enrolamiento biométrico para copropietario {copropietario.nombre_completo}',
                usuario=request.user,
                copropietario=copropietario,
                direccion_ip=get_client_ip(request),
                user_agent=request.META.get('HTTP_USER_AGENT'),
                proveedor_ia=reconocimiento.proveedor_ia
            )
            
            logger.info(f"Enrolamiento eliminado para copropietario {copropietario_id}")
            
            return Response(
                {'message': 'Enrolamiento facial eliminado exitosamente'},
                status=status.HTTP_200_OK
            )
            
        except Exception as e:
            logger.error(f"Error inesperado eliminando enrolamiento: {str(e)}")
            
            # Registrar error en bitácora
            fn_bitacora_log(
                tipo_accion='SYSTEM_ERROR',
                descripcion=f'Error del sistema eliminando enrolamiento: {str(e)}',
                usuario=request.user,
                direccion_ip=get_client_ip(request),
                user_agent=request.META.get('HTTP_USER_AGENT')
            )
            
            return Response(
                {'error': 'Error interno del servidor', 'detail': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class FaceStatusView(APIView):
    """
    Endpoint para consultar estado de enrolamiento facial
    
    GET /api/faces/status/<copropietario_id>/
    """
    
    permission_classes = [IsAuthenticated]
    
    @extend_schema(
        operation_id='face_status',
        summary='Consultar estado de enrolamiento facial',
        description='Consulta el estado del enrolamiento facial de un copropietario',
        responses={
            200: FaceStatusSerializer,
            404: ErrorResponseSerializer,
            500: ErrorResponseSerializer,
        }
    )
    def get(self, request, copropietario_id):
        """Consultar estado de enrolamiento"""
        try:
            # Verificar que el copropietario exista
            try:
                copropietario = Copropietarios.objects.get(id=copropietario_id, activo=True)
            except Copropietarios.DoesNotExist:
                return Response(
                    {'error': 'Copropietario/Inquilino no encontrado'},
                    status=status.HTTP_404_NOT_FOUND
                )
            
            # Buscar enrolamiento activo
            try:
                reconocimiento = ReconocimientoFacial.objects.get(
                    copropietario=copropietario,
                    activo=True
                )
                
                response_data = {
                    'copropietario_id': copropietario_id,
                    'enrolled': True,
                    'provider': reconocimiento.proveedor_ia,
                    'enrollment_date': reconocimiento.fecha_enrolamiento,
                    'verification_attempts': reconocimiento.intentos_verificacion,
                    'last_verification': reconocimiento.ultima_verificacion,
                    'confidence': reconocimiento.confianza_enrolamiento
                }
                
            except ReconocimientoFacial.DoesNotExist:
                response_data = {
                    'copropietario_id': copropietario_id,
                    'enrolled': False,
                    'provider': None,
                    'enrollment_date': None,
                    'verification_attempts': 0,
                    'last_verification': None,
                    'confidence': None
                }
            
            return Response(response_data, status=status.HTTP_200_OK)
            
        except Exception as e:
            logger.error(f"Error inesperado consultando estado: {str(e)}")
            
            return Response(
                {'error': 'Error interno del servidor', 'detail': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class ListarUsuariosReconocimientoFacialView(APIView):
    """
    Vista para listar todos los usuarios que tienen reconocimiento facial habilitado.
    Para uso del panel de seguridad y administración.
    """
    permission_classes = [IsAuthenticated]
    
    @extend_schema(
        summary="Listar usuarios con reconocimiento facial",
        description="Obtiene lista de todos los copropietarios con reconocimiento facial habilitado, incluyendo sus fotos",
        responses={
            200: {
                'type': 'object',
                'properties': {
                    'success': {'type': 'boolean'},
                    'data': {
                        'type': 'array',
                        'items': {
                            'type': 'object',
                            'properties': {
                                'copropietario_id': {'type': 'integer'},
                                'usuario_id': {'type': 'integer', 'nullable': True},
                                'nombres_completos': {'type': 'string'},
                                'documento_identidad': {'type': 'string'},
                                'unidad_residencial': {'type': 'string'},
                                'tipo_residente': {'type': 'string'},
                                'email': {'type': 'string'},
                                'telefono': {'type': 'string'},
                                'foto_perfil_url': {'type': 'string', 'nullable': True},
                                'reconocimiento_facial': {
                                    'type': 'object',
                                    'properties': {
                                        'total_fotos': {'type': 'integer'},
                                        'fecha_ultimo_enrolamiento': {'type': 'string', 'nullable': True},
                                        'ultima_verificacion': {'type': 'string', 'nullable': True},
                                        'fotos_urls': {
                                            'type': 'array',
                                            'items': {'type': 'string'}
                                        }
                                    }
                                },
                                'activo': {'type': 'boolean'},
                                'fecha_creacion': {'type': 'string'}
                            }
                        }
                    },
                    'total': {'type': 'integer'},
                    'estadisticas': {
                        'type': 'object',
                        'properties': {
                            'total_usuarios': {'type': 'integer'},
                            'con_fotos': {'type': 'integer'},
                            'propietarios': {'type': 'integer'},
                            'inquilinos': {'type': 'integer'},
                            'familiares': {'type': 'integer'}
                        }
                    }
                }
            }
        }
    )
    def get(self, request):
        """Listar usuarios con reconocimiento facial"""
        try:
            # Obtener todos los copropietarios activos
            copropietarios = Copropietarios.objects.filter(activo=True).order_by('unidad_residencial')
            
            datos = []
            estadisticas = {
                'total_usuarios': 0,
                'con_fotos': 0,
                'propietarios': 0,
                'inquilinos': 0,
                'familiares': 0
            }
            
            for coprop in copropietarios:
                # Obtener fotos de reconocimiento
                fotos_reconocimiento = ReconocimientoFacial.objects.filter(
                    copropietario=coprop
                ).order_by('-fecha_enrolamiento')
                
                # Solo incluir si tiene fotos
                if fotos_reconocimiento.exists():
                    # ACTUALIZADO: Obtener TODAS las fotos sincronizadas de Dropbox
                    fotos_urls = []
                    for foto in fotos_reconocimiento:
                        # Obtener fotos de Dropbox (múltiples URLs)
                        if foto.fotos_urls:
                            try:
                                fotos_dropbox = json.loads(foto.fotos_urls)
                                if isinstance(fotos_dropbox, list):
                                    fotos_urls.extend(fotos_dropbox)
                            except (json.JSONDecodeError, TypeError):
                                pass
                        
                        # Agregar imagen de referencia si no está en la lista
                        if foto.imagen_referencia_url and foto.imagen_referencia_url not in fotos_urls:
                            fotos_urls.append(foto.imagen_referencia_url)
                    
                    # Obtener información del usuario del sistema si existe
                    usuario_sistema = coprop.usuario_sistema
                    foto_perfil_url = None
                    
                    if usuario_sistema and usuario_sistema.persona:
                        foto_perfil_url = usuario_sistema.persona.foto_perfil_url
                    
                    # Obtener fechas de forma segura
                    primera_foto = fotos_reconocimiento.first()
                    fecha_ultimo_enrolamiento = None
                    ultima_verificacion = None
                    
                    if primera_foto:
                        fecha_ultimo_enrolamiento = primera_foto.fecha_enrolamiento.isoformat()
                        if hasattr(primera_foto, 'ultima_verificacion') and primera_foto.ultima_verificacion:
                            ultima_verificacion = primera_foto.ultima_verificacion.isoformat()
                    
                    datos.append({
                        'copropietario_id': coprop.id,
                        'usuario_id': usuario_sistema.id if usuario_sistema else None,
                        'nombres_completos': f"{coprop.nombres} {coprop.apellidos}",
                        'documento_identidad': coprop.numero_documento,
                        'unidad_residencial': coprop.unidad_residencial,
                        'tipo_residente': coprop.tipo_residente,
                        'email': coprop.email or (usuario_sistema.email if usuario_sistema else ''),
                        'telefono': coprop.telefono or '',
                        'foto_perfil_url': foto_perfil_url,
                        'reconocimiento_facial': {
                            'total_fotos': len(fotos_urls),  # Contar fotos reales sincronizadas
                            'fecha_ultimo_enrolamiento': fecha_ultimo_enrolamiento,
                            'ultima_verificacion': ultima_verificacion,
                            'fotos_urls': fotos_urls  # Mostrar todas las fotos sincronizadas
                        },
                        'activo': coprop.activo,
                        'fecha_creacion': coprop.fecha_creacion.isoformat()
                    })
                    
                    # Actualizar estadísticas
                    estadisticas['con_fotos'] += 1
                    if coprop.tipo_residente == 'Propietario':
                        estadisticas['propietarios'] += 1
                    elif coprop.tipo_residente == 'Inquilino':
                        estadisticas['inquilinos'] += 1
                    elif coprop.tipo_residente == 'Familiar':
                        estadisticas['familiares'] += 1
                
                estadisticas['total_usuarios'] += 1
            
            return Response({
                'success': True,
                'data': datos,
                'total': len(datos),
                'estadisticas': estadisticas
            }, status=status.HTTP_200_OK)
            
        except Exception as e:
            logger.error(f"Error listando usuarios con reconocimiento facial: {str(e)}")
            return Response({
                'success': False,
                'message': f'Error obteniendo usuarios: {str(e)}'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


# ============================================================================
# VISTAS DEL DASHBOARD DE SEGURIDAD
# ============================================================================

class DashboardSeguridadView(APIView):
    """
    Vista para el dashboard principal de seguridad
    GET /api/seguridad/dashboard/
    """
    permission_classes = [IsAuthenticated]
    
    @extend_schema(
        summary="Dashboard de Seguridad",
        description="Obtiene estadísticas generales para el dashboard de seguridad",
        responses={
            200: {
                'type': 'object',
                'properties': {
                    'success': {'type': 'boolean'},
                    'data': {
                        'type': 'object',
                        'properties': {
                            'estadisticas': {
                                'type': 'object',
                                'properties': {
                                    'usuarios_activos': {'type': 'integer'},
                                    'usuarios_con_reconocimiento': {'type': 'integer'},
                                    'incidentes_hoy': {'type': 'integer'},
                                    'visitas_activas': {'type': 'integer'},
                                    'alertas_pendientes': {'type': 'integer'}
                                }
                            },
                            'actividad_reciente': {
                                'type': 'array',
                                'items': {
                                    'type': 'object',
                                    'properties': {
                                        'tipo': {'type': 'string'},
                                        'descripcion': {'type': 'string'},
                                        'timestamp': {'type': 'string'},
                                        'usuario': {'type': 'string'}
                                    }
                                }
                            }
                        }
                    }
                }
            }
        }
    )
    def get(self, request):
        """Obtener datos del dashboard de seguridad"""
        try:
            # Verificar permisos de seguridad
            if not self._verificar_permisos_seguridad(request.user):
                return Response({
                    'success': False,
                    'error': 'No tiene permisos para acceder al dashboard de seguridad'
                }, status=status.HTTP_403_FORBIDDEN)
            
            # Obtener estadísticas
            from authz.models import Usuario
            
            usuarios_activos = Usuario.objects.filter(is_active=True).count()
            usuarios_con_reconocimiento = ReconocimientoFacial.objects.values('copropietario').distinct().count()
            
            # Estadísticas simuladas para incidentes, visitas y alertas
            # TODO: Implementar con modelos reales cuando estén disponibles
            incidentes_hoy = 0
            visitas_activas = 0  
            alertas_pendientes = 0
            
            # Actividad reciente simulada
            actividad_reciente = [
                {
                    'tipo': 'reconocimiento',
                    'descripcion': 'Sistema de reconocimiento facial inicializado',
                    'timestamp': timezone.now().isoformat(),
                    'usuario': 'Sistema'
                }
            ]
            
            return Response({
                'success': True,
                'data': {
                    'estadisticas': {
                        'usuarios_activos': usuarios_activos,
                        'usuarios_con_reconocimiento': usuarios_con_reconocimiento,
                        'incidentes_hoy': incidentes_hoy,
                        'visitas_activas': visitas_activas,
                        'alertas_pendientes': alertas_pendientes
                    },
                    'actividad_reciente': actividad_reciente
                }
            }, status=status.HTTP_200_OK)
            
        except Exception as e:
            logger.error(f"Error en dashboard de seguridad: {str(e)}")
            return Response({
                'success': False,
                'message': f'Error obteniendo datos del dashboard: {str(e)}'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    def _verificar_permisos_seguridad(self, user):
        """Verificar si el usuario tiene permisos de seguridad"""
        try:
            from authz.models import Rol
            security_role = Rol.objects.filter(nombre='security').first()
            admin_role = Rol.objects.filter(nombre='Administrador').first()
            
            user_roles = user.roles.all()
            return (security_role and security_role in user_roles) or (admin_role and admin_role in user_roles)
        except:
            return False


class IncidentesSeguridadView(APIView):
    """
    Vista para listar incidentes de seguridad
    GET /api/seguridad/incidentes/
    """
    permission_classes = [IsAuthenticated]
    
    @extend_schema(
        summary="Incidentes de Seguridad",
        description="Lista los incidentes de seguridad registrados",
        responses={
            200: {
                'type': 'object',
                'properties': {
                    'success': {'type': 'boolean'},
                    'data': {
                        'type': 'array',
                        'items': {
                            'type': 'object',
                            'properties': {
                                'id': {'type': 'integer'},
                                'tipo': {'type': 'string'},
                                'descripcion': {'type': 'string'},
                                'fecha': {'type': 'string'},
                                'estado': {'type': 'string'},
                                'prioridad': {'type': 'string'}
                            }
                        }
                    }
                }
            }
        }
    )
    def get(self, request):
        """Obtener lista de incidentes"""
        try:
            # Verificar permisos de seguridad
            if not self._verificar_permisos_seguridad(request.user):
                return Response({
                    'success': False,
                    'error': 'No tiene permisos para ver incidentes de seguridad'
                }, status=status.HTTP_403_FORBIDDEN)
            
            # TODO: Implementar con modelo real de incidentes
            # Por ahora retornamos datos simulados
            incidentes = [
                {
                    'id': 1,
                    'tipo': 'Acceso no autorizado',
                    'descripcion': 'Intento de acceso sin reconocimiento facial',
                    'fecha': timezone.now().isoformat(),
                    'estado': 'Pendiente',
                    'prioridad': 'Media'
                }
            ]
            
            return Response({
                'success': True,
                'data': incidentes
            }, status=status.HTTP_200_OK)
            
        except Exception as e:
            logger.error(f"Error obteniendo incidentes: {str(e)}")
            return Response({
                'success': False,
                'message': f'Error obteniendo incidentes: {str(e)}'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    def _verificar_permisos_seguridad(self, user):
        """Verificar si el usuario tiene permisos de seguridad"""
        try:
            from authz.models import Rol
            security_role = Rol.objects.filter(nombre='security').first()
            admin_role = Rol.objects.filter(nombre='Administrador').first()
            
            user_roles = user.roles.all()
            return (security_role and security_role in user_roles) or (admin_role and admin_role in user_roles)
        except:
            return False


class VisitasActivasView(APIView):
    """
    Vista para listar visitas activas
    GET /api/seguridad/visitas/activas/
    """
    permission_classes = [IsAuthenticated]
    
    @extend_schema(
        summary="Visitas Activas",
        description="Lista las visitas actualmente en el condominio",
        responses={
            200: {
                'type': 'object',
                'properties': {
                    'success': {'type': 'boolean'},
                    'data': {
                        'type': 'array',
                        'items': {
                            'type': 'object',
                            'properties': {
                                'id': {'type': 'integer'},
                                'visitante': {'type': 'string'},
                                'unidad_destino': {'type': 'string'},
                                'hora_ingreso': {'type': 'string'},
                                'autorizado_por': {'type': 'string'},
                                'estado': {'type': 'string'}
                            }
                        }
                    }
                }
            }
        }
    )
    def get(self, request):
        """Obtener lista de visitas activas"""
        try:
            # Verificar permisos de seguridad
            if not self._verificar_permisos_seguridad(request.user):
                return Response({
                    'success': False,
                    'error': 'No tiene permisos para ver visitas activas'
                }, status=status.HTTP_403_FORBIDDEN)
            
            # TODO: Implementar con modelo real de visitas
            # Por ahora retornamos datos simulados
            visitas = []
            
            return Response({
                'success': True,
                'data': visitas
            }, status=status.HTTP_200_OK)
            
        except Exception as e:
            logger.error(f"Error obteniendo visitas activas: {str(e)}")
            return Response({
                'success': False,
                'message': f'Error obteniendo visitas activas: {str(e)}'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    def _verificar_permisos_seguridad(self, user):
        """Verificar si el usuario tiene permisos de seguridad"""
        try:
            from authz.models import Rol
            security_role = Rol.objects.filter(nombre='security').first()
            admin_role = Rol.objects.filter(nombre='Administrador').first()
            
            user_roles = user.roles.all()
            return (security_role and security_role in user_roles) or (admin_role and admin_role in user_roles)
        except:
            return False


class AlertasActivasView(APIView):
    """
    Vista para listar alertas activas
    GET /api/seguridad/alertas/activas/
    """
    permission_classes = [IsAuthenticated]
    
    @extend_schema(
        summary="Alertas Activas",
        description="Lista las alertas activas del sistema de seguridad",
        responses={
            200: {
                'type': 'object',
                'properties': {
                    'success': {'type': 'boolean'},
                    'data': {
                        'type': 'array',
                        'items': {
                            'type': 'object',
                            'properties': {
                                'id': {'type': 'integer'},
                                'tipo': {'type': 'string'},
                                'mensaje': {'type': 'string'},
                                'fecha': {'type': 'string'},
                                'prioridad': {'type': 'string'},
                                'estado': {'type': 'string'}
                            }
                        }
                    }
                }
            }
        }
    )
    def get(self, request):
        """Obtener lista de alertas activas"""
        try:
            # Verificar permisos de seguridad
            if not self._verificar_permisos_seguridad(request.user):
                return Response({
                    'success': False,
                    'error': 'No tiene permisos para ver alertas activas'
                }, status=status.HTTP_403_FORBIDDEN)
            
            # TODO: Implementar con modelo real de alertas
            # Por ahora retornamos datos simulados
            alertas = []
            
            return Response({
                'success': True,
                'data': alertas
            }, status=status.HTTP_200_OK)
            
        except Exception as e:
            logger.error(f"Error obteniendo alertas activas: {str(e)}")
            return Response({
                'success': False,
                'message': f'Error obteniendo alertas activas: {str(e)}'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    def _verificar_permisos_seguridad(self, user):
        """Verificar si el usuario tiene permisos de seguridad"""
        try:
            from authz.models import Rol
            security_role = Rol.objects.filter(nombre='security').first()
            admin_role = Rol.objects.filter(nombre='Administrador').first()
            
            user_roles = user.roles.all()
            return (security_role and security_role in user_roles) or (admin_role and admin_role in user_roles)
        except:
            return False


class ListaUsuariosActivosView(APIView):
    """
    Vista para listar usuarios activos del sistema
    GET /api/seguridad/lista-usuarios-activos/
    """
    permission_classes = [IsAuthenticated]
    
    @extend_schema(
        summary="Lista de Usuarios Activos",
        description="Lista todos los usuarios activos del sistema para seguridad",
        responses={
            200: {
                'type': 'object',
                'properties': {
                    'success': {'type': 'boolean'},
                    'data': {
                        'type': 'array',
                        'items': {
                            'type': 'object',
                            'properties': {
                                'id': {'type': 'integer'},
                                'email': {'type': 'string'},
                                'nombre_completo': {'type': 'string'},
                                'roles': {'type': 'array', 'items': {'type': 'string'}},
                                'activo': {'type': 'boolean'},
                                'ultima_conexion': {'type': 'string', 'nullable': True},
                                'tiene_reconocimiento': {'type': 'boolean'}
                            }
                        }
                    },
                    'total': {'type': 'integer'}
                }
            }
        }
    )
    def get(self, request):
        """Obtener lista de usuarios activos"""
        try:
            # Verificar permisos de seguridad
            if not self._verificar_permisos_seguridad(request.user):
                return Response({
                    'success': False,
                    'error': 'No tiene permisos para ver la lista de usuarios'
                }, status=status.HTTP_403_FORBIDDEN)
            
            from authz.models import Usuario
            
            # Obtener todos los usuarios activos
            usuarios = Usuario.objects.filter(is_active=True).select_related('persona').prefetch_related('roles')
            
            datos = []
            for usuario in usuarios:
                # Verificar si tiene reconocimiento facial
                tiene_reconocimiento = False
                if usuario.persona:
                    try:
                        copropietario = Copropietarios.objects.filter(
                            email=usuario.email
                        ).first()
                        if copropietario:
                            tiene_reconocimiento = ReconocimientoFacial.objects.filter(
                                copropietario=copropietario
                            ).exists()
                    except:
                        pass
                
                # Obtener roles
                roles = [rol.nombre for rol in usuario.roles.all()]
                
                # Obtener nombre completo
                nombre_completo = "Sin nombre"
                if usuario.persona:
                    try:
                        nombres = getattr(usuario.persona, 'nombres', getattr(usuario.persona, 'nombre', ''))
                        apellidos = getattr(usuario.persona, 'apellidos', getattr(usuario.persona, 'apellido', ''))
                        nombre_completo = f"{nombres} {apellidos}".strip()
                        if not nombre_completo:
                            nombre_completo = "Sin nombre"
                    except:
                        nombre_completo = "Sin nombre"
                
                datos.append({
                    'id': usuario.id,
                    'email': usuario.email,
                    'nombre_completo': nombre_completo,
                    'roles': roles,
                    'activo': usuario.is_active,
                    'ultima_conexion': usuario.last_login.isoformat() if usuario.last_login else None,
                    'tiene_reconocimiento': tiene_reconocimiento
                })
            
            return Response({
                'success': True,
                'data': datos,
                'total': len(datos)
            }, status=status.HTTP_200_OK)
            
        except Exception as e:
            logger.error(f"Error obteniendo lista de usuarios activos: {str(e)}")
            return Response({
                'success': False,
                'message': f'Error obteniendo usuarios activos: {str(e)}'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    def _verificar_permisos_seguridad(self, user):
        """Verificar si el usuario tiene permisos de seguridad"""
        try:
            from authz.models import Rol
            security_role = Rol.objects.filter(nombre='security').first()
            admin_role = Rol.objects.filter(nombre='Administrador').first()
            
            user_roles = user.roles.all()
            return (security_role and security_role in user_roles) or (admin_role and admin_role in user_roles)
        except:
            return False


class PropietariosConReconocimientoView(APIView):
    """
    Vista específica para mostrar solo los propietarios que tienen fotos de reconocimiento facial.
    Diseñada para un apartado específico en el panel de seguridad.
    """
    permission_classes = [IsAuthenticated]
    
    @extend_schema(
        summary="Listar propietarios con reconocimiento facial",
        description="Obtiene lista específica de propietarios que tienen fotos de reconocimiento facial habilitado",
        responses={
            200: {
                'type': 'object',
                'properties': {
                    'success': {'type': 'boolean'},
                    'data': {
                        'type': 'object',
                        'properties': {
                            'propietarios': {
                                'type': 'array',
                                'items': {
                                    'type': 'object',
                                    'properties': {
                                        'copropietario_id': {'type': 'integer'},
                                        'usuario_id': {'type': 'integer', 'nullable': True},
                                        'nombre_completo': {'type': 'string'},
                                        'documento': {'type': 'string'},
                                        'unidad': {'type': 'string'},
                                        'email': {'type': 'string'},
                                        'telefono': {'type': 'string'},
                                        'foto_perfil': {'type': 'string', 'nullable': True},
                                        'fotos_reconocimiento': {
                                            'type': 'object',
                                            'properties': {
                                                'cantidad': {'type': 'integer'},
                                                'urls': {
                                                    'type': 'array',
                                                    'items': {'type': 'string'}
                                                },
                                                'fecha_registro': {'type': 'string'},
                                                'ultima_actualizacion': {'type': 'string', 'nullable': True}
                                            }
                                        },
                                        'estado': {'type': 'string'}
                                    }
                                }
                            },
                            'resumen': {
                                'type': 'object',
                                'properties': {
                                    'total_propietarios': {'type': 'integer'},
                                    'con_reconocimiento': {'type': 'integer'},
                                    'sin_reconocimiento': {'type': 'integer'},
                                    'porcentaje_cobertura': {'type': 'number'},
                                    'total_fotos': {'type': 'integer'}
                                }
                            }
                        }
                    },
                    'message': {'type': 'string'}
                }
            }
        }
    )
    def get(self, request):
        """Obtener propietarios con reconocimiento facial"""
        try:
            # Obtener todos los propietarios activos
            propietarios_total = Copropietarios.objects.filter(
                activo=True,
                tipo_residente='Propietario'
            ).count()
            
            # Obtener propietarios con reconocimiento facial
            propietarios_con_reconocimiento = Copropietarios.objects.filter(
                activo=True,
                tipo_residente='Propietario'
            ).prefetch_related('reconocimiento_facial').order_by('unidad_residencial', 'apellidos')
            
            datos_propietarios = []
            propietarios_con_fotos = 0
            total_fotos = 0
            
            for propietario in propietarios_con_reconocimiento:
                # Verificar si tiene fotos de reconocimiento
                fotos_reconocimiento = ReconocimientoFacial.objects.filter(
                    copropietario=propietario,
                    activo=True
                )
                
                # Solo incluir si tiene fotos
                if fotos_reconocimiento.exists():
                    # Recopilar todas las URLs de fotos
                    fotos_urls = []
                    fecha_registro = None
                    ultima_actualizacion = None
                    
                    for foto_reg in fotos_reconocimiento:
                        # Obtener fotos de Dropbox (múltiples URLs)
                        if foto_reg.fotos_urls:
                            try:
                                fotos_dropbox = json.loads(foto_reg.fotos_urls)
                                if isinstance(fotos_dropbox, list):
                                    fotos_urls.extend(fotos_dropbox)
                            except (json.JSONDecodeError, TypeError):
                                pass
                        
                        # Agregar imagen de referencia si existe
                        if foto_reg.imagen_referencia_url and foto_reg.imagen_referencia_url not in fotos_urls:
                            fotos_urls.append(foto_reg.imagen_referencia_url)
                        
                        # Obtener fechas
                        if not fecha_registro or foto_reg.fecha_enrolamiento < fecha_registro:
                            fecha_registro = foto_reg.fecha_enrolamiento
                        
                        # Usar fecha_actualizacion en lugar de updated_at
                        if not ultima_actualizacion or foto_reg.fecha_actualizacion > ultima_actualizacion:
                            ultima_actualizacion = foto_reg.fecha_actualizacion
                    
                    # Solo incluir si realmente tiene fotos
                    if fotos_urls:
                        # Obtener información del usuario del sistema
                        usuario_sistema = propietario.usuario_sistema
                        foto_perfil = None
                        
                        if usuario_sistema and usuario_sistema.persona:
                            foto_perfil = usuario_sistema.persona.foto_perfil_url
                        
                        datos_propietarios.append({
                            'copropietario_id': propietario.id,
                            'usuario_id': usuario_sistema.id if usuario_sistema else None,
                            'nombre_completo': f"{propietario.nombres} {propietario.apellidos}",
                            'documento': propietario.numero_documento,
                            'unidad': propietario.unidad_residencial,
                            'email': propietario.email or (usuario_sistema.email if usuario_sistema else ''),
                            'telefono': propietario.telefono or '',
                            'foto_perfil': foto_perfil,
                            'fotos_reconocimiento': {
                                'cantidad': len(fotos_urls),
                                'urls': fotos_urls,
                                'fecha_registro': fecha_registro.isoformat() if fecha_registro else None,
                                'ultima_actualizacion': ultima_actualizacion.isoformat() if ultima_actualizacion else None
                            },
                            'estado': 'Activo con reconocimiento'
                        })
                        
                        propietarios_con_fotos += 1
                        total_fotos += len(fotos_urls)
            
            # Calcular estadísticas
            porcentaje_cobertura = (propietarios_con_fotos / propietarios_total * 100) if propietarios_total > 0 else 0
            propietarios_sin_reconocimiento = propietarios_total - propietarios_con_fotos
            
            return Response({
                'success': True,
                'data': {
                    'propietarios': datos_propietarios,
                    'resumen': {
                        'total_propietarios': propietarios_total,
                        'con_reconocimiento': propietarios_con_fotos,
                        'sin_reconocimiento': propietarios_sin_reconocimiento,
                        'porcentaje_cobertura': round(porcentaje_cobertura, 2),
                        'total_fotos': total_fotos
                    }
                },
                'message': f'Se encontraron {propietarios_con_fotos} propietarios con reconocimiento facial de {propietarios_total} totales'
            }, status=status.HTTP_200_OK)
            
        except Exception as e:
            logger.error(f"Error obteniendo propietarios con reconocimiento facial: {str(e)}")
            return Response({
                'success': False,
                'message': f'Error obteniendo propietarios con reconocimiento: {str(e)}'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class ReconocerTiempoRealView(APIView):
    """
    Endpoint para reconocimiento facial en tiempo real con cámara web
    POST /api/seguridad/reconocer-tiempo-real/
    """
    permission_classes = []  # Sin autenticación - para demo rápida
    parser_classes = [MultiPartParser, FormParser]
    
    @extend_schema(
        summary="Reconocimiento Facial en Tiempo Real",
        description="Procesa frame de cámara web y compara con base de datos Dropbox",
        request={
            'multipart/form-data': {
                'type': 'object',
                'properties': {
                    'imagen': {
                        'type': 'string',
                        'format': 'binary',
                        'description': 'Frame capturado de la cámara web'
                    }
                }
            }
        },
        responses={
            200: {
                'type': 'object',
                'properties': {
                    'reconocido': {'type': 'boolean'},
                    'persona': {
                        'type': 'object',
                        'properties': {
                            'nombre': {'type': 'string'},
                            'vivienda': {'type': 'string'},
                            'tipo_residente': {'type': 'string'},
                            'documento': {'type': 'string'}
                        }
                    },
                    'confianza': {'type': 'number'},
                    'proveedor': {'type': 'string'},
                    'timestamp': {'type': 'string'}
                }
            }
        }
    )
    def post(self, request):
        """Procesar frame de cámara web para reconocimiento"""
        try:
            # Validar que se recibió una imagen
            if 'imagen' not in request.FILES:
                return Response({
                    'reconocido': False,
                    'error': 'No se recibió imagen'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            imagen = request.FILES['imagen']
            imagen_bytes = imagen.read()
            
            # Usar el proveedor de reconocimiento existente
            from .services.realtime_face_provider import OpenCVFaceProvider
            
            provider = OpenCVFaceProvider()
            
            # Obtener todas las personas con reconocimiento facial de la BD
            personas_bd = []
            reconocimientos = ReconocimientoFacial.objects.filter(activo=True).select_related('copropietario')
            
            for reconocimiento in reconocimientos:
                personas_bd.append({
                    'persona': reconocimiento.copropietario,
                    'reconocimiento': reconocimiento
                })
            
            # Procesar reconocimiento
            resultados = provider.procesar_imagen_multiple(imagen_bytes, personas_bd)
            
            if resultados and len(resultados) > 0:
                # Persona reconocida
                resultado = resultados[0]  # Tomar el mejor match
                persona = resultado['persona']
                
                # Registrar en bitácora
                fn_bitacora_log(
                    tipo_accion='RECONOCIMIENTO_TIEMPO_REAL',
                    descripcion=f'Reconocimiento exitoso desde cámara web: {persona.nombre_completo}',
                    usuario=None,  # Usuario anónimo para demo
                    copropietario=persona,
                    direccion_ip=get_client_ip(request),
                    user_agent=request.META.get('HTTP_USER_AGENT'),
                    proveedor_ia='OpenCV',
                    confianza=resultado['confianza'],
                    resultado_match=True
                )
                
                return Response({
                    'reconocido': True,
                    'persona': {
                        'nombre': f"{persona.nombres} {persona.apellidos}",
                        'vivienda': persona.unidad_residencial,
                        'tipo_residente': persona.tipo_residente,
                        'documento': persona.numero_documento
                    },
                    'confianza': resultado['confianza'],
                    'proveedor': 'OpenCV + face_recognition',
                    'timestamp': timezone.now().isoformat()
                }, status=status.HTTP_200_OK)
            
            else:
                # No se reconoció a nadie
                fn_bitacora_log(
                    tipo_accion='RECONOCIMIENTO_TIEMPO_REAL',
                    descripcion='Reconocimiento fallido desde cámara web: persona no identificada',
                    usuario=None,
                    copropietario=None,
                    direccion_ip=get_client_ip(request),
                    user_agent=request.META.get('HTTP_USER_AGENT'),
                    proveedor_ia='OpenCV',
                    resultado_match=False
                )
                
                return Response({
                    'reconocido': False,
                    'persona': None,
                    'confianza': 0.0,
                    'proveedor': 'OpenCV + face_recognition',
                    'timestamp': timezone.now().isoformat()
                }, status=status.HTTP_200_OK)
        
        except Exception as e:
            logger.error(f"Error en reconocimiento tiempo real: {str(e)}")
            
            # Registrar error en bitácora
            fn_bitacora_log(
                tipo_accion='SYSTEM_ERROR',
                descripcion=f'Error en reconocimiento tiempo real: {str(e)}',
                usuario=None,
                direccion_ip=get_client_ip(request),
                user_agent=request.META.get('HTTP_USER_AGENT')
            )
            
            return Response({
                'reconocido': False,
                'error': f'Error procesando imagen: {str(e)}',
                'timestamp': timezone.now().isoformat()
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class HealthCheckView(APIView):
    """
    Vista simple para verificar que el backend esté funcionando
    No requiere autenticación - para testing de conectividad
    """
    permission_classes = []  # Sin autenticación requerida
    
    @extend_schema(
        summary="Health Check",
        description="Verifica que el backend esté funcionando correctamente",
        responses={
            200: {
                'type': 'object',
                'properties': {
                    'success': {'type': 'boolean'},
                    'message': {'type': 'string'},
                    'timestamp': {'type': 'string'},
                    'status': {'type': 'string'}
                }
            }
        }
    )
    def get(self, request):
        """
        Endpoint simple para verificar conectividad
        """
        try:
            return Response({
                'success': True,
                'message': 'Backend funcionando correctamente',
                'timestamp': timezone.now().isoformat(),
                'status': 'online',
                'version': '1.0.0'
            }, status=status.HTTP_200_OK)
            
        except Exception as e:
            return Response({
                'success': False,
                'message': f'Error en health check: {str(e)}',
                'timestamp': timezone.now().isoformat(),
                'status': 'error'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
