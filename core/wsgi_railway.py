"""
WSGI config for Railway deployment - MINIMAL VERSION
"""

import os
from django.core.wsgi import get_wsgi_application

# Configuración mínima para Railway
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings_railway')

application = get_wsgi_application()