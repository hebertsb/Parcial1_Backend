#!/usr/bin/env python3
"""
Script para corregir URLs de Dropbox en el modelo de seguridad
"""
import os
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from seguridad.models import ReconocimientoFacial

def convertir_url_dropbox(url):
    """Convierte URL de Dropbox al formato correcto para mostrar imágenes"""
    if not url:
        return url
    
    if 'www.dropbox.com/scl/fi/' in url and '?dl=1' in url:
        # Extraer el ID del archivo
        id_inicio = url.find('/scl/fi/') + 8
        id_fin = url.find('/', id_inicio)
        file_id = url[id_inicio:id_fin]
        
        # Extraer el nombre del archivo
        nombre_inicio = url.rfind('/') + 1
        nombre_fin = url.find('?dl=1')
        nombre_archivo = url[nombre_inicio:nombre_fin]
        
        # Construir la nueva URL
        nueva_url = f"https://dl.dropboxusercontent.com/scl/fi/{file_id}/{nombre_archivo}"
        return nueva_url
    
    return url

def main():
    print("🔧 CORRIGIENDO URLs EN MODELO SEGURIDAD...")
    print("=" * 60)
    
    reconocimientos = ReconocimientoFacial.objects.all()
    total_registros = reconocimientos.count()
    registros_actualizados = 0
    total_fotos_corregidas = 0
    
    for reconocimiento in reconocimientos:
        if reconocimiento.fotos_urls:
            # Verificar si es string o lista
            if isinstance(reconocimiento.fotos_urls, str):
                import json
                try:
                    urls_originales = json.loads(reconocimiento.fotos_urls)
                except:
                    urls_originales = [reconocimiento.fotos_urls]
            else:
                urls_originales = reconocimiento.fotos_urls.copy()
            
            urls_corregidas = []
            fotos_corregidas_este_registro = 0
            
            for url in urls_originales:
                url_nueva = convertir_url_dropbox(url)
                urls_corregidas.append(url_nueva)
                
                if url != url_nueva:
                    fotos_corregidas_este_registro += 1
            
            if fotos_corregidas_este_registro > 0:
                reconocimiento.fotos_urls = urls_corregidas
                reconocimiento.save()
                registros_actualizados += 1
                total_fotos_corregidas += fotos_corregidas_este_registro
                
                print(f"✅ Registro {reconocimiento.id}: {fotos_corregidas_este_registro} fotos corregidas")
    
    print()
    print("📊 RESUMEN DE CORRECCIÓN:")
    print(f"   📋 Total registros: {total_registros}")
    print(f"   🔄 Registros actualizados: {registros_actualizados}")
    print(f"   📸 Total fotos corregidas: {total_fotos_corregidas}")
    print()
    
    # Verificación final
    print("🔍 VERIFICACIÓN FINAL:")
    total_fotos_sistema = 0
    urls_correctas = 0
    
    for r in ReconocimientoFacial.objects.all():
        if r.fotos_urls:
            total_fotos_sistema += len(r.fotos_urls)
            for url in r.fotos_urls:
                if url and 'dl.dropboxusercontent.com' in url:
                    urls_correctas += 1
    
    print(f"   💾 Total fotos en sistema: {total_fotos_sistema}")
    print(f"   ✅ URLs en formato correcto: {urls_correctas}")
    if total_fotos_sistema > 0:
        porcentaje = (urls_correctas / total_fotos_sistema) * 100
        print(f"   📈 Éxito: {porcentaje:.1f}%")
        
        if porcentaje == 100:
            print()
            print("🎉 ¡TODAS LAS URLs ESTÁN CORREGIDAS!")
            print("🚀 El frontend puede mostrar las imágenes correctamente")

if __name__ == "__main__":
    main()