# seguridad/views_ai_training.py - Endpoints para entrenamiento de IA
from django.http import JsonResponse
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
import logging

from core.services.ai_training_service import AITrainingService
from .models import fn_bitacora_log

logger = logging.getLogger('ai_training')

# ===================================================
# ENDPOINTS PARA ENTRENAMIENTO DE IA
# ===================================================

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def entrenar_ia_automatico(request):
    """
    Entrena el modelo de IA automáticamente usando todos los datos disponibles
    POST /api/seguridad/ia/entrenar/
    """
    try:
        training_service = AITrainingService()
        resultado = training_service.entrenar_modelo_automatico()
        
        # Registrar en bitácora
        if resultado['success']:
            descripcion = f"Entrenamiento de IA completado - Precisión: {resultado['accuracy']:.2%}"
            tipo_accion = 'AI_TRAINING_SUCCESS'
        else:
            descripcion = f"Error en entrenamiento de IA: {resultado.get('error', 'Error desconocido')}"
            tipo_accion = 'AI_TRAINING_ERROR'
        
        fn_bitacora_log(
            tipo_accion=tipo_accion,
            descripcion=descripcion,
            usuario=request.user,
            direccion_ip=request.META.get('REMOTE_ADDR'),
            user_agent=request.META.get('HTTP_USER_AGENT')
        )
        
        logger.info(f"🧠 Entrenamiento solicitado por: {request.user.email}")
        
        if resultado['success']:
            return Response({
                'success': True,
                'message': 'Modelo de IA entrenado exitosamente',
                'data': resultado
            }, status=status.HTTP_200_OK)
        else:
            return Response({
                'success': False,
                'message': 'Error en el entrenamiento',
                'error': resultado['error']
            }, status=status.HTTP_400_BAD_REQUEST)
            
    except Exception as e:
        logger.error(f"❌ Error en endpoint de entrenamiento: {e}")
        return Response({
            'success': False,
            'message': 'Error interno del servidor',
            'error': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def re_entrenar_ia(request):
    """
    Re-entrena el modelo si hay nuevos datos disponibles
    POST /api/seguridad/ia/re-entrenar/
    """
    try:
        training_service = AITrainingService()
        resultado = training_service.re_entrenar_automatico()
        
        logger.info(f"🔄 Re-entrenamiento solicitado por: {request.user.email}")
        
        return Response({
            'success': True,
            'message': 'Re-entrenamiento completado',
            'data': resultado
        }, status=status.HTTP_200_OK)
        
    except Exception as e:
        logger.error(f"❌ Error en re-entrenamiento: {e}")
        return Response({
            'success': False,
            'message': 'Error en re-entrenamiento',
            'error': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def estadisticas_modelo_ia(request):
    """
    Obtiene estadísticas del modelo de IA actual
    GET /api/seguridad/ia/estadisticas/
    """
    try:
        training_service = AITrainingService()
        estadisticas = training_service.obtener_estadisticas_modelo()
        
        return Response({
            'success': True,
            'data': estadisticas
        }, status=status.HTTP_200_OK)
        
    except Exception as e:
        logger.error(f"❌ Error obteniendo estadísticas: {e}")
        return Response({
            'success': False,
            'message': 'Error obteniendo estadísticas',
            'error': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def probar_modelo_entrenado(request):
    """
    Prueba el modelo entrenado con una imagen
    POST /api/seguridad/ia/probar/
    """
    try:
        if 'imagen' not in request.FILES:
            return Response({
                'success': False,
                'message': 'No se encontró imagen en la petición'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        imagen = request.FILES['imagen']
        
        # Procesar imagen con face_recognition
        import face_recognition
        import numpy as np
        from PIL import Image
        import io
        
        # Cargar imagen
        imagen_pil = Image.open(io.BytesIO(imagen.read()))
        imagen_rgb = np.array(imagen_pil)
        
        # Extraer encoding facial
        encodings = face_recognition.face_encodings(imagen_rgb)
        
        if not encodings:
            return Response({
                'success': False,
                'message': 'No se detectó ningún rostro en la imagen'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Usar modelo entrenado para predecir
        training_service = AITrainingService()
        resultado_prediccion = training_service.predecir_con_modelo_entrenado(encodings[0])
        
        if not resultado_prediccion['success']:
            return Response({
                'success': False,
                'message': resultado_prediccion['error']
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Registrar prueba en bitácora
        descripcion = f"Prueba de modelo IA - {resultado_prediccion['persona_nombre']} ({resultado_prediccion['confidence']:.1f}%)"
        fn_bitacora_log(
            tipo_accion='AI_MODEL_TEST',
            descripcion=descripcion,
            usuario=request.user,
            confianza=resultado_prediccion['confidence'],
            resultado_match=resultado_prediccion['recognized']
        )
        
        logger.info(f"🧪 Prueba de modelo por: {request.user.email}")
        
        return Response({
            'success': True,
            'message': 'Predicción completada',
            'data': resultado_prediccion
        }, status=status.HTTP_200_OK)
        
    except Exception as e:
        logger.error(f"❌ Error probando modelo: {e}")
        return Response({
            'success': False,
            'message': 'Error probando modelo',
            'error': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def dashboard_entrenamiento_ia(request):
    """
    Dashboard con información completa del entrenamiento de IA
    GET /api/seguridad/ia/dashboard/
    """
    try:
        training_service = AITrainingService()
        estadisticas = training_service.obtener_estadisticas_modelo()
        
        # Estadísticas adicionales
        from seguridad.models import BitacoraAcciones, ReconocimientoFacial
        from django.utils import timezone
        from datetime import timedelta
        
        hoy = timezone.now().date()
        ayer = hoy - timedelta(days=1)
        
        # Conteos de entrenamientos
        entrenamientos_exitosos = BitacoraAcciones.objects.filter(
            tipo_accion='AI_TRAINING_SUCCESS',
            fecha_accion__date__gte=ayer
        ).count()
        
        entrenamientos_fallidos = BitacoraAcciones.objects.filter(
            tipo_accion='AI_TRAINING_ERROR',
            fecha_accion__date__gte=ayer
        ).count()
        
        # Pruebas del modelo
        pruebas_modelo = BitacoraAcciones.objects.filter(
            tipo_accion='AI_MODEL_TEST',
            fecha_accion__date=hoy
        ).count()
        
        dashboard_data = {
            **estadisticas,
            'training_stats': {
                'successful_trainings_24h': entrenamientos_exitosos,
                'failed_trainings_24h': entrenamientos_fallidos,
                'model_tests_today': pruebas_modelo,
                'total_face_recognitions': ReconocimientoFacial.objects.filter(activo=True).count()
            },
            'recommendations': []
        }
        
        # Generar recomendaciones
        if estadisticas.get('needs_retraining', False):
            dashboard_data['recommendations'].append({
                'type': 'warning',
                'message': 'Hay nuevos usuarios registrados. Se recomienda re-entrenar el modelo.',
                'action': 'retrain'
            })
        
        if estadisticas.get('accuracy', 0) < 0.8:
            dashboard_data['recommendations'].append({
                'type': 'info',
                'message': 'La precisión del modelo es baja. Considera agregar más fotos por persona.',
                'action': 'add_photos'
            })
        
        if not estadisticas.get('model_exists', False):
            dashboard_data['recommendations'].append({
                'type': 'error',
                'message': 'No hay modelo entrenado. Inicia el entrenamiento inicial.',
                'action': 'initial_train'
            })
        
        return Response({
            'success': True,
            'data': dashboard_data
        }, status=status.HTTP_200_OK)
        
    except Exception as e:
        logger.error(f"❌ Error en dashboard IA: {e}")
        return Response({
            'success': False,
            'message': 'Error obteniendo dashboard',
            'error': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)