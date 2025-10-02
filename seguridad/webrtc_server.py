#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Servidor WebRTC profesional para reconocimiento facial en tiempo real
Usa Socket.IO para comunicación bidireccional y procesamiento en streaming
"""

import socketio
import cv2
import numpy as np
import base64
import json
import logging
from typing import Dict, List, Optional
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

# Importar configuración WebRTC
try:
    from settings_webrtc import (
        WEBRTC_CORS_ORIGINS, 
        FACE_RECOGNITION_SETTINGS, 
        FACE_PROVIDERS_CONFIG,
        WEBRTC_STATS
    )
except ImportError:
    # Configuración por defecto si no existe el archivo
    WEBRTC_CORS_ORIGINS = ["http://localhost:3000", "http://127.0.0.1:3000"]
    FACE_RECOGNITION_SETTINGS = {
        'MAX_FPS': 10, 
        'DEFAULT_FPS': 5,
        'MAX_QUALITY': 1.0,
        'DEFAULT_QUALITY': 0.7,
        'SUPPORTED_FORMATS': ['image/jpeg', 'image/png'],
        'MAX_RESOLUTION': {'width': 1280, 'height': 720}
    }
    FACE_PROVIDERS_CONFIG = {'opencv': {'enabled': True}}
    WEBRTC_STATS = {'enable_real_time_stats': True}

logger = logging.getLogger('seguridad_webrtc')

class WebRTCFaceRecognitionServer:
    """
    Servidor profesional de reconocimiento facial con WebRTC
    """
    
    def __init__(self):
        # Crear servidor Socket.IO con CORS
        self.sio = socketio.AsyncServer(
            cors_allowed_origins="*",
            async_mode='asgi',
            logger=True,
            engineio_logger=True
        )
        
        # Configurar proveedores de IA
        self.opencv_provider = OpenCVFaceProvider()
        try:
            self.yolo_provider = YOLOFaceProvider()
            self.use_yolo = True
            logger.info("✅ YOLO provider cargado exitosamente")
        except Exception as e:
            self.yolo_provider = None
            self.use_yolo = False
            logger.warning(f"⚠️ YOLO no disponible, usando OpenCV puro: {str(e)}")
        
        # Cache de personas en BD para optimizar rendimiento
        self.personas_cache = {}
        self.cache_timestamp = 0
        self.cache_duration = 300  # 5 minutos
        
        # Estadísticas en tiempo real
        self.stats = {
            'connected_clients': 0,
            'total_frames_processed': 0,
            'successful_recognitions': 0,
            'failed_recognitions': 0,
            'average_processing_time': 0.0
        }
        
        # Configurar event handlers
        self.setup_event_handlers()
    
    def setup_event_handlers(self):
        """Configurar manejadores de eventos Socket.IO"""
        
        @self.sio.event
        async def connect(sid, environ, auth):
            """Cliente conectado"""
            self.stats['connected_clients'] += 1
            logger.info(f"🔗 Cliente conectado: {sid} (Total: {self.stats['connected_clients']})")
            
            # Enviar configuración inicial
            await self.sio.emit('config', {
                'provider': 'YOLO + OpenCV' if self.use_yolo else 'OpenCV',
                'max_fps': 10,  # Máximo 10 FPS para no sobrecargar
                'supported_formats': ['jpeg', 'png', 'webp'],
                'max_resolution': {'width': 1280, 'height': 720}
            }, room=sid)
            
            # Enviar estadísticas iniciales
            await self.sio.emit('stats', self.stats, room=sid)
        
        @self.sio.event
        async def disconnect(sid):
            """Cliente desconectado"""
            self.stats['connected_clients'] = max(0, self.stats['connected_clients'] - 1)
            logger.info(f"❌ Cliente desconectado: {sid} (Total: {self.stats['connected_clients']})")
        
        @self.sio.event
        async def process_frame(sid, data):
            """Procesar frame de video en tiempo real"""
            try:
                import time
                start_time = time.time()
                
                # Validar datos recibidos
                if not isinstance(data, dict) or 'image' not in data:
                    await self.sio.emit('error', {
                        'message': 'Formato de datos inválido',
                        'code': 'INVALID_DATA'
                    }, room=sid)
                    return
                
                # Decodificar imagen base64
                image_data = data['image']
                if image_data.startswith('data:image'):
                    # Remover prefijo data:image/jpeg;base64,
                    image_data = image_data.split(',')[1]
                
                # Convertir a bytes
                image_bytes = base64.b64decode(image_data)
                
                # Procesar con IA
                resultado = await self.process_face_recognition(image_bytes, sid)
                
                # Calcular tiempo de procesamiento
                processing_time = time.time() - start_time
                self.stats['total_frames_processed'] += 1
                
                # Actualizar promedio de tiempo de procesamiento
                current_avg = self.stats['average_processing_time']
                total_frames = self.stats['total_frames_processed']
                self.stats['average_processing_time'] = (
                    (current_avg * (total_frames - 1) + processing_time) / total_frames
                )
                
                # Enviar resultado
                await self.sio.emit('recognition_result', {
                    **resultado,
                    'processing_time': round(processing_time * 1000, 2),  # En millisegundos
                    'frame_id': data.get('frame_id', 0),
                    'timestamp': time.time()
                }, room=sid)
                
                # Enviar estadísticas actualizadas cada 10 frames
                if self.stats['total_frames_processed'] % 10 == 0:
                    await self.sio.emit('stats', self.stats, room=sid)
                
            except Exception as e:
                logger.error(f"Error procesando frame: {str(e)}")
                await self.sio.emit('error', {
                    'message': f'Error procesando frame: {str(e)}',
                    'code': 'PROCESSING_ERROR'
                }, room=sid)
        
        @self.sio.event
        async def get_stats(sid):
            """Obtener estadísticas actuales"""
            await self.sio.emit('stats', self.stats, room=sid)
        
        @self.sio.event
        async def reset_stats(sid):
            """Resetear estadísticas (solo para admin)"""
            self.stats.update({
                'total_frames_processed': 0,
                'successful_recognitions': 0,
                'failed_recognitions': 0,
                'average_processing_time': 0.0
            })
            await self.sio.emit('stats', self.stats, room=sid)
            logger.info(f"📊 Estadísticas reseteadas por cliente: {sid}")
    
    async def process_face_recognition(self, image_bytes: bytes, client_id: str) -> Dict:
        """
        Procesar reconocimiento facial con la imagen recibida
        """
        try:
            # Actualizar cache de personas si es necesario
            await self.update_personas_cache()
            
            # Seleccionar proveedor según configuración
            if self.use_yolo and self.yolo_provider:
                provider = self.yolo_provider
                provider_name = "YOLO + OpenCV"
            else:
                provider = self.opencv_provider
                provider_name = "OpenCV"
            
            # Procesar reconocimiento
            resultados = provider.procesar_reconocimiento_tiempo_real(
                image_bytes, 
                list(self.personas_cache.values())
            )
            
            if resultados and len(resultados) > 0:
                # Reconocimiento exitoso
                resultado = resultados[0]
                persona = resultado['persona']
                confianza = resultado['confianza']
                
                self.stats['successful_recognitions'] += 1
                
                # Registrar en bitácora (de forma asíncrona)
                self.log_recognition_async(
                    persona=persona,
                    confianza=confianza,
                    client_id=client_id,
                    provider_name=provider_name,
                    success=True
                )
                
                return {
                    'reconocido': True,
                    'persona': {
                        'id': persona.id,
                        'nombre': f"{persona.nombres} {persona.apellidos}",
                        'vivienda': persona.unidad_residencial,
                        'tipo_residente': persona.tipo_residente,
                        'documento': persona.numero_documento
                    },
                    'confianza': round(confianza, 3),
                    'proveedor': provider_name,
                    'threshold_usado': provider.tolerance if hasattr(provider, 'tolerance') else 0.6
                }
            
            else:
                # No se reconoció a nadie
                self.stats['failed_recognitions'] += 1
                
                self.log_recognition_async(
                    persona=None,
                    confianza=0.0,
                    client_id=client_id,
                    provider_name=provider_name,
                    success=False
                )
                
                return {
                    'reconocido': False,
                    'persona': None,
                    'confianza': 0.0,
                    'proveedor': provider_name,
                    'mensaje': 'Persona no identificada en el sistema'
                }
        
        except Exception as e:
            logger.error(f"Error en reconocimiento facial: {str(e)}")
            self.stats['failed_recognitions'] += 1
            
            return {
                'reconocido': False,
                'persona': None,
                'confianza': 0.0,
                'error': str(e),
                'proveedor': 'Error'
            }
    
    async def update_personas_cache(self):
        """
        Actualizar cache de personas con reconocimiento facial
        """
        import time
        current_time = time.time()
        
        # Solo actualizar si han pasado más de 5 minutos
        if current_time - self.cache_timestamp < self.cache_duration:
            return
        
        try:
            # Obtener todas las personas con reconocimiento activo
            reconocimientos = ReconocimientoFacial.objects.filter(
                activo=True
            ).select_related('copropietario')
            
            new_cache = {}
            for reconocimiento in reconocimientos:
                persona_id = reconocimiento.copropietario.id
                new_cache[persona_id] = {
                    'persona': reconocimiento.copropietario,
                    'reconocimiento': reconocimiento
                }
            
            self.personas_cache = new_cache
            self.cache_timestamp = current_time
            
            logger.info(f"🔄 Cache actualizado: {len(new_cache)} personas con reconocimiento")
            
        except Exception as e:
            logger.error(f"Error actualizando cache de personas: {str(e)}")
    
    def log_recognition_async(self, persona, confianza, client_id, provider_name, success):
        """
        Registrar reconocimiento en bitácora de forma asíncrona
        """
        try:
            descripcion = (
                f'Reconocimiento WebRTC {"exitoso" if success else "fallido"} '
                f'(Cliente: {client_id[:8]}..., Proveedor: {provider_name})'
            )
            
            if persona:
                descripcion += f' - Persona: {persona.nombres} {persona.apellidos}'
            
            fn_bitacora_log(
                tipo_accion='RECONOCIMIENTO_WEBRTC',
                descripcion=descripcion,
                usuario=None,  # Usuario anónimo para WebRTC
                copropietario=persona,
                direccion_ip='WebRTC_Client',
                user_agent=f'WebRTC_Client_{client_id[:8]}',
                proveedor_ia=provider_name,
                confianza=confianza,
                resultado_match=success
            )
        except Exception as e:
            logger.error(f"Error registrando en bitácora: {str(e)}")

# Instancia global del servidor
webrtc_server = WebRTCFaceRecognitionServer()

# Aplicación ASGI para integrar con Django
app = socketio.ASGIApp(webrtc_server.sio, other_asgi_app=None)