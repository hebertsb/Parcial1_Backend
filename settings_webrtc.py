# settings_webrtc.py - Configuración adicional para WebRTC
import os
from pathlib import Path

# Configuración WebRTC específica
WEBRTC_SERVER_HOST = '0.0.0.0'
WEBRTC_SERVER_PORT = 8001
WEBRTC_CORS_ORIGINS = [
    "http://localhost:3000",    # Next.js dev
    "http://localhost:3001",    # Next.js alt
    "http://127.0.0.1:3000",
    "http://127.0.0.1:3001",
    "https://localhost:3000",
    "https://127.0.0.1:3000",
]

# Configuración Socket.IO
SOCKETIO_CORS_ALLOWED_ORIGINS = WEBRTC_CORS_ORIGINS
SOCKETIO_LOGGER = True
SOCKETIO_ENGINEIO_LOGGER = True

# Configuración de reconocimiento facial
FACE_RECOGNITION_SETTINGS = {
    'MAX_FPS': 10,
    'DEFAULT_FPS': 5,
    'MAX_QUALITY': 1.0,
    'DEFAULT_QUALITY': 0.7,
    'SUPPORTED_FORMATS': ['image/jpeg', 'image/png'],
    'MAX_RESOLUTION': {
        'width': 1280,
        'height': 720
    },
    'TIMEOUT_SECONDS': 30,
    'MAX_CONCURRENT_CLIENTS': 10
}

# Configuración de proveedores
FACE_PROVIDERS_CONFIG = {
    'opencv': {
        'enabled': True,
        'confidence_threshold': 0.7,
        'model_path': 'seguridad/models/'
    },
    'azure': {
        'enabled': False,  # Habilitar si tienes Azure Face API
        'endpoint': os.getenv('AZURE_FACE_ENDPOINT', ''),
        'api_key': os.getenv('AZURE_FACE_API_KEY', ''),
        'confidence_threshold': 0.5
    }
}

# Stats y monitoring
WEBRTC_STATS = {
    'enable_real_time_stats': True,
    'stats_update_interval': 1.0,  # segundos
    'enable_frame_logging': True,
    'max_log_entries': 1000
}