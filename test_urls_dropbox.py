#!/usr/bin/env python3
"""
Test de URLs de Dropbox para verificar que sean accesibles
"""
import os
import django
import json
import requests
from urllib.parse import urlparse

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from seguridad.models import ReconocimientoFacial

def test_url_accesibilidad(url, timeout=5):
    """
    Prueba si una URL es accesible y devuelve una imagen
    """
    try:
        response = requests.head(url, timeout=timeout, allow_redirects=True)
        
        # Verificar código de respuesta
        if response.status_code == 200:
            content_type = response.headers.get('content-type', '').lower()
            
            if 'image' in content_type:
                return {
                    'accesible': True,
                    'tipo_contenido': content_type,
                    'tamaño': response.headers.get('content-length', 'Desconocido'),
                    'error': None
                }
            else:
                return {
                    'accesible': False,
                    'tipo_contenido': content_type,
                    'error': f'No es imagen, tipo: {content_type}'
                }
        else:
            return {
                'accesible': False,
                'error': f'Código HTTP: {response.status_code}'
            }
            
    except requests.exceptions.RequestException as e:
        return {
            'accesible': False,
            'error': f'Error de conexión: {str(e)}'
        }

def main():
    print("🧪 TEST DE ACCESIBILIDAD DE URLs DE DROPBOX")
    print("=" * 70)
    
    total_urls = 0
    urls_accesibles = 0
    urls_con_error = 0
    
    for r in ReconocimientoFacial.objects.all():
        if r.fotos_urls:
            try:
                if isinstance(r.fotos_urls, str):
                    urls = json.loads(r.fotos_urls)
                else:
                    urls = r.fotos_urls
                
                if urls:
                    print(f"\n📋 REGISTRO {r.id} - Testando {len(urls)} URLs:")
                    
                    for i, url in enumerate(urls, 1):
                        total_urls += 1
                        print(f"   🔗 Foto {i}: Probando URL...", end=' ')
                        
                        # Test de accesibilidad
                        resultado = test_url_accesibilidad(url)
                        
                        if resultado['accesible']:
                            print(f"✅ ACCESIBLE")
                            print(f"      Tipo: {resultado['tipo_contenido']}")
                            if resultado['tamaño'] != 'Desconocido':
                                print(f"      Tamaño: {resultado['tamaño']} bytes")
                            urls_accesibles += 1
                        else:
                            print(f"❌ ERROR")
                            print(f"      Error: {resultado['error']}")
                            urls_con_error += 1
                        
                        # Mostrar URL para referencia
                        print(f"      URL: {url[:60]}{'...' if len(url) > 60 else ''}")
                        
            except Exception as e:
                print(f"❌ Error procesando registro {r.id}: {e}")
    
    print()
    print("=" * 70)
    print("📊 RESUMEN DEL TEST:")
    print(f"   🔗 Total URLs probadas: {total_urls}")
    print(f"   ✅ URLs accesibles: {urls_accesibles}")
    print(f"   ❌ URLs con error: {urls_con_error}")
    
    if total_urls > 0:
        porcentaje_exito = (urls_accesibles / total_urls) * 100
        print(f"   📈 Tasa de éxito: {porcentaje_exito:.1f}%")
        
        if porcentaje_exito == 100:
            print("\n🎉 ¡PERFECTO! Todas las URLs son accesibles")
            print("🚀 El frontend puede cargar todas las imágenes sin problemas")
        elif porcentaje_exito >= 80:
            print("\n⚠️  La mayoría de URLs funcionan, pero algunas necesitan atención")
        else:
            print("\n❌ Muchas URLs tienen problemas, revisar configuración de Dropbox")
    
    print()
    print("💡 NOTA: Si hay errores, podrían ser URLs de ejemplo/prueba que no apuntan a archivos reales")

if __name__ == "__main__":
    main()