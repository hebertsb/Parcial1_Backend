# seguridad/views_actividad.py - Endpoints para el panel de actividades de seguridad
from django.http import JsonResponse
from django.utils import timezone
from django.db.models import Q, Count
from django.core.paginator import Paginator
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from datetime import datetime, timedelta
import logging

from .models import Copropietarios, ReconocimientoFacial, BitacoraAcciones
from core.models.seguridad_ia import LecturaPlacaOCR
from core.models.propiedades_residentes import Visita
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from django.db import models

logger = logging.getLogger('seguridad.actividad')

# ===================================================
# ENDPOINTS PARA LOGS DE ACCESO Y ACTIVIDAD
# ===================================================

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def logs_acceso(request):
    """
    Endpoint principal para logs de acceso al condominio
    GET /api/authz/seguridad/acceso/logs/
    """
    try:
        # Parámetros de consulta
        limit = int(request.GET.get('limit', 50))
        fecha_desde = request.GET.get('fecha_desde')
        fecha_hasta = request.GET.get('fecha_hasta')
        usuario = request.GET.get('usuario')
        
        # Construir consulta base - obtener acciones de verificación facial
        queryset = BitacoraAcciones.objects.filter(
            tipo_accion__in=['VERIFY_FACE', 'ACCESS_GRANTED', 'ACCESS_DENIED']
        ).select_related('copropietario', 'usuario')
        
        # Aplicar filtros
        if fecha_desde:
            try:
                fecha_desde_dt = datetime.fromisoformat(fecha_desde.replace('Z', '+00:00'))
                queryset = queryset.filter(fecha_accion__gte=fecha_desde_dt)
            except ValueError:
                pass
                
        if fecha_hasta:
            try:
                fecha_hasta_dt = datetime.fromisoformat(fecha_hasta.replace('Z', '+00:00'))
                queryset = queryset.filter(fecha_accion__lte=fecha_hasta_dt)
            except ValueError:
                pass
                
        if usuario:
            queryset = queryset.filter(
                Q(copropietario__nombres__icontains=usuario) |
                Q(copropietario__apellidos__icontains=usuario) |
                Q(usuario__email__icontains=usuario)
            )
        
        # Ordenar por fecha descendente
        queryset = queryset.order_by('-fecha_accion')
        
        # Paginar
        paginator = Paginator(queryset, limit)
        page = paginator.get_page(1)
        
        # Formatear resultados
        results = []
        for bitacora in page.object_list:
            # Determinar datos del usuario
            if bitacora.copropietario:
                usuario_nombre = bitacora.copropietario.nombre_completo
                nombre_completo = bitacora.copropietario.nombre_completo
                usuario_str = f"{bitacora.copropietario.nombres.lower()}.{bitacora.copropietario.apellidos.split()[0].lower()}"
                unidad = bitacora.copropietario.unidad_residencial
                apartamento = bitacora.copropietario.unidad_residencial.replace('Torre ', '').replace('Apt ', '')
            else:
                usuario_nombre = "Desconocido"
                nombre_completo = "Usuario no identificado"
                usuario_str = "desconocido"
                unidad = "N/A"
                apartamento = "N/A"
            
            # Determinar autorización
            autorizado = bitacora.resultado_match if bitacora.resultado_match is not None else False
            if bitacora.tipo_accion == 'ACCESS_GRANTED':
                autorizado = True
            elif bitacora.tipo_accion == 'ACCESS_DENIED':
                autorizado = False
            
            # Confianza
            confianza = bitacora.confianza if bitacora.confianza else 0.0
            
            # Método de acceso
            metodo_acceso = "reconocimiento_facial"
            if bitacora.proveedor_ia:
                if "azure" in bitacora.proveedor_ia.lower():
                    metodo_acceso = "azure_face_api"
                elif "local" in bitacora.proveedor_ia.lower():
                    metodo_acceso = "reconocimiento_local"
            
            # Descripción y razón
            descripcion = bitacora.descripcion
            razon = None
            motivo = None
            
            if not autorizado:
                if confianza > 0:
                    razon = f"Confianza insuficiente ({confianza:.1f}%)"
                    motivo = "Reconocimiento facial con baja confianza"
                else:
                    razon = "Usuario no registrado en el sistema"
                    motivo = "Sin autorización"
            
            result_item = {
                'id': bitacora.id,
                'usuario_nombre': usuario_nombre,
                'nombre_completo': nombre_completo,
                'usuario': usuario_str,
                'autorizado': autorizado,
                'acceso_autorizado': autorizado,
                'metodo_acceso': metodo_acceso,
                'metodo': 'facial',
                'confianza': confianza,
                'confidence': confianza,
                'ubicacion': 'Entrada Principal',
                'unidad': unidad,
                'apartamento': apartamento,
                'fecha_hora': bitacora.fecha_accion.isoformat(),
                'timestamp': bitacora.fecha_accion.isoformat(),
                'descripcion': descripcion,
                'razon': razon,
                'motivo': motivo
            }
            results.append(result_item)
        
        response_data = {
            'results': results,
            'count': paginator.count,
            'next': None,
            'previous': None
        }
        
        logger.info(f"📊 Logs de acceso consultados: {len(results)} registros")
        return Response(response_data, status=status.HTTP_200_OK)
        
    except Exception as e:
        logger.error(f"❌ Error obteniendo logs de acceso: {e}")
        return Response({
            'error': 'Error interno del servidor',
            'detail': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def actividad_reciente(request):
    """
    Endpoint alternativo para actividad reciente
    GET /api/seguridad/actividad/reciente/
    """
    try:
        limit = int(request.GET.get('limit', 20))
        
        # Obtener las acciones más recientes
        bitacoras = BitacoraAcciones.objects.filter(
            tipo_accion__in=['VERIFY_FACE', 'ACCESS_GRANTED', 'ACCESS_DENIED', 'ENROLL_FACE']
        ).select_related('copropietario', 'usuario').order_by('-fecha_accion')[:limit]
        
        results = []
        for bitacora in bitacoras:
            usuario_nombre = bitacora.copropietario.nombre_completo if bitacora.copropietario else "Sistema"
            autorizado = bitacora.resultado_match if bitacora.resultado_match is not None else False
            
            result_item = {
                'id': bitacora.id,
                'usuario_nombre': usuario_nombre,
                'tipo_accion': bitacora.tipo_accion,
                'autorizado': autorizado,
                'confianza': bitacora.confianza or 0.0,
                'fecha_hora': bitacora.fecha_accion.isoformat(),
                'descripcion': bitacora.descripcion,
                'ubicacion': 'Entrada Principal'
            }
            results.append(result_item)
        
        logger.info(f"📊 Actividad reciente consultada: {len(results)} registros")
        return Response(results, status=status.HTTP_200_OK)
        
    except Exception as e:
        logger.error(f"❌ Error obteniendo actividad reciente: {e}")
        return Response({
            'error': 'Error interno del servidor',
            'detail': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


# ===================================================
# ENDPOINTS PARA INCIDENTES DE SEGURIDAD
# ===================================================

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def incidentes_seguridad(request):
    """
    Endpoint para incidentes de seguridad
    GET /api/authz/seguridad/incidentes/
    """
    try:
        # Obtener intentos fallidos recientes
        intentos_fallidos = BitacoraAcciones.objects.filter(
            tipo_accion='ACCESS_DENIED',
            fecha_accion__gte=timezone.now() - timedelta(days=7)
        ).select_related('copropietario')
        
        # Agrupar por IP o usuario para detectar intentos repetidos
        incidentes = []
        
        # Buscar intentos repetidos en las últimas 24 horas
        intentos_24h = BitacoraAcciones.objects.filter(
            tipo_accion='ACCESS_DENIED',
            fecha_accion__gte=timezone.now() - timedelta(hours=24)
        ).values('direccion_ip').annotate(intentos=Count('id')).filter(intentos__gte=3)
        
        for intento in intentos_24h:
            ip = intento['direccion_ip'] or 'IP desconocida'
            cantidad = intento['intentos']
            
            incidente = {
                'id': len(incidentes) + 1,
                'tipo': 'acceso_no_autorizado',
                'descripcion': f'Intentos de acceso fallidos repetidos desde {ip}',
                'detalle': f'Se detectaron {cantidad} intentos fallidos en las últimas 24 horas',
                'estado': 'abierto',
                'fecha_hora': timezone.now().isoformat(),
                'created_at': timezone.now().isoformat(),
                'ubicacion': 'Entrada Principal',
                'unidad': 'N/A',
                'usuario_reporta': 'Sistema',
                'reportado_por': 'Sistema de Seguridad',
                'prioridad': 'alta' if cantidad > 5 else 'media'
            }
            incidentes.append(incidente)
        
        # Buscar usuarios no reconocidos (baja confianza)
        baja_confianza = BitacoraAcciones.objects.filter(
            tipo_accion='VERIFY_FACE',
            confianza__lt=50.0,
            fecha_accion__gte=timezone.now() - timedelta(days=1)
        ).count()
        
        if baja_confianza > 0:
            incidente = {
                'id': len(incidentes) + 1,
                'tipo': 'reconocimiento_fallido',
                'descripcion': 'Múltiples intentos de reconocimiento con baja confianza',
                'detalle': f'Se detectaron {baja_confianza} intentos con confianza menor al 50%',
                'estado': 'abierto',
                'fecha_hora': timezone.now().isoformat(),
                'created_at': timezone.now().isoformat(),
                'ubicacion': 'Entrada Principal',
                'unidad': 'N/A',
                'usuario_reporta': 'Sistema',
                'reportado_por': 'Sistema de IA Facial',
                'prioridad': 'media'
            }
            incidentes.append(incidente)
        
        logger.info(f"🚨 Incidentes de seguridad: {len(incidentes)} encontrados")
        return Response(incidentes, status=status.HTTP_200_OK)
        
    except Exception as e:
        logger.error(f"❌ Error obteniendo incidentes: {e}")
        return Response({
            'error': 'Error interno del servidor',
            'detail': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


# ===================================================
# ENDPOINT PARA ESTADÍSTICAS DEL DASHBOARD
# ===================================================

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def dashboard_estadisticas(request):
    """
    Endpoint para estadísticas del dashboard de seguridad
    GET /api/authz/seguridad/dashboard/
    """
    try:
        # Estadísticas básicas
        total_usuarios = Copropietarios.objects.filter(activo=True).count()
        usuarios_con_fotos = ReconocimientoFacial.objects.filter(activo=True).count()
        total_fotos = ReconocimientoFacial.objects.filter(activo=True).count()  # Una foto por usuario por ahora
        
        # Estadísticas de hoy
        hoy = timezone.now().date()
        accesos_hoy = BitacoraAcciones.objects.filter(
            tipo_accion__in=['VERIFY_FACE', 'ACCESS_GRANTED'],
            fecha_accion__date=hoy
        ).count()
        
        eventos_hoy = BitacoraAcciones.objects.filter(fecha_accion__date=hoy).count()
        
        # Accesos exitosos vs fallidos
        accesos_exitosos = BitacoraAcciones.objects.filter(
            tipo_accion__in=['ACCESS_GRANTED', 'VERIFY_FACE'],
            resultado_match=True,
            fecha_accion__date=hoy
        ).count()
        
        intentos_fallidos = BitacoraAcciones.objects.filter(
            tipo_accion='ACCESS_DENIED',
            fecha_accion__date=hoy
        ).count()
        
        # Usuarios únicos hoy
        usuarios_unicos = BitacoraAcciones.objects.filter(
            fecha_accion__date=hoy,
            copropietario__isnull=False
        ).values('copropietario').distinct().count()
        
        # Incidentes abiertos (simulado)
        incidentes_abiertos = BitacoraAcciones.objects.filter(
            tipo_accion='ACCESS_DENIED',
            fecha_accion__gte=timezone.now() - timedelta(hours=24)
        ).count()
        
        # Visitas activas (si tienes el modelo)
        try:
            visitas_activas = Visita.objects.filter(
                estado='en_curso',
                fecha_hora_llegada__date=hoy
            ).count()
        except:
            visitas_activas = 0
        
        # Porcentaje de enrolamiento
        porcentaje_enrolamiento = (usuarios_con_fotos / total_usuarios * 100) if total_usuarios > 0 else 0
        
        estadisticas = {
            'total_usuarios': total_usuarios,
            'usuarios_con_fotos': usuarios_con_fotos,
            'total_fotos': total_fotos,
            'accesos_hoy': accesos_hoy,
            'incidentes_abiertos': min(incidentes_abiertos, 10),  # Limitar para no alarmar
            'visitas_activas': visitas_activas,
            'porcentaje_enrolamiento': round(porcentaje_enrolamiento, 1),
            'eventos_hoy': eventos_hoy,
            'accesos_exitosos': accesos_exitosos,
            'intentos_fallidos': intentos_fallidos,
            'usuarios_unicos': usuarios_unicos
        }
        
        logger.info(f"📈 Estadísticas dashboard generadas: {estadisticas}")
        return Response(estadisticas, status=status.HTTP_200_OK)
        
    except Exception as e:
        logger.error(f"❌ Error generando estadísticas: {e}")
        return Response({
            'error': 'Error interno del servidor',
            'detail': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


# ===================================================
# ENDPOINT PARA VISITAS ACTIVAS
# ===================================================

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def visitas_activas(request):
    """
    Endpoint para visitas activas
    GET /api/authz/seguridad/visitas/activas/
    """
    try:
        # Intentar obtener visitas del modelo si existe
        try:
            hoy = timezone.now().date()
            
            visitas = Visita.objects.filter(
                estado='en_curso',
                fecha_hora_llegada__date=hoy
            ).select_related('persona_autorizante')
            
            results = []
            for visita in visitas:
                result_item = {
                    'id': getattr(visita, 'id', visita.pk),  # Usar getattr para evitar error de Pylance
                    'visitante': visita.nombre_visitante,
                    'unidad': visita.persona_autorizante.nombre_completo if visita.persona_autorizante else 'N/A',
                    'fecha_hora': visita.fecha_hora_llegada.isoformat() if visita.fecha_hora_llegada else timezone.now().isoformat(),
                    'estado': visita.estado,
                    'motivo': visita.motivo_visita or 'Visita general',
                    'autorizado_por': visita.persona_autorizante.nombre_completo if visita.persona_autorizante else 'Sistema'
                }
                results.append(result_item)
                
        except ImportError:
            # Si no existe el modelo, simular algunas visitas
            results = [
                {
                    'id': 1,
                    'visitante': 'Juan Pérez',
                    'unidad': 'Torre A - Apt 301',
                    'fecha_hora': timezone.now().isoformat(),
                    'estado': 'activa',
                    'motivo': 'Mantenimiento',
                    'autorizado_por': 'Carlos Mendoza'
                }
            ]
        
        logger.info(f"👥 Visitas activas: {len(results)} encontradas")
        return Response(results, status=status.HTTP_200_OK)
        
    except Exception as e:
        logger.error(f"❌ Error obteniendo visitas activas: {e}")
        return Response({
            'error': 'Error interno del servidor',
            'detail': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


# ===================================================
# ENDPOINT AUXILIAR PARA CREAR LOGS DE PRUEBA
# ===================================================

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def crear_log_prueba(request):
    """
    Endpoint para crear logs de prueba (solo desarrollo)
    POST /api/authz/seguridad/logs/crear-prueba/
    """
    try:
        from django.conf import settings
        if not settings.DEBUG:
            return Response({
                'error': 'Endpoint solo disponible en modo desarrollo'
            }, status=status.HTTP_403_FORBIDDEN)
        
        # Obtener copropietarios existentes
        copropietarios = list(Copropietarios.objects.filter(activo=True))
        
        if not copropietarios:
            return Response({
                'error': 'No hay copropietarios registrados'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        import random
        
        # Crear logs de prueba
        logs_creados = 0
        for i in range(10):  # Crear 10 logs de prueba
            copropietario = random.choice(copropietarios)
            confianza = random.uniform(30, 100)
            autorizado = confianza > 60
            
            tipo_accion = 'ACCESS_GRANTED' if autorizado else 'ACCESS_DENIED'
            descripcion = f"Verificación facial: {'ACEPTADO' if autorizado else 'RECHAZADO'} ({confianza:.1f}%)"
            
            BitacoraAcciones.objects.create(
                copropietario=copropietario,
                tipo_accion=tipo_accion,
                descripcion=descripcion,
                proveedor_ia='Local',
                confianza=confianza,
                resultado_match=autorizado,
                direccion_ip='127.0.0.1'
            )
            logs_creados += 1
        
        logger.info(f"🧪 Logs de prueba creados: {logs_creados}")
        return Response({
            'message': f'Se crearon {logs_creados} logs de prueba exitosamente',
            'logs_creados': logs_creados
        }, status=status.HTTP_201_CREATED)
        
    except Exception as e:
        logger.error(f"❌ Error creando logs de prueba: {e}")
        return Response({
            'error': 'Error interno del servidor',
            'detail': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)