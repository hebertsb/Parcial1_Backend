"""
Face Recognition Provider Interface and Factory

Este módulo define la interfaz común para proveedores de reconocimiento facial
y el factory pattern para crear instancias del proveedor adecuado.
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
from django.conf import settings
import logging

logger = logging.getLogger('seguridad')


class FaceRecognitionProvider(ABC):
    """
    Interfaz abstracta para proveedores de reconocimiento facial
    """
    
    @abstractmethod
    def detect_face(self, image_bytes: bytes) -> Optional[str]:
        """
        Detecta un rostro en la imagen y retorna un identificador único
        
        Args:
            image_bytes: Bytes de la imagen
            
        Returns:
            str: Identificador único del rostro detectado (faceId para Azure, vector para Local)
            None: Si no se detecta rostro
            
        Raises:
            FaceDetectionError: Si hay error en la detección
        """
        pass
    
    @abstractmethod
    def verify_faces(self, face_ref: str, image_bytes: bytes) -> Dict[str, Any]:
        """
        Verifica si dos rostros pertenecen a la misma persona
        
        Args:
            face_ref: Referencia del rostro enrolado (faceId o vector)
            image_bytes: Bytes de la imagen a verificar
            
        Returns:
            Dict con formato: {
                "isIdentical": bool,
                "confidence": float,
                "provider": str,
                "threshold": float (opcional)
            }
            
        Raises:
            FaceVerificationError: Si hay error en la verificación
        """
        pass
    
    @abstractmethod
    def enroll_face(self, image_bytes: bytes) -> Dict[str, Any]:
        """
        Enrola un rostro para futuras verificaciones
        
        Args:
            image_bytes: Bytes de la imagen de referencia
            
        Returns:
            Dict con formato: {
                "face_reference": str,  # faceId o vector
                "provider": str,
                "confidence": float (opcional),
                "image_url": str (opcional, para Azure)
            }
            
        Raises:
            FaceEnrollmentError: Si hay error en el enrolamiento
        """
        pass
    
    @property
    @abstractmethod
    def provider_name(self) -> str:
        """Retorna el nombre del proveedor"""
        pass


class FaceRecognitionError(Exception):
    """Base exception para errores de reconocimiento facial"""
    pass


class FaceDetectionError(FaceRecognitionError):
    """Error en detección de rostros"""
    pass


class FaceVerificationError(FaceRecognitionError):
    """Error en verificación de rostros"""
    pass


class FaceEnrollmentError(FaceRecognitionError):
    """Error en enrolamiento de rostros"""
    pass


class FaceProviderFactory:
    """
    Factory para crear instancias de proveedores de reconocimiento facial
    """
    
    @staticmethod
    def create_provider() -> FaceRecognitionProvider:
        """
        Crea una instancia del proveedor configurado
        
        Returns:
            FaceRecognitionProvider: Instancia del proveedor
            
        Raises:
            ValueError: Si el proveedor configurado no es válido
        """
        provider_name = getattr(settings, 'FACE_RECOGNITION_PROVIDER', 'Local')
        
        logger.info(f"Creando proveedor de reconocimiento facial: {provider_name}")
        
        if provider_name == 'Microsoft':
            from .azure_face import AzureFaceProvider
            return AzureFaceProvider()
        elif provider_name == 'Local':
            from .local_face import LocalFaceProvider
            return LocalFaceProvider()
        else:
            raise ValueError(f"Proveedor no soportado: {provider_name}")
    
    @staticmethod
    def get_available_providers() -> list:
        """
        Retorna lista de proveedores disponibles
        """
        return ['Microsoft', 'Local']
