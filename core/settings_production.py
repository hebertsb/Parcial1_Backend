"""
Configuración de producción para Railway
"""
import os
from .settings import *

# ==============================================
# CONFIGURACIÓN DE PRODUCCIÓN PARA RAILWAY
# ==============================================

# Variables de entorno para producción
DEBUG = os.getenv('DEBUG', 'False').lower() == 'true'
SECRET_KEY = os.getenv('SECRET_KEY', SECRET_KEY)

# Hosts permitidos para Railway
ALLOWED_HOSTS = [
    'localhost',
    '127.0.0.1',
    '.railway.app',  # Dominios de Railway
    '.up.railway.app',  # Subdominios de Railway
]

# Agregar el dominio personalizado si existe
RAILWAY_DOMAIN = os.getenv('RAILWAY_PUBLIC_DOMAIN')
if RAILWAY_DOMAIN:
    ALLOWED_HOSTS.append(RAILWAY_DOMAIN)

# ==============================================
# CONFIGURACIÓN DE BASE DE DATOS
# ==============================================

# Si tienes una base de datos en Railway, descomenta y configura:
DATABASE_URL = os.getenv('DATABASE_URL')
if DATABASE_URL:
    import dj_database_url
    DATABASES = {
        'default': dj_database_url.parse(DATABASE_URL)
    }
else:
    # Usar SQLite como fallback (solo para desarrollo/pruebas)
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': BASE_DIR / 'db.sqlite3',
        }
    }

# ==============================================
# ARCHIVOS ESTÁTICOS
# ==============================================

# Usar WhiteNoise para servir archivos estáticos
MIDDLEWARE.insert(1, 'whitenoise.middleware.WhiteNoiseMiddleware')

STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

# ==============================================
# CONFIGURACIÓN DE SEGURIDAD
# ==============================================

if not DEBUG:
    # HTTPS y seguridad
    SECURE_BROWSER_XSS_FILTER = True
    SECURE_CONTENT_TYPE_NOSNIFF = True
    X_FRAME_OPTIONS = 'DENY'
    
    # CORS para producción
    CORS_ALLOW_ALL_ORIGINS = False
    CORS_ALLOWED_ORIGINS = [
        "https://tu-frontend.netlify.app",  # Cambia por tu dominio de frontend
        "https://tu-dominio-personalizado.com",
    ]
    
    # Si necesitas credenciales en CORS
    CORS_ALLOW_CREDENTIALS = True

# ==============================================
# CONFIGURACIÓN DE LOGS
# ==============================================

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '{levelname} {asctime} {module} {process:d} {thread:d} {message}',
            'style': '{',
        },
        'simple': {
            'format': '{levelname} {message}',
            'style': '{',
        },
    },
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'formatter': 'verbose',
        },
    },
    'root': {
        'handlers': ['console'],
        'level': 'INFO',
    },
    'loggers': {
        'django': {
            'handlers': ['console'],
            'level': 'INFO',
            'propagate': True,
        },
        'core': {
            'handlers': ['console'],
            'level': 'DEBUG' if DEBUG else 'INFO',
            'propagate': True,
        },
    },
}

# ==============================================
# CONFIGURACIÓN DE MEDIA FILES
# ==============================================

# Para archivos de media en Railway
MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

# ==============================================
# CONFIGURACIÓN ESPECÍFICA DE TU APLICACIÓN
# ==============================================

# Configuración para OCR y Face Recognition
TESSERACT_CMD = os.getenv('TESSERACT_CMD', '/usr/bin/tesseract')

# Configuración para Dropbox (si la usas)
DROPBOX_ACCESS_TOKEN = os.getenv('DROPBOX_ACCESS_TOKEN')

# Configuración para Azure (si la usas)
AZURE_FACE_KEY = os.getenv('AZURE_FACE_KEY')
AZURE_FACE_ENDPOINT = os.getenv('AZURE_FACE_ENDPOINT')