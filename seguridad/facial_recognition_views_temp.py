# Vistas temporales para reconocimiento facial sin dependencia de face_recognition
from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.utils.decorators import method_decorator
from django.views import View
import json

# Importar el servicio temporal
from .facial_recognition_temp import FacialRecognitionService

@csrf_exempt
@require_http_methods(["POST"])
def reconocimiento_facial_simulado(request):
    """API para reconocimiento facial simulado"""
    try:
        data = json.loads(request.body)
        imagen_base64 = data.get('imagen')
        
        if not imagen_base64:
            return JsonResponse({
                'error': 'No se proporcionó imagen'
            }, status=400)
        
        # Procesar reconocimiento facial
        resultado = FacialRecognitionService.reconocimiento_facial_simulado(imagen_base64)
        
        return JsonResponse(resultado)
        
    except Exception as e:
        return JsonResponse({
            'error': f'Error procesando solicitud: {str(e)}'
        }, status=500)

@require_http_methods(["GET"])
def lista_usuarios_reconocimiento(request):
    """API para obtener lista de usuarios con reconocimiento facial activo"""
    try:
        usuarios = FacialRecognitionService.obtener_usuarios_activos()
        
        return JsonResponse({
            'usuarios': usuarios,
            'total': len(usuarios)
        })
        
    except Exception as e:
        return JsonResponse({
            'error': f'Error obteniendo usuarios: {str(e)}'
        }, status=500)

@require_http_methods(["GET"])
def buscar_usuarios_reconocimiento(request):
    """API para buscar usuarios"""
    try:
        termino = request.GET.get('q', '')
        usuarios = FacialRecognitionService.buscar_usuarios(termino)
        
        return JsonResponse({
            'usuarios': usuarios,
            'total': len(usuarios),
            'termino_busqueda': termino
        })
        
    except Exception as e:
        return JsonResponse({
            'error': f'Error buscando usuarios: {str(e)}'
        }, status=500)

@require_http_methods(["GET"])
def estadisticas_reconocimiento(request):
    """API para obtener estadísticas del sistema"""
    try:
        estadisticas = FacialRecognitionService.obtener_estadisticas()
        return JsonResponse(estadisticas)
        
    except Exception as e:
        return JsonResponse({
            'error': f'Error obteniendo estadísticas: {str(e)}'
        }, status=500)

def panel_guardia(request):
    """Vista principal del panel del guardia"""
    return render(request, 'guardia_panel.html', {
        'titulo': 'Panel del Guardia de Seguridad',
        'sistema': 'Reconocimiento Facial - Versión Demo'
    })