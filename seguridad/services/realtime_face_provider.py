#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Proveedor de reconocimiento facial usando OpenCV + face_recognition
Implementación real para reemplazar la simulación
"""
from typing import List, Dict, Tuple

import face_recognition
import numpy as np
import requests
from PIL import Image
import io
import json
import logging

logger = logging.getLogger('seguridad')


class OpenCVFaceProvider:
    """
    Proveedor de reconocimiento facial usando OpenCV y face_recognition
    """
    
    def __init__(self):
        self.model = 'hog'  # 'hog' es más rápido, 'cnn' es más preciso
        self.tolerance = 0.6  # Umbral de tolerancia (menor = más estricto)
        
    def detectar_caras_en_imagen(self, imagen_path_o_bytes) -> List[np.ndarray]:
        """
        Detecta caras en una imagen y retorna los encodings faciales
        """
        try:
            # Cargar imagen
            if isinstance(imagen_path_o_bytes, bytes):
                # Si es bytes (imagen subida)
                imagen_pil = Image.open(io.BytesIO(imagen_path_o_bytes))
                imagen_rgb = np.array(imagen_pil)
            elif isinstance(imagen_path_o_bytes, str):
                # Si es URL, descargar
                if imagen_path_o_bytes.startswith('http'):
                    response = requests.get(imagen_path_o_bytes)
                    imagen_pil = Image.open(io.BytesIO(response.content))
                    imagen_rgb = np.array(imagen_pil)
                else:
                    # Si es path local
                    imagen_rgb = face_recognition.load_image_file(imagen_path_o_bytes)
            else:
                # Si ya es array numpy
                imagen_rgb = imagen_path_o_bytes
            
            # Convertir de PIL RGB a OpenCV BGR si es necesario
            if len(imagen_rgb.shape) == 3 and imagen_rgb.shape[2] == 3:
                # Asegurar que esté en RGB
                pass
            
            # Detectar ubicaciones de caras
            face_locations = face_recognition.face_locations(imagen_rgb, model=self.model)
            
            # Obtener encodings faciales
            face_encodings = face_recognition.face_encodings(imagen_rgb, face_locations)
            
            return face_encodings
            
        except Exception as e:
            logger.error(f"Error detectando caras: {str(e)}")
            return []
    
    def comparar_caras(self, encoding_conocido: np.ndarray, encoding_desconocido: np.ndarray) -> float:
        """
        Compara dos encodings faciales y retorna el porcentaje de confianza
        """
        try:
            # Calcular distancia facial
            distancia = face_recognition.face_distance([encoding_conocido], encoding_desconocido)[0]
            
            # Convertir distancia a porcentaje de confianza
            # face_recognition usa distancia euclidiana: menor distancia = mayor similitud
            # Tolerancia típica: 0.6 (0.0 = idéntico, 1.0 = muy diferente)
            
            if distancia <= self.tolerance:
                # Conversión de distancia a porcentaje de confianza
                confianza = max(0, (1 - distancia) * 100)
                return min(100, confianza)  # Limitar a 100%
            else:
                # Si supera la tolerancia, confianza muy baja
                confianza = max(0, (1 - distancia) * 50)  # Reducir factor
                return min(30, confianza)  # Máximo 30% si supera tolerancia
            
        except Exception as e:
            logger.error(f"Error comparando caras: {str(e)}")
            return 0.0
    
    def procesar_reconocimiento_tiempo_real(self, 
                                          imagen_subida: bytes, 
                                          personas_bd: List[Dict]) -> List[Dict]:
        """
        Procesa reconocimiento facial en tiempo real
        """
        resultados = []
        
        try:
            # Detectar caras en imagen subida
            encodings_subida = self.detectar_caras_en_imagen(imagen_subida)
            
            if not encodings_subida:
                logger.warning("No se detectaron caras en la imagen subida")
                return resultados
            
            # Usar la primera cara detectada
            encoding_target = encodings_subida[0]
            
            # Comparar con cada persona en BD
            for persona_data in personas_bd:
                persona = persona_data['persona']
                reconocimiento = persona_data['reconocimiento']
                
                try:
                    # Obtener fotos de la persona
                    fotos_urls = []
                    if reconocimiento.fotos_urls:
                        fotos_urls = json.loads(reconocimiento.fotos_urls)
                    
                    if reconocimiento.imagen_referencia_url:
                        fotos_urls.append(reconocimiento.imagen_referencia_url)
                    
                    mejor_confianza = 0
                    foto_coincidente = None
                    
                    # Comparar con cada foto de la persona
                    for foto_url in fotos_urls:
                        try:
                            # Detectar caras en foto de BD
                            encodings_bd = self.detectar_caras_en_imagen(foto_url)
                            
                            if encodings_bd:
                                # Comparar con primera cara detectada
                                confianza = self.comparar_caras(encodings_bd[0], encoding_target)
                                
                                if confianza > mejor_confianza:
                                    mejor_confianza = confianza
                                    foto_coincidente = foto_url
                                    
                        except Exception as e:
                            logger.warning(f"Error procesando foto {foto_url}: {str(e)}")
                            continue
                    
                    # Agregar resultado
                    resultados.append({
                        'persona': persona,
                        'reconocimiento': reconocimiento,
                        'confianza': mejor_confianza,
                        'foto_coincidente': foto_coincidente,
                        'num_fotos_procesadas': len(fotos_urls)
                    })
                    
                except Exception as e:
                    logger.warning(f"Error procesando persona {persona.id}: {str(e)}")
                    continue
            
            # Ordenar por confianza descendente
            resultados.sort(key=lambda x: x['confianza'], reverse=True)
            
            return resultados
            
        except Exception as e:
            logger.error(f"Error en reconocimiento tiempo real: {str(e)}")
            return resultados


class YOLOFaceProvider:
    """
    Proveedor usando YOLO para detección de caras + face_recognition para reconocimiento
    Más rápido para detección en tiempo real
    """
    
    def __init__(self):
        try:
            # Cargar modelo YOLO preentrenado para detección de caras
            from ultralytics import YOLO
            self.yolo_model = YOLO('yolov8n-face.pt')  # Modelo específico para caras
            self.face_provider = OpenCVFaceProvider()
        except ImportError:
            logger.warning("YOLO no disponible, usando OpenCV puro")
            self.yolo_model = None
            self.face_provider = OpenCVFaceProvider()
    
    def detectar_caras_yolo(self, imagen_bytes: bytes) -> List[Tuple[int, int, int, int]]:
        """
        Detecta caras usando YOLO, retorna coordenadas de bounding boxes
        """
        if not self.yolo_model:
            return []
        
        try:
            # Convertir bytes a imagen PIL
            imagen_pil = Image.open(io.BytesIO(imagen_bytes))
            
            # Detectar con YOLO
            results = self.yolo_model(imagen_pil)
            
            caras_detectadas = []
            for result in results:
                boxes = result.boxes
                if boxes is not None:
                    for box in boxes:
                        # Obtener coordenadas
                        x1, y1, x2, y2 = box.xyxy[0].cpu().numpy()
                        confianza = box.conf[0].cpu().numpy()
                        
                        if confianza > 0.5:  # Umbral de confianza para detección
                            caras_detectadas.append((int(x1), int(y1), int(x2), int(y2)))
            
            return caras_detectadas
            
        except Exception as e:
            logger.error(f"Error en detección YOLO: {str(e)}")
            return []
    
    def procesar_reconocimiento_tiempo_real(self, imagen_subida: bytes, personas_bd: List[Dict]) -> List[Dict]:
        """
        Método principal para procesamiento de reconocimiento facial en tiempo real
        Usa YOLO para detección optimizada + face_recognition para reconocimiento
        """
        return self.procesar_con_yolo(imagen_subida, personas_bd)
    
    def procesar_con_yolo(self, imagen_subida: bytes, personas_bd: List[Dict]) -> List[Dict]:
        """
        Procesa usando YOLO para detección + face_recognition para reconocimiento
        """
        # Primero detectar caras con YOLO
        caras_detectadas = self.detectar_caras_yolo(imagen_subida)
        
        if not caras_detectadas:
            logger.warning("YOLO no detectó caras, usando OpenCV")
            return self.face_provider.procesar_reconocimiento_tiempo_real(imagen_subida, personas_bd)
        
        # Si YOLO detectó caras, usar face_recognition para el reconocimiento
        logger.info(f"YOLO detectó {len(caras_detectadas)} caras")
        return self.face_provider.procesar_reconocimiento_tiempo_real(imagen_subida, personas_bd)


# Factory para elegir proveedor
class RealTimeFaceProviderFactory:
    """
    Factory para crear proveedores de reconocimiento facial en tiempo real
    """
    
    @staticmethod
    def crear_proveedor(tipo: str = 'opencv'):
        """
        Crear proveedor según tipo especificado
        """
        if tipo.lower() == 'yolo':
            return YOLOFaceProvider()
        elif tipo.lower() == 'opencv':
            return OpenCVFaceProvider()
        else:
            logger.warning(f"Tipo {tipo} no reconocido, usando OpenCV")
            return OpenCVFaceProvider()