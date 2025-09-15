"""
Local Face Recognition Provider

Implementación del proveedor de reconocimiento facial local usando face_recognition library
"""

import io
import base64
import logging
import numpy as np
from typing import Dict, Any, Optional
from django.conf import settings
from PIL import Image

# Intentar importar face_recognition, si no está disponible usar fallback
try:
    import face_recognition
    import cv2
    FACE_RECOGNITION_AVAILABLE = True
except ImportError:
    FACE_RECOGNITION_AVAILABLE = False
    face_recognition = None
    cv2 = None

from .face_provider import (
    FaceRecognitionProvider, 
    FaceDetectionError, 
    FaceVerificationError, 
    FaceEnrollmentError
)

logger = logging.getLogger('seguridad')


class LocalFaceProvider(FaceRecognitionProvider):
    """
    Proveedor de reconocimiento facial local usando face_recognition library
    """
    
    def __init__(self):
        """Inicializa el proveedor local"""
        self.threshold = getattr(settings, 'FACE_LOCAL_THRESHOLD', 0.6)
        
        # Verificar si face_recognition está disponible
        if not FACE_RECOGNITION_AVAILABLE:
            logger.warning("face_recognition library no está disponible. Usando modo simulado.")
        else:
            logger.info(f"Local Face Provider inicializado con umbral: {self.threshold}")
    
    def detect_face(self, image_bytes: bytes) -> Optional[str]:
        """
        Detecta un rostro en la imagen y genera un encoding
        
        Args:
            image_bytes: Bytes de la imagen
            
        Returns:
            str: Vector facial encodificado en base64 o None si no se detecta rostro
            
        Raises:
            FaceDetectionError: Si hay error en la detección
        """
        # Si face_recognition no está disponible, simular detección exitosa
        if not FACE_RECOGNITION_AVAILABLE:
            return self._simulate_face_detection(image_bytes)
            
        try:
            # Cargar imagen
            image_array = self._bytes_to_rgb_array(image_bytes)
            
            # Detectar ubicaciones de rostros
            face_locations = face_recognition.face_locations(image_array)
            
            if not face_locations:
                logger.warning("No se detectaron rostros en la imagen")
                return None
            
            if len(face_locations) > 1:
                logger.warning(f"Se detectaron {len(face_locations)} rostros, usando el primero")
            
            # Generar encoding del primer rostro
            face_encodings = face_recognition.face_encodings(
                image_array, 
                face_locations[:1]  # Solo el primer rostro
            )
            
            if not face_encodings:
                logger.warning("No se pudo generar encoding del rostro detectado")
                return None
            
            # Convertir encoding a base64
            encoding_bytes = face_encodings[0].tobytes()
            encoding_b64 = base64.b64encode(encoding_bytes).decode('utf-8')
            
            logger.info("Rostro detectado y encoding generado exitosamente")
            
            return encoding_b64
            
        except Exception as e:
            logger.error(f"Error en detección local: {str(e)}")
            raise FaceDetectionError(f"Error en detección local: {str(e)}")
    
    def verify_faces(self, face_ref: str, image_bytes: bytes) -> Dict[str, Any]:
        """
        Verifica dos rostros comparando sus encodings
        
        Args:
            face_ref: Vector facial de referencia en base64
            image_bytes: Bytes de la imagen a verificar
            
        Returns:
            Dict con resultado de verificación
            
        Raises:
            FaceVerificationError: Si hay error en la verificación
        """
        # Si face_recognition no está disponible, simular verificación
        if not FACE_RECOGNITION_AVAILABLE:
            return self._simulate_face_verification(face_ref, image_bytes)
            
        try:
            # Generar encoding de la imagen de prueba
            probe_encoding_b64 = self.detect_face(image_bytes)
            
            if not probe_encoding_b64:
                return {
                    "isIdentical": False,
                    "confidence": 0.0,
                    "provider": self.provider_name,
                    "threshold": self.threshold,
                    "error": "No se detectó rostro en imagen de verificación"
                }
            
            # Comparar encodings
            distance = self._compare_encodings(face_ref, probe_encoding_b64)
            
            # Convertir distancia a confianza (1 - distancia)
            confidence = max(0.0, 1.0 - distance)
            is_match = distance <= self.threshold
            
            result = {
                "isIdentical": is_match,
                "confidence": float(confidence),
                "provider": self.provider_name,
                "threshold": self.threshold,
                "distance": float(distance)
            }
            
            logger.info(
                f"Verificación local: match={is_match}, "
                f"confidence={confidence:.3f}, distance={distance:.3f}"
            )
            
            return result
            
        except Exception as e:
            logger.error(f"Error en verificación local: {str(e)}")
            raise FaceVerificationError(f"Error en verificación local: {str(e)}")
    
    def enroll_face(self, image_bytes: bytes) -> Dict[str, Any]:
        """
        Enrola un rostro generando su encoding
        
        Args:
            image_bytes: Bytes de la imagen de referencia
            
        Returns:
            Dict con datos del enrolamiento
            
        Raises:
            FaceEnrollmentError: Si hay error en el enrolamiento
        """
        try:
            # Generar encoding
            encoding_b64 = self.detect_face(image_bytes)
            
            if not encoding_b64:
                raise FaceEnrollmentError("No se detectó rostro en imagen de enrolamiento")
            
            # Calcular métricas de calidad de la imagen
            quality_score = self._calculate_image_quality(image_bytes)
            
            result = {
                "face_reference": encoding_b64,
                "provider": self.provider_name,
                "confidence": quality_score,
                "threshold": self.threshold
            }
            
            logger.info(f"Enrolamiento local exitoso, calidad: {quality_score:.3f}")
            
            return result
            
        except FaceDetectionError:
            raise FaceEnrollmentError("No se detectó rostro en imagen de enrolamiento")
        except Exception as e:
            logger.error(f"Error en enrolamiento local: {str(e)}")
            raise FaceEnrollmentError(f"Error en enrolamiento local: {str(e)}")
    
    @property
    def provider_name(self) -> str:
        """Retorna el nombre del proveedor"""
        return "Local"
    
    def _bytes_to_rgb_array(self, image_bytes: bytes) -> np.ndarray:
        """
        Convierte bytes de imagen a array RGB
        
        Args:
            image_bytes: Bytes de la imagen
            
        Returns:
            np.ndarray: Array RGB de la imagen
            
        Raises:
            FaceDetectionError: Si no se puede cargar la imagen
        """
        try:
            # Abrir imagen con PIL
            image_pil = Image.open(io.BytesIO(image_bytes))
            
            # Convertir a RGB si es necesario
            if image_pil.mode != 'RGB':
                image_pil = image_pil.convert('RGB')
            
            # Convertir a array numpy
            image_array = np.array(image_pil)
            
            return image_array
            
        except Exception as e:
            raise FaceDetectionError(f"Error cargando imagen: {str(e)}")
    
    def _compare_encodings(self, encoding1_b64: str, encoding2_b64: str) -> float:
        """
        Compara dos encodings faciales
        
        Args:
            encoding1_b64: Primer encoding en base64
            encoding2_b64: Segundo encoding en base64
            
        Returns:
            float: Distancia euclidiana entre los encodings
            
        Raises:
            FaceVerificationError: Si no se pueden comparar los encodings
        """
        try:
            # Decodificar encodings
            encoding1_bytes = base64.b64decode(encoding1_b64)
            encoding2_bytes = base64.b64decode(encoding2_b64)
            
            # Convertir a arrays numpy
            encoding1 = np.frombuffer(encoding1_bytes, dtype=np.float64)
            encoding2 = np.frombuffer(encoding2_bytes, dtype=np.float64)
            
            # Calcular distancia euclidiana
            distance = np.linalg.norm(encoding1 - encoding2)
            
            return distance
            
        except Exception as e:
            raise FaceVerificationError(f"Error comparando encodings: {str(e)}")
    
    def _calculate_image_quality(self, image_bytes: bytes) -> float:
        """
        Calcula un score de calidad de la imagen (simple)
        
        Args:
            image_bytes: Bytes de la imagen
            
        Returns:
            float: Score de calidad entre 0 y 1
        """
        try:
            # Convertir a formato OpenCV
            nparr = np.frombuffer(image_bytes, np.uint8)
            image_cv = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
            
            if image_cv is None:
                return 0.5  # Calidad media por defecto
            
            # Calcular métricas simples de calidad
            # 1. Resolución
            height, width = image_cv.shape[:2]
            resolution_score = min(1.0, (width * height) / (640 * 480))
            
            # 2. Varianza (como medida de nitidez)
            gray = cv2.cvtColor(image_cv, cv2.COLOR_BGR2GRAY)
            variance = cv2.Laplacian(gray, cv2.CV_64F).var()
            sharpness_score = min(1.0, variance / 1000)  # Normalizar arbitrariamente
            
            # 3. Brillo promedio
            brightness = np.mean(gray)
            brightness_score = 1.0 - abs(brightness - 127) / 127  # Ideal en 127
            
            # Combinar scores
            quality_score = (resolution_score + sharpness_score + brightness_score) / 3
            
            return max(0.0, min(1.0, quality_score))
            
        except Exception as e:
            logger.warning(f"Error calculando calidad de imagen: {str(e)}")
            return 0.5  # Calidad media por defecto
    
    def compare_vectors(self, vector_ref_b64: str, image_bytes: bytes) -> Dict[str, Any]:
        """
        Método de compatibilidad que usa verify_faces internamente
        
        Args:
            vector_ref_b64: Vector de referencia en base64
            image_bytes: Bytes de la imagen a comparar
            
        Returns:
            Dict con formato: {match: bool, confidence_aprox: float}
        """
        try:
            result = self.verify_faces(vector_ref_b64, image_bytes)
            
            return {
                "match": result["isIdentical"],
                "confidence_aprox": result["confidence"]
            }
            
        except Exception as e:
            logger.error(f"Error en compare_vectors: {str(e)}")
            return {
                "match": False,
                "confidence_aprox": 0.0
            }
    
    def encode_face(self, image_bytes: bytes) -> str:
        """
        Método de compatibilidad que usa detect_face internamente
        
        Args:
            image_bytes: Bytes de la imagen
            
        Returns:
            str: Vector facial en base64
            
        Raises:
            FaceDetectionError: Si no se puede generar el encoding
        """
        encoding = self.detect_face(image_bytes)
        if not encoding:
            raise FaceDetectionError("No se pudo generar encoding facial")
        return encoding

    def _simulate_face_detection(self, image_bytes: bytes) -> Optional[str]:
        """
        Simula detección facial cuando face_recognition no está disponible
        
        Args:
            image_bytes: Bytes de la imagen
            
        Returns:
            str: Vector simulado en base64
        """
        try:
            # Verificar que sea una imagen válida
            image = Image.open(io.BytesIO(image_bytes))
            
            # Verificaciones básicas de tamaño
            if image.width < 50 or image.height < 50:
                logger.warning("Imagen muy pequeña para detección simulada")
                return None
                
            # Generar vector simulado basado en hash de la imagen
            import hashlib
            image_hash = hashlib.md5(image_bytes).hexdigest()
            
            # Crear vector simulado de 128 dimensiones (como face_recognition)
            import numpy as np
            np.random.seed(int(image_hash[:8], 16))  # Seed basado en hash
            simulated_vector = np.random.rand(128).astype(np.float64)
            
            # Convertir a base64
            encoding_bytes = simulated_vector.tobytes()
            encoding_b64 = base64.b64encode(encoding_bytes).decode('utf-8')
            
            logger.info("Rostro detectado usando simulación (face_recognition no disponible)")
            return encoding_b64
            
        except Exception as e:
            logger.error(f"Error en simulación de detección: {str(e)}")
            return None
    
    def _simulate_face_verification(self, face_ref: str, image_bytes: bytes) -> Dict[str, Any]:
        """
        Simula verificación facial cuando face_recognition no está disponible
        
        Args:
            face_ref: Vector facial de referencia en base64
            image_bytes: Bytes de la imagen a verificar
            
        Returns:
            Dict con resultado simulado de verificación
        """
        try:
            # Generar encoding simulado de la imagen de prueba
            probe_encoding_b64 = self._simulate_face_detection(image_bytes)
            
            if not probe_encoding_b64:
                return {
                    "isIdentical": False,
                    "confidence": 0.0,
                    "provider": self.provider_name,
                    "threshold": self.threshold,
                    "error": "No se detectó rostro en imagen de verificación (simulado)"
                }
            
            # Simular comparación: si los hashes son similares, es match
            import hashlib
            ref_hash = hashlib.md5(face_ref.encode()).hexdigest()
            probe_hash = hashlib.md5(probe_encoding_b64.encode()).hexdigest()
            
            # Comparar primeros 8 caracteres del hash
            similarity = sum(1 for a, b in zip(ref_hash[:8], probe_hash[:8]) if a == b) / 8
            
            # Agregar algo de aleatoriedad para simular variabilidad real
            import random
            confidence = max(0.0, min(1.0, similarity + random.uniform(-0.2, 0.2)))
            is_match = confidence >= self.threshold
            
            result = {
                "isIdentical": is_match,
                "confidence": float(confidence),
                "provider": f"{self.provider_name} (Simulado)",
                "threshold": self.threshold,
                "distance": float(1.0 - confidence)
            }
            
            logger.info(
                f"Verificación simulada: match={is_match}, "
                f"confidence={confidence:.3f} (face_recognition no disponible)"
            )
            
            return result
            
        except Exception as e:
            logger.error(f"Error en simulación de verificación: {str(e)}")
            raise FaceVerificationError(f"Error en verificación simulada: {str(e)}")
