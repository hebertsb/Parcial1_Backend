#!/usr/bin/env python3
"""
AGREGAR FOTOS DE EJEMPLO A LARA
===============================
"""

import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from seguridad.models import ReconocimientoFacial
from authz.models import Usuario

def main():
    print("📸 AGREGANDO FOTOS DE EJEMPLO A LARA")
    print("=" * 40)
    
    try:
        # Buscar reconocimiento de lara
        lara_reconoc = ReconocimientoFacial.objects.get(id=7)
        print(f"✅ ReconocimientoFacial encontrado: ID {lara_reconoc.id}")
        
        # Agregar URLs de ejemplo (simulando fotos de Dropbox)
        fotos_ejemplo = [
            "https://dl.dropboxusercontent.com/scl/fi/ejemplo1/lara_foto1.jpg?rlkey=abc123",
            "https://dl.dropboxusercontent.com/scl/fi/ejemplo2/lara_foto2.jpg?rlkey=def456",
            "https://dl.dropboxusercontent.com/scl/fi/ejemplo3/lara_foto3.jpg?rlkey=ghi789"
        ]
        
        # Guardar en el campo vector_facial como URLs separadas por comas
        lara_reconoc.vector_facial = ','.join(fotos_ejemplo)
        lara_reconoc.save()
        
        print(f"✅ Fotos agregadas: {len(fotos_ejemplo)}")
        for i, foto in enumerate(fotos_ejemplo, 1):
            print(f"   📸 Foto {i}: {foto[:50]}...")
        
        # Verificar que se guardó correctamente
        lara_reconoc.refresh_from_db()
        fotos_guardadas = lara_reconoc.vector_facial.split(',') if lara_reconoc.vector_facial else []
        print(f"✅ Verificación: {len(fotos_guardadas)} fotos guardadas")
        
        print("\n🎯 LISTO PARA PROBAR EN FRONTEND:")
        print("   El usuario lara@gmail.com ahora tiene fotos")
        print("   El endpoint GET debe devolver estas URLs")
        
    except ReconocimientoFacial.DoesNotExist:
        print("❌ ReconocimientoFacial ID 7 no encontrado")
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    main()