"""
Azure Face API Provider

Implementación del proveedor de reconocimiento facial usando Azure Cognitive Services Face API
"""

import io
import base64
import logging
from typing import Dict, Any, Optional
from django.conf import settings
from azure.cognitiveservices.vision.face import FaceClient
from azure.cognitiveservices.vision.face.models import TrainingStatusType, Person
from msrest.authentication import CognitiveServicesCredentials
from PIL import Image

from .face_provider import (
    FaceRecognitionProvider, 
    FaceDetectionError, 
    FaceVerificationError, 
    FaceEnrollmentError
)

logger = logging.getLogger('seguridad')


class AzureFaceProvider(FaceRecognitionProvider):
    """
    Proveedor de reconocimiento facial usando Azure Face API
    """
    
    def __init__(self):
        """Inicializa el cliente de Azure Face API"""
        self.api_key = getattr(settings, 'AZURE_FACE_API_KEY', '')
        self.endpoint = getattr(settings, 'AZURE_FACE_ENDPOINT', '')
        
        if not self.api_key or not self.endpoint:
            raise ValueError(
                "Azure Face API key y endpoint son requeridos. "
                "Configura AZURE_FACE_API_KEY y AZURE_FACE_ENDPOINT en settings."
            )
        
        self.face_client = FaceClient(
            self.endpoint, 
            CognitiveServicesCredentials(self.api_key)
        )
        
        logger.info("Azure Face API client inicializado")
    
    def detect_face(self, image_bytes: bytes) -> Optional[str]:
        """
        Detecta un rostro usando Azure Face API
        
        Args:
            image_bytes: Bytes de la imagen
            
        Returns:
            str: faceId de Azure o None si no se detecta rostro
            
        Raises:
            FaceDetectionError: Si hay error en la detección
        """
        try:
            # Validar imagen
            self._validate_image(image_bytes)
            
            # Detectar rostros
            detected_faces = self.face_client.face.detect_with_stream(
                image=io.BytesIO(image_bytes),
                return_face_id=True,
                return_face_landmarks=False,
                return_face_attributes=None
            )
            
            if not detected_faces:
                logger.warning("No se detectaron rostros en la imagen")
                return None
            
            if len(detected_faces) > 1:
                logger.warning(f"Se detectaron {len(detected_faces)} rostros, usando el primero")
            
            face_id = detected_faces[0].face_id
            logger.info(f"Rostro detectado con faceId: {face_id}")
            
            return str(face_id)
            
        except Exception as e:
            logger.error(f"Error en detección de rostro Azure: {str(e)}")
            raise FaceDetectionError(f"Error en Azure Face detection: {str(e)}")
    
    def verify_faces(self, face_ref: str, image_bytes: bytes) -> Dict[str, Any]:
        """
        Verifica dos rostros usando Azure Face API
        
        Args:
            face_ref: faceId de referencia
            image_bytes: Bytes de la imagen a verificar
            
        Returns:
            Dict con resultado de verificación
            
        Raises:
            FaceVerificationError: Si hay error en la verificación
        """
        try:
            # Detectar rostro en imagen de prueba
            probe_face_id = self.detect_face(image_bytes)
            
            if not probe_face_id:
                return {
                    "isIdentical": False,
                    "confidence": 0.0,
                    "provider": self.provider_name,
                    "error": "No se detectó rostro en imagen de verificación"
                }
            
            # Verificar rostros
            verify_result = self.face_client.face.verify_face_to_face(
                face_id1=face_ref,
                face_id2=probe_face_id
            )
            
            result = {
                "isIdentical": verify_result.is_identical,
                "confidence": float(verify_result.confidence),
                "provider": self.provider_name
            }
            
            logger.info(
                f"Verificación Azure: match={result['isIdentical']}, "
                f"confidence={result['confidence']}"
            )
            
            return result
            
        except Exception as e:
            logger.error(f"Error en verificación Azure: {str(e)}")
            raise FaceVerificationError(f"Error en Azure Face verification: {str(e)}")
    
    def enroll_face(self, image_bytes: bytes) -> Dict[str, Any]:
        """
        Enrola un rostro usando Azure Face API
        
        Args:
            image_bytes: Bytes de la imagen de referencia
            
        Returns:
            Dict con datos del enrolamiento
            
        Raises:
            FaceEnrollmentError: Si hay error en el enrolamiento
        """
        try:
            # Detectar rostro
            face_id = self.detect_face(image_bytes)
            
            if not face_id:
                raise FaceEnrollmentError("No se detectó rostro en imagen de enrolamiento")
            
            # Para Azure, el face_id tiene vida limitada (24 horas)
            # En un caso real, se debería crear un PersonGroup y Person
            # para persistencia a largo plazo
            
            result = {
                "face_reference": face_id,
                "provider": self.provider_name,
                "image_url": None  # En implementación completa, subir a blob storage
            }
            
            logger.info(f"Enrolamiento exitoso con faceId: {face_id}")
            
            return result
            
        except FaceDetectionError:
            raise
        except Exception as e:
            logger.error(f"Error en enrolamiento Azure: {str(e)}")
            raise FaceEnrollmentError(f"Error en Azure Face enrollment: {str(e)}")
    
    @property
    def provider_name(self) -> str:
        """Retorna el nombre del proveedor"""
        return "Microsoft"
    
    def _validate_image(self, image_bytes: bytes) -> None:
        """
        Valida que la imagen sea válida para Azure Face API
        
        Args:
            image_bytes: Bytes de la imagen
            
        Raises:
            FaceDetectionError: Si la imagen no es válida
        """
        try:
            # Validar que es una imagen válida
            image = Image.open(io.BytesIO(image_bytes))
            
            # Azure Face API requisitos:
            # - Formato: JPEG, PNG, GIF, BMP
            # - Tamaño: 1KB a 6MB
            # - Dimensiones: 36x36 a 4096x4096 pixels
            
            size_mb = len(image_bytes) / (1024 * 1024)
            if size_mb > 6:
                raise FaceDetectionError("Imagen muy grande (máximo 6MB)")
            
            if len(image_bytes) < 1024:
                raise FaceDetectionError("Imagen muy pequeña (mínimo 1KB)")
            
            width, height = image.size
            if width < 36 or height < 36 or width > 4096 or height > 4096:
                raise FaceDetectionError(
                    "Dimensiones inválidas (debe ser entre 36x36 y 4096x4096 pixels)"
                )
            
            # Validar formato
            if image.format not in ['JPEG', 'PNG', 'GIF', 'BMP']:
                raise FaceDetectionError(
                    f"Formato no soportado: {image.format}. "
                    "Formatos soportados: JPEG, PNG, GIF, BMP"
                )
                
        except Exception as e:
            if isinstance(e, FaceDetectionError):
                raise
            raise FaceDetectionError(f"Error validando imagen: {str(e)}")
    
    def create_person_group(self, group_id: str, group_name: str) -> None:
        """
        Crea un grupo de personas para persistencia a largo plazo
        (Funcionalidad extendida para implementación completa)
        """
        try:
            self.face_client.person_group.create(
                person_group_id=group_id,
                name=group_name
            )
            logger.info(f"PersonGroup creado: {group_id}")
        except Exception as e:
            logger.error(f"Error creando PersonGroup: {str(e)}")
            raise
    
    def train_person_group(self, group_id: str) -> None:
        """
        Entrena un grupo de personas
        (Funcionalidad extendida para implementación completa)
        """
        try:
            self.face_client.person_group.train(person_group_id=group_id)
            logger.info(f"Entrenamiento iniciado para PersonGroup: {group_id}")
        except Exception as e:
            logger.error(f"Error entrenando PersonGroup: {str(e)}")
            raise
