# webrtc_enhanced_server.py - Servidor WebRTC mejorado para React
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Servidor WebRTC profesional optimizado para React Frontend
Compatible con el componente WebRTCFaceRecognition.tsx
"""

import socketio
import cv2
import numpy as np
import base64
import json
import logging
import asyncio
import time
from datetime import datetime
from typing import Dict, List, Optional, Any
from django.conf import settings
import django
import os
import sys

# Configurar Django
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from seguridad.models import ReconocimientoFacial, Copropietarios, fn_bitacora_log
from seguridad.services.realtime_face_provider import OpenCVFaceProvider, YOLOFaceProvider

# Configuración específica para React Frontend
CORS_ORIGINS = [
    "http://localhost:3000",    # Next.js dev
    "http://localhost:3001",    # Next.js alt
    "http://127.0.0.1:3000",
    "http://127.0.0.1:3001",
    "https://localhost:3000",
    "https://127.0.0.1:3000",
    "*"  # Para desarrollo - en producción quitar esto
]

FACE_CONFIG = {
    'MAX_FPS': 10,
    'DEFAULT_FPS': 5,
    'MAX_QUALITY': 1.0,
    'DEFAULT_QUALITY': 0.7,
    'SUPPORTED_FORMATS': ['image/jpeg', 'image/png'],
    'MAX_RESOLUTION': {'width': 1280, 'height': 720},
    'TIMEOUT_SECONDS': 30,
    'MAX_CONCURRENT_CLIENTS': 10
}

logger = logging.getLogger('webrtc_enhanced')

class EnhancedWebRTCServer:
    """Servidor WebRTC mejorado para React Frontend"""
    
    def __init__(self):
        # Crear servidor Socket.IO optimizado para React
        self.sio = socketio.AsyncServer(
            cors_allowed_origins=CORS_ORIGINS,
            logger=True,
            engineio_logger=True,
            async_mode='asgi',
            ping_timeout=60,
            ping_interval=25
        )
        
        # Estadísticas en tiempo real
        self.stats = {
            'connected_clients': 0,
            'total_frames_processed': 0,
            'successful_recognitions': 0,
            'failed_recognitions': 0,
            'average_processing_time': 0.0,
            'start_time': datetime.now(),
            'processing_times': []
        }
        
        # Proveedores de reconocimiento facial
        self.providers = {}
        self.current_provider = None
        self._init_providers()
        
        # Configurar event handlers
        self._setup_event_handlers()
        
        logger.info("🚀 Enhanced WebRTC Server iniciado")
    
    def _init_providers(self):
        """Inicializar proveedores de reconocimiento facial"""
        try:
            # OpenCV Provider (siempre disponible)
            self.providers['opencv'] = OpenCVFaceProvider()
            self.current_provider = self.providers['opencv']
            logger.info("✅ OpenCV Provider cargado")
            
            # YOLO Provider (si está disponible)
            try:
                self.providers['yolo'] = YOLOFaceProvider()
                logger.info("✅ YOLO Provider cargado")
            except Exception as e:
                logger.warning(f"⚠️ YOLO Provider no disponible: {e}")
                
        except Exception as e:
            logger.error(f"❌ Error inicializando proveedores: {e}")
    
    def _setup_event_handlers(self):
        """Configurar todos los event handlers para React"""
        
        @self.sio.event
        async def connect(sid, environ):
            """Cliente conectado"""
            self.stats['connected_clients'] += 1
            logger.info(f"🔗 Cliente conectado: {sid} (Total: {self.stats['connected_clients']})")
            
            # Enviar configuración inicial al cliente React
            await self.sio.emit('config', {
                'provider': self.current_provider.__class__.__name__ if self.current_provider else 'None',
                'max_fps': FACE_CONFIG['MAX_FPS'],
                'supported_formats': FACE_CONFIG['SUPPORTED_FORMATS'],
                'max_resolution': FACE_CONFIG['MAX_RESOLUTION']
            }, room=sid)
            
            # Enviar estadísticas actuales
            await self.sio.emit('stats', self.get_stats_dict(), room=sid)
        
        @self.sio.event
        async def disconnect(sid):
            """Cliente desconectado"""
            self.stats['connected_clients'] = max(0, self.stats['connected_clients'] - 1)
            logger.info(f"🔌 Cliente desconectado: {sid} (Total: {self.stats['connected_clients']})")
        
        @self.sio.event
        async def process_frame(sid, data):
            """Procesar frame enviado desde React"""
            start_time = time.time()
            
            try:
                # Validar datos requeridos por React
                if not isinstance(data, dict) or 'image' not in data:
                    await self.sio.emit('error', {
                        'message': 'Formato de datos inválido',
                        'code': 'INVALID_DATA'
                    }, room=sid)
                    return
                
                # Extraer información del frame
                image_data = data['image']
                frame_id = data.get('frame_id', 0)
                quality = data.get('quality', 0.7)
                timestamp = data.get('timestamp', time.time() * 1000)
                
                # Decodificar imagen base64
                if image_data.startswith('data:image'):
                    image_data = image_data.split(',')[1]
                
                image_bytes = base64.b64decode(image_data)
                nparr = np.frombuffer(image_bytes, np.uint8)
                frame = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
                
                if frame is None:
                    raise ValueError("No se pudo decodificar la imagen")
                
                # Procesar reconocimiento facial
                resultado = await self._process_recognition(frame, frame_id)
                
                # Calcular tiempo de procesamiento
                processing_time = (time.time() - start_time) * 1000
                resultado['processing_time'] = processing_time
                resultado['frame_id'] = frame_id
                resultado['timestamp'] = timestamp
                
                # Actualizar estadísticas
                self._update_stats(processing_time, resultado['reconocido'])
                
                # Enviar resultado a React
                await self.sio.emit('recognition_result', resultado, room=sid)
                
                # Broadcast estadísticas actualizadas
                await self.sio.emit('stats', self.get_stats_dict())
                
                logger.debug(f"📊 Frame {frame_id} procesado en {processing_time:.1f}ms")
                
            except Exception as e:
                logger.error(f"❌ Error procesando frame: {e}")
                await self.sio.emit('error', {
                    'message': f'Error procesando frame: {str(e)}',
                    'code': 'PROCESSING_ERROR',
                    'frame_id': data.get('frame_id', 0)
                }, room=sid)
        
        @self.sio.event
        async def get_stats(sid):
            """Obtener estadísticas actuales"""
            await self.sio.emit('stats', self.get_stats_dict(), room=sid)
        
        @self.sio.event
        async def reset_stats(sid):
            """Resetear estadísticas"""
            self.stats.update({
                'total_frames_processed': 0,
                'successful_recognitions': 0,
                'failed_recognitions': 0,
                'average_processing_time': 0.0,
                'start_time': datetime.now(),
                'processing_times': []
            })
            
            await self.sio.emit('stats', self.get_stats_dict(), room=sid)
            logger.info(f"📊 Estadísticas reseteadas por cliente: {sid}")
        
        @self.sio.event 
        async def change_provider(sid, data):
            """Cambiar proveedor de reconocimiento"""
            provider_name = data.get('provider', 'opencv').lower()
            
            if provider_name in self.providers:
                self.current_provider = self.providers[provider_name]
                await self.sio.emit('config', {
                    'provider': self.current_provider.__class__.__name__,
                    'max_fps': FACE_CONFIG['MAX_FPS'],
                    'supported_formats': FACE_CONFIG['SUPPORTED_FORMATS'],
                    'max_resolution': FACE_CONFIG['MAX_RESOLUTION']
                }, room=sid)
                logger.info(f"🔄 Proveedor cambiado a: {provider_name}")
            else:
                await self.sio.emit('error', {
                    'message': f'Proveedor no disponible: {provider_name}',
                    'code': 'PROVIDER_NOT_AVAILABLE'
                }, room=sid)
    
    async def _process_recognition(self, frame: np.ndarray, frame_id: int) -> Dict[str, Any]:
        """Procesar reconocimiento facial optimizado para React"""
        try:
            if not self.current_provider:
                return {
                    'reconocido': False,
                    'error': 'No hay proveedor disponible',
                    'proveedor': 'None'
                }
            
            # Procesar imagen con el proveedor actual
            if hasattr(self.current_provider, 'procesar_imagen_multiple'):
                resultados = self.current_provider.procesar_imagen_multiple(
                    [frame], 
                    umbrales=[0.5]  # Umbral más permisivo para reconocimiento rápido
                )
            else:
                # Fallback para proveedores más simples
                resultados = [self.current_provider.procesar_imagen(frame)]
            
            if not resultados or not resultados[0]:
                return {
                    'reconocido': False,
                    'mensaje': 'No se detectaron rostros',
                    'proveedor': self.current_provider.__class__.__name__
                }
            
            resultado = resultados[0]
            
            if resultado.get('reconocido', False) and resultado.get('persona'):
                # Formatear resultado exitoso para React
                persona_data = resultado['persona']
                
                # Obtener información completa de la persona
                try:
                    copropietario = Copropietarios.objects.get(numero_documento=persona_data.get('documento', ''))
                    vivienda = copropietario.unidad_residencial if copropietario.unidad_residencial else None
                    tipo_residente = copropietario.tipo_residente or 'Propietario'
                except Copropietarios.DoesNotExist:
                    vivienda = None
                    tipo_residente = 'Desconocido'
                
                # Registrar en bitácora
                fn_bitacora_log(
                    f"Reconocimiento exitoso: {persona_data['nombre']} (Frame #{frame_id})",
                    'WEBRTC_SUCCESS'
                )
                
                return {
                    'reconocido': True,
                    'persona': {
                        'id': persona_data['id'],
                        'nombre': persona_data['nombre'],
                        'vivienda': vivienda,
                        'tipo_residente': tipo_residente
                    },
                    'confianza': resultado.get('confianza', 0.0),
                    'proveedor': self.current_provider.__class__.__name__
                }
            
            else:
                # Persona no reconocida
                fn_bitacora_log(
                    f"Reconocimiento fallido (Frame #{frame_id})",
                    'WEBRTC_FAILED'
                )
                
                return {
                    'reconocido': False,
                    'mensaje': 'Persona no reconocida en el sistema',
                    'proveedor': self.current_provider.__class__.__name__
                }
                
        except Exception as e:
            logger.error(f"❌ Error en reconocimiento: {e}")
            return {
                'reconocido': False,
                'error': f'Error interno: {str(e)}',
                'proveedor': self.current_provider.__class__.__name__ if self.current_provider else 'None'
            }
    
    def _update_stats(self, processing_time: float, success: bool):
        """Actualizar estadísticas en tiempo real"""
        self.stats['total_frames_processed'] += 1
        
        if success:
            self.stats['successful_recognitions'] += 1
        else:
            self.stats['failed_recognitions'] += 1
        
        # Mantener historial de tiempos (máximo 100 entradas)
        self.stats['processing_times'].append(processing_time)
        if len(self.stats['processing_times']) > 100:
            self.stats['processing_times'].pop(0)
        
        # Calcular tiempo promedio
        if self.stats['processing_times']:
            self.stats['average_processing_time'] = (
                sum(self.stats['processing_times']) / len(self.stats['processing_times'])
            ) / 1000  # Convertir a segundos para compatibilidad
    
    def get_stats_dict(self) -> Dict[str, Any]:
        """Obtener diccionario de estadísticas para React"""
        return {
            'connected_clients': self.stats['connected_clients'],
            'total_frames_processed': self.stats['total_frames_processed'],
            'successful_recognitions': self.stats['successful_recognitions'],
            'failed_recognitions': self.stats['failed_recognitions'],
            'average_processing_time': self.stats['average_processing_time'],
            'uptime_seconds': (datetime.now() - self.stats['start_time']).total_seconds(),
            'current_provider': self.current_provider.__class__.__name__ if self.current_provider else 'None',
            'available_providers': list(self.providers.keys())
        }
    
    def get_asgi_app(self):
        """Obtener aplicación ASGI para uvicorn"""
        import socketio.asgi
        return socketio.ASGIApp(self.sio, static_files={
            '/': {'content_type': 'text/html', 'filename': 'index.html'}
        })

# Instancia global del servidor
server = EnhancedWebRTCServer()
app = server.get_asgi_app()

if __name__ == "__main__":
    import uvicorn
    
    logger.info("🚀 Iniciando Enhanced WebRTC Server para React...")
    logger.info(f"📡 CORS habilitado para: {CORS_ORIGINS}")
    logger.info(f"⚙️ Configuración: {FACE_CONFIG}")
    
    uvicorn.run(
        "webrtc_enhanced_server:app",
        host="0.0.0.0",
        port=8001,
        reload=True,
        log_level="info"
    )