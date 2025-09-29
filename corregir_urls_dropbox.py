#!/usr/bin/env python
"""
Script para corregir URLs de Dropbox a formato directo para imágenes
"""
import os
import sys
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from seguridad.models import ReconocimientoFacial
import json

def convertir_url_dropbox_a_directa(url):
    """
    Convierte una URL de Dropbox al formato de descarga directa para imágenes
    """
    if not url:
        return url
    
    # Convertir desde www.dropbox.com a dl.dropboxusercontent.com
    if url.startswith("https://www.dropbox.com/scl/fi/"):
        # Formato: https://www.dropbox.com/scl/fi/ID/filename?dl=1
        # Convertir a: https://dl.dropboxusercontent.com/scl/fi/ID/filename
        url = url.replace("https://www.dropbox.com/scl/fi/", "https://dl.dropboxusercontent.com/scl/fi/")
        # Remover parámetros dl
        if "?dl=1" in url:
            url = url.replace("?dl=1", "")
        if "?dl=0" in url:
            url = url.replace("?dl=0", "")
        print(f"✅ Convertida: {url}")
        return url
    
    # Ya está en formato correcto
    if url.startswith("https://dl.dropboxusercontent.com/"):
        return url
        
    return url

def corregir_urls_reconocimiento():
    """
    Corregir todas las URLs de reconocimiento facial en la base de datos
    """
    print("🔧 Corrigiendo URLs de Dropbox en la base de datos...")
    
    reconocimientos = ReconocimientoFacial.objects.filter(
        fotos_urls__isnull=False
    ).exclude(fotos_urls='')
    
    total_corregidos = 0
    
    for reconocimiento in reconocimientos:
        try:
            fotos_list = json.loads(reconocimiento.fotos_urls)
            if isinstance(fotos_list, list):
                fotos_corregidas = []
                cambios = False
                
                for url in fotos_list:
                    url_original = url
                    url_corregida = convertir_url_dropbox_a_directa(url)
                    fotos_corregidas.append(url_corregida)
                    
                    if url_original != url_corregida:
                        cambios = True
                
                if cambios:
                    reconocimiento.fotos_urls = json.dumps(fotos_corregidas)
                    reconocimiento.save()
                    total_corregidos += 1
                    print(f"✅ Corregido reconocimiento ID {reconocimiento.id} - {len(fotos_corregidas)} fotos")
                    
        except (json.JSONDecodeError, TypeError) as e:
            print(f"❌ Error procesando reconocimiento ID {reconocimiento.id}: {e}")
            continue
    
    print(f"\n🎉 Proceso completado: {total_corregidos} reconocimientos corregidos")

def mostrar_urls_actuales():
    """
    Mostrar las URLs actuales para verificación
    """
    print("\n📋 URLs ACTUALES EN LA BASE DE DATOS:")
    print("-" * 60)
    
    reconocimientos = ReconocimientoFacial.objects.filter(
        fotos_urls__isnull=False
    ).exclude(fotos_urls='')[:3]  # Solo los primeros 3
    
    for reconocimiento in reconocimientos:
        try:
            copropietario = reconocimiento.copropietario
            print(f"\n👤 {copropietario.nombres} {copropietario.apellidos}")
            
            fotos_list = json.loads(reconocimiento.fotos_urls)
            if isinstance(fotos_list, list):
                for i, url in enumerate(fotos_list[:2], 1):  # Solo las primeras 2 fotos
                    print(f"   📸 Foto {i}: {url}")
                    
        except (json.JSONDecodeError, TypeError):
            print(f"❌ Error en reconocimiento ID {reconocimiento.id}")

def main():
    print("=" * 80)
    print("🔧 CORRECTOR DE URLs DE DROPBOX PARA FRONTEND")
    print("=" * 80)
    
    print("\n1. Mostrando URLs actuales...")
    mostrar_urls_actuales()
    
    print("\n2. Corrigiendo URLs...")
    corregir_urls_reconocimiento()
    
    print("\n3. Verificando URLs corregidas...")
    mostrar_urls_actuales()
    
    print("\n" + "=" * 80)
    print("✅ CORRECCIÓN COMPLETADA")
    print("=" * 80)
    print("Ahora las URLs deberían mostrarse correctamente en el frontend")
    print("Formato correcto: https://dl.dropboxusercontent.com/scl/fi/ID/filename")

if __name__ == '__main__':
    main()