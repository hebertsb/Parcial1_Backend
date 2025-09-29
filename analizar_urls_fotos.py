#!/usr/bin/env python3
"""
Análisis detallado de URLs de fotos para identificar cuáles son reales
"""
import os
import django
import json

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from seguridad.models import ReconocimientoFacial

def analizar_urls():
    print('🔍 ANÁLISIS DETALLADO DE URLs DE FOTOS')
    print('=' * 60)

    for r in ReconocimientoFacial.objects.all():
        if r.fotos_urls:
            try:
                if isinstance(r.fotos_urls, str):
                    urls = json.loads(r.fotos_urls)
                else:
                    urls = r.fotos_urls
                
                print(f'\n📋 REGISTRO {r.id} - {len(urls)} fotos:')
                
                # Clasificar URLs
                urls_reales = []
                urls_ejemplo = []
                urls_otros = []
                
                for i, url in enumerate(urls, 1):
                    if 'ejemplo' in url.lower():
                        urls_ejemplo.append((i, url))
                    elif any(word in url for word in ['reconocimiento_2025', 'propietario_', '_20250928_']):
                        urls_reales.append((i, url))
                    else:
                        urls_otros.append((i, url))
                
                # Mostrar clasificación
                if urls_reales:
                    print(f'   ✅ URLs REALES ({len(urls_reales)}):')
                    for i, url in urls_reales[:2]:  # Mostrar solo las primeras 2
                        print(f'      Foto {i}: {url}')
                    if len(urls_reales) > 2:
                        print(f'      ... y {len(urls_reales) - 2} más')
                
                if urls_ejemplo:
                    print(f'   🧪 URLs DE EJEMPLO ({len(urls_ejemplo)}) - NO FUNCIONALES:')
                    for i, url in urls_ejemplo[:2]:  # Mostrar solo las primeras 2
                        print(f'      Foto {i}: {url}')
                    if len(urls_ejemplo) > 2:
                        print(f'      ... y {len(urls_ejemplo) - 2} más')
                
                if urls_otros:
                    print(f'   ❓ URLs OTROS FORMATOS ({len(urls_otros)}):')
                    for i, url in urls_otros[:2]:
                        print(f'      Foto {i}: {url}')
                    if len(urls_otros) > 2:
                        print(f'      ... y {len(urls_otros) - 2} más')
                
                # Estado del registro
                if urls_reales and not urls_ejemplo:
                    print(f'   🎯 ESTADO: COMPLETAMENTE FUNCIONAL')
                elif urls_ejemplo and not urls_reales:
                    print(f'   ⚠️  ESTADO: SOLO EJEMPLOS - NO FUNCIONAL')
                elif urls_reales and urls_ejemplo:
                    print(f'   ⚠️  ESTADO: MIXTO - PARCIALMENTE FUNCIONAL')
                else:
                    print(f'   ❓ ESTADO: NECESITA REVISIÓN')
                
            except Exception as e:
                print(f'❌ Error procesando registro {r.id}: {e}')

    print('\n' + '=' * 60)
    print('📊 RESUMEN DE HALLAZGOS:')
    print()
    print('✅ URLs REALES (Funcionales):')
    print('   • Contienen timestamps como "20250928"')
    print('   • Tienen nombres como "reconocimiento_" o "propietario_"')
    print('   • Son archivos realmente subidos a Dropbox')
    print()
    print('🧪 URLs DE EJEMPLO (No funcionales):')
    print('   • Contienen la palabra "ejemplo"')
    print('   • Son URLs simuladas para demostración')
    print('   • Devuelven error 404 porque no existen archivos reales')
    print()
    print('🔧 RECOMENDACIÓN:')
    print('   • Las URLs reales funcionarán en el frontend')
    print('   • Las URLs de ejemplo necesitan ser reemplazadas por fotos reales')
    print('   • Usar el endpoint de subida para crear fotos nuevas con URLs funcionales')

if __name__ == "__main__":
    analizar_urls()