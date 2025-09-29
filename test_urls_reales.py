#!/usr/bin/env python3
"""
Test específico de URLs reales de Dropbox
"""
import os
import django
import json
import requests

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from seguridad.models import ReconocimientoFacial

def test_urls_reales():
    print('🧪 TEST ESPECÍFICO DE URLs REALES DE DROPBOX')
    print('=' * 60)
    
    # Obtener solo registros con URLs reales
    registros_reales = []
    
    for r in ReconocimientoFacial.objects.all():
        if r.fotos_urls:
            try:
                if isinstance(r.fotos_urls, str):
                    urls = json.loads(r.fotos_urls)
                else:
                    urls = r.fotos_urls
                
                # Verificar si tiene URLs reales
                urls_reales = [url for url in urls if 
                             any(word in url for word in ['reconocimiento_2025', 'propietario_', '_20250928_'])]
                
                if urls_reales:
                    registros_reales.append((r.id, urls_reales))
                    
            except Exception as e:
                print(f'❌ Error procesando registro {r.id}: {e}')
    
    print(f'📋 Encontrados {len(registros_reales)} registros con URLs reales')
    print()
    
    for registro_id, urls_reales in registros_reales:
        print(f'📸 REGISTRO {registro_id} - Testando {len(urls_reales)} URLs reales:')
        
        for i, url in enumerate(urls_reales[:3], 1):  # Test solo las primeras 3 URLs
            print(f'   🔗 Foto {i}: Testando...', end=' ')
            
            try:
                response = requests.head(url, timeout=10, allow_redirects=True)
                
                if response.status_code == 200:
                    content_type = response.headers.get('content-type', '').lower()
                    if 'image' in content_type:
                        tamaño = response.headers.get('content-length', 'Desconocido')
                        print(f'✅ FUNCIONAL ({content_type}, {tamaño} bytes)')
                    else:
                        print(f'⚠️  Respuesta OK pero no es imagen ({content_type})')
                elif response.status_code == 403:
                    print('🔒 ACCESO DENEGADO (403) - Verificar permisos de Dropbox')
                elif response.status_code == 404:
                    print('❌ NO ENCONTRADO (404) - URL no válida')
                else:
                    print(f'❌ ERROR HTTP {response.status_code}')
                    
            except requests.exceptions.Timeout:
                print('⏱️  TIMEOUT - Dropbox no responde')
            except requests.exceptions.RequestException as e:
                print(f'❌ ERROR DE RED: {str(e)[:50]}...')
            
            # Mostrar URL para referencia
            print(f'      URL: {url[:80]}...')
        
        if len(urls_reales) > 3:
            print(f'   ... y {len(urls_reales) - 3} URLs más por testear')
        print()
    
    print('🔍 ANÁLISIS:')
    print('• Si ves ✅ FUNCIONAL: Las URLs están correctas y accesibles')
    print('• Si ves 🔒 ACCESO DENEGADO: Las URLs existen pero necesitan configuración de permisos')
    print('• Si ves ❌ NO ENCONTRADO: Las URLs no apuntan a archivos reales')
    print()
    print('💡 NOTA: Error 403 es común en Dropbox si los archivos no son públicos')

if __name__ == "__main__":
    test_urls_reales()