#!/usr/bin/env python
"""
Script para probar directamente las URLs de Django
"""
import os
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from django.urls import reverse, resolve
from django.test import RequestFactory
from authz.views_fotos_reconocimiento import subir_fotos_reconocimiento

def probar_configuracion_urls():
    print("🔧 VERIFICANDO CONFIGURACIÓN DE URLS")
    print("=" * 50)
    
    # 1. Verificar si la URL se puede resolver
    try:
        url = reverse('subir-fotos-reconocimiento')
        print(f"✅ URL reversa encontrada: {url}")
    except Exception as e:
        print(f"❌ Error en URL reversa: {e}")
        return
    
    # 2. Verificar si la URL se puede hacer match
    try:
        path = "/api/authz/usuarios/fotos-reconocimiento/"
        match = resolve(path)
        print(f"✅ URL resolve: {match}")
        print(f"   Función: {match.func}")
        print(f"   Nombre: {match.url_name}")
    except Exception as e:
        print(f"❌ Error en resolve: {e}")
    
    # 3. Probar la función directamente
    try:
        factory = RequestFactory()
        request = factory.post('/test/', {'usuario_id': '8'})
        
        # Simular usuario autenticado
        from authz.models import Usuario
        user = Usuario.objects.first()
        request.user = user
        
        print(f"🧪 PROBANDO FUNCIÓN DIRECTAMENTE")
        response = subir_fotos_reconocimiento(request)
        print(f"   Status: {response.status_code}")
        print(f"   Contenido: {response.data if hasattr(response, 'data') else 'No data'}")
        
    except Exception as e:
        print(f"❌ Error probando función: {e}")

def verificar_importaciones():
    print("\n📦 VERIFICANDO IMPORTACIONES")
    print("=" * 50)
    
    try:
        from authz.views_fotos_reconocimiento import subir_fotos_reconocimiento
        print(f"✅ Función importada: {subir_fotos_reconocimiento}")
        
        # Verificar atributos de función de forma segura
        func_attrs = [attr for attr in dir(subir_fotos_reconocimiento) if not attr.startswith('_')]
        print(f"   Atributos disponibles: {func_attrs}")
        
    except ImportError as e:
        print(f"❌ Error de importación: {e}")

if __name__ == "__main__":
    verificar_importaciones()
    probar_configuracion_urls()