#!/usr/bin/env python3
# servidor_webrtc_basico.py - Versión básica usando Django existente
import os
import sys
import django
from django.conf import settings

# Configurar Django
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

# Ahora ejecutar Django en puerto 8001
if __name__ == '__main__':
    print("🚀 Iniciando Django + WebRTC en puerto 8001...")
    
    import subprocess
    try:
        # Iniciar Django en puerto 8001
        result = subprocess.run([
            sys.executable, 
            'manage.py', 
            'runserver', 
            '0.0.0.0:8001'
        ], check=True)
    except KeyboardInterrupt:
        print("\n🛑 Servidor detenido por el usuario")
    except Exception as e:
        print(f"❌ Error: {e}")