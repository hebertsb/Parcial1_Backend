#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Parche para evitar errores de importación en Railway
Este archivo reemplaza imports problemáticos con versiones seguras
"""

# Monkey patch para imports problemáticos
import sys
import logging

logger = logging.getLogger('seguridad')

def patch_imports():
    """Aplica parches para imports problemáticos"""
    try:
        # Intentar import normal
        import face_recognition
        logger.info("✅ face_recognition disponible - sin parches necesarios")
        return True
    except ImportError:
        logger.warning("⚠️ face_recognition no disponible - aplicando parches")
        
        # Crear módulos mock para evitar errores
        class MockFaceRecognition:
            @staticmethod
            def load_image_file(*args, **kwargs):
                return []
            
            @staticmethod
            def face_locations(*args, **kwargs):
                return []
            
            @staticmethod  
            def face_encodings(*args, **kwargs):
                return []
            
            @staticmethod
            def face_distance(*args, **kwargs):
                return [0.5]
        
        class MockNumpy:
            @staticmethod
            def array(data):
                return data
            
            @staticmethod
            def frombuffer(*args, **kwargs):
                return []
        
        # Añadir mocks al sys.modules con typing correcto
        from types import ModuleType
        
        # Crear instancias mock que hereden de ModuleType
        face_recognition_mock = type('MockFaceRecognition', (MockFaceRecognition,), {})()
        numpy_mock = type('MockNumpy', (MockNumpy,), {})()
        
        sys.modules['face_recognition'] = face_recognition_mock  # type: ignore
        sys.modules['numpy'] = numpy_mock  # type: ignore
        
        logger.info("🔧 Parches aplicados exitosamente")
        return False

# Aplicar parches al importar este módulo
FACE_RECOGNITION_AVAILABLE = patch_imports()