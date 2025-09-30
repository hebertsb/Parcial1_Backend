"""
Endpoints específicos para sincronización de reconocimiento facial
"""

from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from drf_spectacular.utils import extend_schema, OpenApiResponse

from .services.sincronizacion_service import SincronizacionReconocimientoService
from .models import Copropietarios


@api_view(['POST'])
@permission_classes([IsAuthenticated])
@extend_schema(
    summary="Sincronizar fotos de propietario con sistema de seguridad",
    description="Sincroniza automáticamente las fotos de un propietario específico con el sistema de seguridad",
    request={
        'type': 'object',
        'properties': {
            'copropietario_id': {
                'type': 'integer',
                'description': 'ID del copropietario a sincronizar'
            }
        },
        'required': ['copropietario_id']
    },
    responses={
        200: OpenApiResponse(description="Sincronización exitosa"),
        404: OpenApiResponse(description="Copropietario no encontrado"),
        500: OpenApiResponse(description="Error en sincronización")
    }
)
def sincronizar_fotos_propietario(request):
    """
from rest_framework.permissions import IsAuthenticated
    Sincroniza las fotos de un propietario específico con el sistema de seguridad
    
    POST /api/seguridad/sincronizar-fotos/
    """
    try:
        copropietario_id = request.data.get('copropietario_id')
        
        if not copropietario_id:
            return Response({
                'success': False,
                'error': 'copropietario_id es requerido'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Verificar que el copropietario existe
        try:
            copropietario = Copropietarios.objects.get(id=copropietario_id)
        except Copropietarios.DoesNotExist:
            return Response({
                'success': False,
                'error': f'Copropietario {copropietario_id} no encontrado'
            }, status=status.HTTP_404_NOT_FOUND)
        
        # Realizar sincronización completa
        resultado = SincronizacionReconocimientoService.sincronizar_todas_las_fotos_propietario(copropietario_id)
        
        if resultado['success']:
            return Response({
                'success': True,
                'message': f'Sincronización completada para {copropietario.nombre_completo}',
                'data': {
                    'copropietario_id': copropietario_id,
                    'nombre_completo': copropietario.nombre_completo,
                    'total_fotos_sincronizadas': resultado.get('total_fotos_sincronizadas', 0),
                    'fotos_urls': resultado.get('fotos_urls', [])
                }
            })
        else:
            return Response({
                'success': False,
                'error': resultado.get('error', 'Error desconocido en sincronización')
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            
    except Exception as e:
        return Response({
            'success': False,
            'error': f'Error interno: {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
@extend_schema(
    summary="Obtener estadísticas de sincronización",
    description="Obtiene estadísticas detalladas sobre el estado de sincronización entre sistemas",
    responses={
        200: {
            'type': 'object',
            'properties': {
                'success': {'type': 'boolean'},
                'data': {
                    'type': 'object',
                    'properties': {
                        'total_usuarios_reconocimiento': {'type': 'integer'},
                        'usuarios_con_fotos_dropbox': {'type': 'integer'},
                        'usuarios_sin_fotos': {'type': 'integer'},
                        'total_fotos_sincronizadas': {'type': 'integer'},
                        'porcentaje_sincronizacion': {'type': 'number'}
                    }
                }
            }
        }
    }
)
def estadisticas_sincronizacion(request):
    """
    Obtiene estadísticas de sincronización entre sistemas
    
    GET /api/seguridad/estadisticas-sincronizacion/
    """
    try:
        estadisticas = SincronizacionReconocimientoService.obtener_estadisticas_sincronizacion()
        
        if 'error' in estadisticas:
            return Response({
                'success': False,
                'error': estadisticas['error']
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
        return Response({
            'success': True,
            'data': estadisticas
        })
        
    except Exception as e:
        return Response({
            'success': False,
            'error': f'Error obteniendo estadísticas: {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
@extend_schema(
    summary="Sincronizar todos los usuarios con el sistema de seguridad",
    description="Ejecuta una sincronización masiva de todos los usuarios con fotos",
    responses={
        200: OpenApiResponse(description="Sincronización masiva completada"),
        500: OpenApiResponse(description="Error en sincronización masiva")
    }
)
def sincronizar_todos_usuarios(request):
    """
    Sincroniza todos los usuarios con fotos al sistema de seguridad
    
    POST /api/seguridad/sincronizar-todos/
    """
    try:
        # Obtener todos los copropietarios activos
        copropietarios = Copropietarios.objects.filter(activo=True)
        
        resultados = {
            'total_procesados': 0,
            'exitosos': 0,
            'errores': 0,
            'detalles': []
        }
        
        for copropietario in copropietarios:
            resultado = SincronizacionReconocimientoService.sincronizar_todas_las_fotos_propietario(copropietario.id)
            
            resultados['total_procesados'] += 1
            
            if resultado['success']:
                resultados['exitosos'] += 1
                if resultado.get('total_fotos_sincronizadas', 0) > 0:
                    resultados['detalles'].append({
                        'copropietario_id': copropietario.id,
                        'nombre': copropietario.nombre_completo,
                        'fotos_sincronizadas': resultado['total_fotos_sincronizadas'],
                        'status': 'sincronizado'
                    })
            else:
                resultados['errores'] += 1
                resultados['detalles'].append({
                    'copropietario_id': copropietario.id,
                    'nombre': copropietario.nombre_completo,
                    'error': resultado.get('error', 'Error desconocido'),
                    'status': 'error'
                })
        
        return Response({
            'success': True,
            'message': f'Sincronización masiva completada. {resultados["exitosos"]}/{resultados["total_procesados"]} usuarios procesados exitosamente',
            'data': resultados
        })
        
    except Exception as e:
        return Response({
            'success': False,
            'error': f'Error en sincronización masiva: {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)