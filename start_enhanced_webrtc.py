# start_enhanced_webrtc.py - Script mejorado para iniciar servidor WebRTC para React
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script de inicio optimizado para React Frontend
Compatible con WebRTCFaceRecognition.tsx
"""

import os
import sys
import logging
import asyncio
from pathlib import Path

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler('webrtc_enhanced.log')
    ]
)

logger = logging.getLogger('webrtc_startup')

def setup_django():
    """Configurar Django para el servidor WebRTC"""
    try:
        # Configurar path de Django
        project_root = Path(__file__).parent
        sys.path.insert(0, str(project_root))
        
        # Configurar settings
        os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
        
        import django
        django.setup()
        
        logger.info("✅ Django configurado correctamente")
        return True
        
    except Exception as e:
        logger.error(f"❌ Error configurando Django: {e}")
        return False

def check_dependencies():
    """Verificar que todas las dependencias están instaladas"""
    required_packages = [
        'socketio',
        'cv2',
        'numpy',
        'django',
        'uvicorn'
    ]
    
    missing_packages = []
    
    for package in required_packages:
        try:
            if package == 'cv2':
                import cv2
            elif package == 'socketio':
                import socketio
            elif package == 'numpy':
                import numpy
            elif package == 'django':
                import django
            elif package == 'uvicorn':
                import uvicorn
            
            logger.info(f"✅ {package} disponible")
            
        except ImportError:
            missing_packages.append(package)
            logger.error(f"❌ {package} no encontrado")
    
    if missing_packages:
        logger.error(f"Instalar dependencias faltantes: pip install {' '.join(missing_packages)}")
        return False
    
    logger.info("✅ Todas las dependencias están disponibles")
    return True

def start_enhanced_server():
    """Iniciar el servidor WebRTC mejorado"""
    try:
        import uvicorn
        from webrtc_enhanced_server import app
        
        logger.info("🚀 Iniciando Enhanced WebRTC Server...")
        logger.info("📡 Compatible con React Frontend")
        logger.info("🔗 Conectar desde: http://localhost:3000")
        logger.info("⚡ Socket.IO en: http://localhost:8001")
        
        # Configuración optimizada para desarrollo
        uvicorn.run(
            app,
            host="0.0.0.0",
            port=8001,
            reload=True,
            log_level="info",
            access_log=True,
            ws_ping_interval=25,
            ws_ping_timeout=60
        )
        
    except Exception as e:
        logger.error(f"❌ Error iniciando servidor: {e}")
        sys.exit(1)

def main():
    """Función principal"""
    logger.info("🎬 Iniciando Enhanced WebRTC Server para React...")
    
    # 1. Verificar dependencias
    if not check_dependencies():
        logger.error("❌ Dependencias faltantes. Ejecutar: pip install -r requirements_webrtc.txt")
        sys.exit(1)
    
    # 2. Configurar Django
    if not setup_django():
        logger.error("❌ Error en configuración Django")
        sys.exit(1)
    
    # 3. Verificar modelos Django
    try:
        from seguridad.models import Copropietarios, ReconocimientoFacial
        logger.info("✅ Modelos Django accesibles")
    except Exception as e:
        logger.error(f"❌ Error accediendo modelos Django: {e}")
        sys.exit(1)
    
    # 4. Verificar proveedores de reconocimiento
    try:
        from seguridad.services.realtime_face_provider import OpenCVFaceProvider
        provider = OpenCVFaceProvider()
        logger.info("✅ Proveedor OpenCV disponible")
    except Exception as e:
        logger.warning(f"⚠️ Advertencia proveedor OpenCV: {e}")
    
    # 5. Iniciar servidor
    logger.info("🎯 Todo listo. Iniciando servidor...")
    start_enhanced_server()

if __name__ == "__main__":
    main()