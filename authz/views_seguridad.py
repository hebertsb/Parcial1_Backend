"""
Vistas para el panel de seguridad - Gestión de reconocimiento facial
"""
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.authentication import JWTAuthentication
from drf_spectacular.utils import extend_schema, OpenApiResponse
import json

class ListarUsuariosConFotosView(APIView):
    """Vista para listar todos los usuarios con fotos de reconocimiento facial"""
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]
    
    @extend_schema(
        summary="Listar usuarios con fotos de reconocimiento",
        description="Obtiene todos los copropietarios que tienen fotos de reconocimiento facial cargadas",
        responses={
            200: OpenApiResponse(description="Lista de usuarios con fotos"),
            403: OpenApiResponse(description="Sin permisos de seguridad"),
            401: OpenApiResponse(description="No autorizado")
        }
    )
    def get(self, request):
        """Obtener todos los usuarios con fotos de reconocimiento"""
        try:
            from seguridad.models import Copropietarios, ReconocimientoFacial
            
            usuario = request.user
            
            # Verificar que el usuario tiene rol de Seguridad
            roles_usuario = [rol.nombre for rol in usuario.roles.all()]
            if 'Seguridad' not in roles_usuario and 'security' not in roles_usuario and not usuario.is_superuser:
                return Response({
                    'success': False,
                    'error': 'No tienes permisos para acceder a esta información'
                }, status=403)
            
            # Obtener todos los copropietarios con reconocimiento facial
            reconocimientos = ReconocimientoFacial.objects.filter(
                activo=True,
                fotos_urls__isnull=False
            ).exclude(fotos_urls='').select_related('copropietario')
            
            usuarios_con_fotos = []
            
            for reconocimiento in reconocimientos:
                copropietario = reconocimiento.copropietario
                
                # Parsear las URLs de fotos
                fotos_urls = []
                if reconocimiento.fotos_urls:
                    try:
                        fotos_list = json.loads(reconocimiento.fotos_urls)
                        if isinstance(fotos_list, list):
                            fotos_urls = fotos_list
                    except (json.JSONDecodeError, TypeError):
                        pass
                
                # Solo incluir si tiene fotos válidas
                if fotos_urls:
                    usuario_data = {
                        'copropietario_id': copropietario.id,
                        'nombre_completo': f"{copropietario.nombres} {copropietario.apellidos}",
                        'documento': copropietario.numero_documento,
                        'tipo_documento': copropietario.tipo_documento,
                        'unidad_residencial': copropietario.unidad_residencial,
                        'tipo_residente': copropietario.tipo_residente,
                        'telefono': copropietario.telefono or '',
                        'email': copropietario.email or '',
                        'reconocimiento_id': reconocimiento.id,
                        'total_fotos': len(fotos_urls),
                        'fotos_urls': fotos_urls,
                        'fecha_enrolamiento': reconocimiento.fecha_enrolamiento.isoformat() if reconocimiento.fecha_enrolamiento else None,
                        'ultima_actualizacion': reconocimiento.fecha_actualizacion.isoformat() if reconocimiento.fecha_actualizacion else None,
                        'activo': copropietario.activo
                    }
                    usuarios_con_fotos.append(usuario_data)
            
            return Response({
                'success': True,
                'data': {
                    'total_usuarios': len(usuarios_con_fotos),
                    'usuarios': usuarios_con_fotos
                }
            })
            
        except Exception as e:
            return Response({
                'success': False,
                'error': f'Error interno: {str(e)}'
            }, status=500)


class DetalleUsuarioFotosView(APIView):
    """Vista para obtener detalles de fotos de un usuario específico"""
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]
    
    @extend_schema(
        summary="Obtener detalles de fotos de un usuario",
        description="Obtiene información detallada de las fotos de reconocimiento de un copropietario específico",
        responses={
            200: OpenApiResponse(description="Detalles de fotos del usuario"),
            404: OpenApiResponse(description="Usuario no encontrado"),
            403: OpenApiResponse(description="Sin permisos de seguridad"),
            401: OpenApiResponse(description="No autorizado")
        }
    )
    def get(self, request, copropietario_id):
        """Obtener detalles de fotos de un copropietario específico"""
        try:
            from seguridad.models import Copropietarios, ReconocimientoFacial
            
            usuario = request.user
            
            # Verificar que el usuario tiene rol de Seguridad
            roles_usuario = [rol.nombre for rol in usuario.roles.all()]
            if 'Seguridad' not in roles_usuario and 'security' not in roles_usuario and not usuario.is_superuser:
                return Response({
                    'success': False,
                    'error': 'No tienes permisos para acceder a esta información'
                }, status=403)
            
            # Buscar copropietario
            try:
                copropietario = Copropietarios.objects.get(id=copropietario_id)
            except Copropietarios.DoesNotExist:
                return Response({
                    'success': False,
                    'error': 'Copropietario no encontrado'
                }, status=404)
            
            # Buscar reconocimiento facial
            reconocimiento = ReconocimientoFacial.objects.filter(copropietario=copropietario).first()
            
            if not reconocimiento:
                return Response({
                    'success': True,
                    'data': {
                        'copropietario': {
                            'id': copropietario.id,
                            'nombre_completo': f"{copropietario.nombres} {copropietario.apellidos}",
                            'documento': copropietario.numero_documento,
                            'unidad_residencial': copropietario.unidad_residencial,
                            'tipo_residente': copropietario.tipo_residente,
                            'telefono': copropietario.telefono or '',
                            'email': copropietario.email or '',
                        },
                        'reconocimiento': {
                            'tiene_reconocimiento': False,
                            'total_fotos': 0,
                            'fotos_urls': []
                        }
                    }
                })
            
            # Obtener URLs de fotos
            fotos_urls = []
            if reconocimiento.fotos_urls:
                try:
                    fotos_list = json.loads(reconocimiento.fotos_urls)
                    if isinstance(fotos_list, list):
                        fotos_urls = fotos_list
                except (json.JSONDecodeError, TypeError):
                    pass
            
            return Response({
                'success': True,
                'data': {
                    'copropietario': {
                        'id': copropietario.id,
                        'nombre_completo': f"{copropietario.nombres} {copropietario.apellidos}",
                        'documento': copropietario.numero_documento,
                        'tipo_documento': copropietario.tipo_documento,
                        'unidad_residencial': copropietario.unidad_residencial,
                        'tipo_residente': copropietario.tipo_residente,
                        'telefono': copropietario.telefono or '',
                        'email': copropietario.email or '',
                        'activo': copropietario.activo
                    },
                    'reconocimiento': {
                        'id': reconocimiento.id,
                        'tiene_reconocimiento': True,
                        'total_fotos': len(fotos_urls),
                        'fotos_urls': fotos_urls,
                        'fecha_enrolamiento': reconocimiento.fecha_enrolamiento.isoformat() if reconocimiento.fecha_enrolamiento else None,
                        'ultima_actualizacion': reconocimiento.fecha_actualizacion.isoformat() if reconocimiento.fecha_actualizacion else None,
                        'proveedor_ia': reconocimiento.proveedor_ia,
                        'activo': reconocimiento.activo
                    }
                }
            })
            
        except Exception as e:
            return Response({
                'success': False,
                'error': f'Error interno: {str(e)}'
            }, status=500)


class EstadisticasReconocimientoView(APIView):
    """Vista para obtener estadísticas del sistema de reconocimiento facial"""
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]
    
    @extend_schema(
        summary="Obtener estadísticas de reconocimiento facial",
        description="Obtiene estadísticas generales del sistema de reconocimiento facial",
        responses={
            200: OpenApiResponse(description="Estadísticas del sistema"),
            403: OpenApiResponse(description="Sin permisos de seguridad"),
            401: OpenApiResponse(description="No autorizado")
        }
    )
    def get(self, request):
        """Obtener estadísticas del sistema de reconocimiento"""
        try:
            from seguridad.models import Copropietarios, ReconocimientoFacial
            
            usuario = request.user
            
            # Verificar que el usuario tiene rol de Seguridad
            roles_usuario = [rol.nombre for rol in usuario.roles.all()]
            if 'Seguridad' not in roles_usuario and 'security' not in roles_usuario and not usuario.is_superuser:
                return Response({
                    'success': False,
                    'error': 'No tienes permisos para acceder a esta información'
                }, status=403)
            
            # Contar copropietarios totales
            total_copropietarios = Copropietarios.objects.filter(activo=True).count()
            
            # Contar reconocimientos activos
            total_reconocimientos = ReconocimientoFacial.objects.filter(activo=True).count()
            
            # Contar usuarios con fotos
            reconocimientos_con_fotos = ReconocimientoFacial.objects.filter(
                activo=True,
                fotos_urls__isnull=False
            ).exclude(fotos_urls='')
            
            usuarios_con_fotos = 0
            total_fotos = 0
            
            for reconocimiento in reconocimientos_con_fotos:
                if reconocimiento.fotos_urls:
                    try:
                        fotos_list = json.loads(reconocimiento.fotos_urls)
                        if isinstance(fotos_list, list) and len(fotos_list) > 0:
                            usuarios_con_fotos += 1
                            total_fotos += len(fotos_list)
                    except (json.JSONDecodeError, TypeError):
                        pass
            
            # Estadísticas por tipo de residente
            tipos_residente = Copropietarios.objects.filter(activo=True).values_list('tipo_residente', flat=True)
            estadisticas_tipos = {}
            for tipo in tipos_residente:
                if tipo not in estadisticas_tipos:
                    estadisticas_tipos[tipo] = 0
                estadisticas_tipos[tipo] += 1
            
            return Response({
                'success': True,
                'data': {
                    'totales': {
                        'copropietarios_activos': total_copropietarios,
                        'usuarios_con_reconocimiento': total_reconocimientos,
                        'usuarios_con_fotos': usuarios_con_fotos,
                        'total_fotos_sistema': total_fotos
                    },
                    'porcentajes': {
                        'cobertura_reconocimiento': round((total_reconocimientos / total_copropietarios * 100), 2) if total_copropietarios > 0 else 0,
                        'usuarios_con_fotos': round((usuarios_con_fotos / total_copropietarios * 100), 2) if total_copropietarios > 0 else 0
                    },
                    'por_tipo_residente': estadisticas_tipos,
                    'promedio_fotos_por_usuario': round((total_fotos / usuarios_con_fotos), 2) if usuarios_con_fotos > 0 else 0
                }
            })
            
        except Exception as e:
            return Response({
                'success': False,
                'error': f'Error interno: {str(e)}'
            }, status=500)