"""
Face Recognition API Views
"""

import logging
from datetime import datetime
from typing import Dict, Any, cast
from django.utils import timezone
from django.http import Http404
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.throttling import UserRateThrottle
from drf_spectacular.utils import extend_schema, OpenApiExample
from drf_spectacular.types import OpenApiTypes

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
            
            # Obtener copropietario
            try:
                copropietario = Copropietarios.objects.get(id=copropietario_id, activo=True)
            except Copropietarios.DoesNotExist:
                return Response(
                    {'error': 'Copropietario no encontrado'},
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
                reconocimiento.imagen_referencia_url = enroll_result.get('image_url')
                reconocimiento.confianza_enrolamiento = enroll_result.get('confidence')
                reconocimiento.fecha_modificacion = now
                reconocimiento.save()
                
                response_status = status.HTTP_200_OK
                
            else:
                # Crear nuevo
                reconocimiento = ReconocimientoFacial.objects.create(
                    copropietario=copropietario,
                    proveedor_ia=enroll_result['provider'],
                    vector_facial=enroll_result['face_reference'],
                    imagen_referencia_url=enroll_result.get('image_url'),
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
            
            # Obtener copropietario y reconocimiento facial
            try:
                copropietario = Copropietarios.objects.get(id=copropietario_id, activo=True)
                reconocimiento = ReconocimientoFacial.objects.get(
                    copropietario=copropietario,
                    activo=True
                )
            except Copropietarios.DoesNotExist:
                return Response(
                    {'error': 'Copropietario no encontrado'},
                    status=status.HTTP_404_NOT_FOUND
                )
            except ReconocimientoFacial.DoesNotExist:
                return Response(
                    {'error': 'Copropietario no tiene enrolamiento facial activo'},
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
                    {'error': 'Copropietario no encontrado'},
                    status=status.HTTP_404_NOT_FOUND
                )
            except ReconocimientoFacial.DoesNotExist:
                return Response(
                    {'error': 'Copropietario no tiene enrolamiento facial activo'},
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
                    {'error': 'Copropietario no encontrado'},
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
