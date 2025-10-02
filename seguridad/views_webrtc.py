# seguridad/views_webrtc.py - Vistas WebRTC básicas
from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
import json
import logging

# Importar modelos y funciones para logging
from .models import Copropietarios, fn_bitacora_log

logger = logging.getLogger(__name__)

def webrtc_status(request):
    """Endpoint para verificar el estado del servidor WebRTC"""
    return JsonResponse({
        'status': 'ok',
        'server': 'Django WebRTC',
        'port': 8001,
        'message': '✅ Servidor Django WebRTC funcionando correctamente',
        'endpoints': {
            'status': '/webrtc/status/',
            'test': '/webrtc/test/',
        }
    })

@csrf_exempt
@require_http_methods(["GET", "POST"])
def webrtc_test(request):
    """Endpoint de prueba para el cliente"""
    if request.method == 'GET':
        return JsonResponse({
            'message': '🧪 Endpoint de prueba funcionando',
            'method': 'GET'
        })
    
    elif request.method == 'POST':
        try:
            data = json.loads(request.body)
            logger.info(f"📨 Datos recibidos: {data}")
            
            return JsonResponse({
                'status': 'success',
                'message': '📬 Datos recibidos correctamente',
                'received_data': data,
                'method': 'POST'
            })
        except json.JSONDecodeError:
            return JsonResponse({
                'status': 'error',
                'message': 'JSON inválido'
            }, status=400)
    
    # Return por defecto para métodos no manejados
    return JsonResponse({
        'status': 'error',
        'message': f'Método {request.method} no permitido'
    }, status=405)

def mobile_camera_interface(request):
    """Servir interfaz móvil para cámara del celular"""
    import os
    from django.conf import settings
    
    # Ruta al archivo HTML móvil
    mobile_file_path = os.path.join(settings.BASE_DIR, 'mobile_camera_interface.html')
    
    try:
        with open(mobile_file_path, 'r', encoding='utf-8') as file:
            html_content = file.read()
        return HttpResponse(html_content, content_type='text/html')
    except FileNotFoundError:
        return HttpResponse(
            '<h1>Error: Interfaz móvil no encontrada</h1><p>Archivo mobile_camera_interface.html no existe</p>', 
            content_type='text/html', 
            status=404
        )

@csrf_exempt  
def webrtc_face_recognition(request):
    """Endpoint para reconocimiento facial con IA real"""
    if request.method != 'POST':
        return JsonResponse({'error': 'Método no permitido'}, status=405)
    
    try:
        import numpy as np
        import cv2
        from PIL import Image
        import io
        import base64
        from .services.realtime_face_provider import OpenCVFaceProvider
        from .models import Copropietarios
        
        logger.info("📷 Frame recibido para reconocimiento facial")
        
        # Obtener la imagen del request
        image_data = None
        
        if 'frame' in request.FILES:
            # Si viene como archivo
            image_file = request.FILES['frame']
            image_data = image_file.read()
        elif request.body:
            # Si viene como JSON con base64
            try:
                json_data = json.loads(request.body)
                if 'image' in json_data:
                    # Decodificar base64
                    image_base64 = json_data['image'].split(',')[1] if ',' in json_data['image'] else json_data['image']
                    image_data = base64.b64decode(image_base64)
            except:
                pass
        
        if not image_data:
            return JsonResponse({
                'status': 'error',
                'message': 'No se recibió imagen válida'
            }, status=400)
        
        # Convertir bytes a imagen OpenCV
        nparr = np.frombuffer(image_data, np.uint8)
        frame = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        
        if frame is None:
            return JsonResponse({
                'status': 'error',
                'message': 'No se pudo decodificar la imagen'
            }, status=400)
        
        # Inicializar proveedor de reconocimiento
        provider = OpenCVFaceProvider()
        
        # Realizar reconocimiento facial
        logger.info("🔍 Iniciando reconocimiento facial...")
        result = provider.procesar_imagen(frame)
        
        if result and len(result) > 0:
            # Se encontraron rostros
            best_match = result[0]  # Tomar el mejor resultado
            confianza = best_match.get('confianza', 0.0)
            reconocido = best_match.get('reconocido', False)
            
            persona_reconocida = None
            copropietario_obj = None
            
            if 'persona_id' in best_match and best_match['persona_id']:
                try:
                    copropietario_obj = Copropietarios.objects.get(id=best_match['persona_id'])
                    persona_reconocida = {
                        'id': copropietario_obj.id,
                        'nombre': f"{copropietario_obj.nombres} {copropietario_obj.apellidos}",
                        'unidad': copropietario_obj.unidad_residencial,
                        'tipo': copropietario_obj.tipo_residente,
                        'documento': copropietario_obj.numero_documento,
                        'activo': copropietario_obj.activo
                    }
                except Copropietarios.DoesNotExist:
                    pass
            
            # Registrar en bitácora de acciones
            tipo_accion = 'ACCESS_GRANTED' if reconocido and confianza > 60 else 'ACCESS_DENIED'
            estado_texto = 'ACEPTADO' if reconocido and confianza > 60 else 'RECHAZADO'
            descripcion = f"Verificación facial: {estado_texto} ({confianza:.2f}%)"
            
            # Obtener IP del cliente
            client_ip = request.META.get('HTTP_X_FORWARDED_FOR')
            if client_ip:
                client_ip = client_ip.split(',')[0]
            else:
                client_ip = request.META.get('REMOTE_ADDR')
            
            fn_bitacora_log(
                tipo_accion=tipo_accion,
                descripcion=descripcion,
                usuario=request.user if request.user.is_authenticated else None,
                copropietario=copropietario_obj,
                direccion_ip=client_ip,
                user_agent=request.META.get('HTTP_USER_AGENT'),
                proveedor_ia='OpenCV',
                confianza=confianza,
                resultado_match=reconocido and confianza > 60
            )
            
            logger.info(f"✅ Verificación facial completada: {estado_texto} ({confianza:.2f}%)")
            
            return JsonResponse({
                'status': 'success',
                'message': 'Reconocimiento completado',
                'recognized': best_match.get('reconocido', False),
                'confidence': best_match.get('confianza', 0.0),
                'faces_detected': len(result),
                'person': persona_reconocida,
                'details': {
                    'tolerance_used': 0.4,  # Tu tolerancia optimizada
                    'provider': 'OpenCV',
                    'processing_time': best_match.get('tiempo_procesamiento', 0)
                },
                'timestamp': __import__('time').time()
            })
        else:
            # No se encontraron rostros o no se reconoció ninguno
            return JsonResponse({
                'status': 'success',
                'message': 'No se detectaron rostros reconocibles',
                'recognized': False,
                'confidence': 0.0,
                'faces_detected': 0,
                'person': None,
                'details': {
                    'tolerance_used': 0.4,
                    'provider': 'OpenCV',
                    'processing_time': 0
                },
                'timestamp': __import__('time').time()
            })
        
    except Exception as e:
        logger.error(f"❌ Error en reconocimiento facial: {e}")
        return JsonResponse({
            'status': 'error',
            'message': f'Error procesando imagen: {str(e)}',
            'timestamp': __import__('time').time()
        }, status=500)