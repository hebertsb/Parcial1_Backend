#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Inicializador del servidor WebRTC para reconocimiento facial
"""

import uvicorn
import sys
import os
import django
from pathlib import Path

# Agregar el directorio raíz al path
BASE_DIR = Path(__file__).resolve().parent
sys.path.append(str(BASE_DIR))

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

def start_webrtc_server():
    """Iniciar servidor WebRTC"""
    print("🚀 Iniciando servidor WebRTC para reconocimiento facial...")
    print("📡 Socket.IO Server: ws://localhost:8001")
    print("🎥 Reconocimiento en tiempo real con YOLO + OpenCV")
    print("⚡ Optimizado para alta performance")
    print("-" * 50)
    
    # Importar la aplicación después de configurar Django
    from seguridad.webrtc_server import app
    
    # Configuración del servidor
    config = uvicorn.Config(
        app=app,
        host="0.0.0.0",
        port=8001,
        log_level="info",
        reload=False,  # Desactivar reload para mejor performance
        access_log=True,
    )
    
    server = uvicorn.Server(config)
    server.run()

if __name__ == "__main__":
    try:
        start_webrtc_server()
    except KeyboardInterrupt:
        print("\n🛑 Servidor WebRTC detenido por el usuario")
    except Exception as e:
        print(f"❌ Error iniciando servidor WebRTC: {str(e)}")
        sys.exit(1)