#!/usr/bin/env python
"""
Script para verificar el estado de implementación de endpoints de APIs
Ejecutar: python verificar_endpoints_implementados.py
"""

import os
import sys
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from django.urls import get_resolver
from django.conf import settings
from authz.models import Usuario, Rol
from core.models.propiedades_residentes import Persona, Vivienda, Propiedad

def obtener_todas_las_urls():
    """Obtiene todas las URLs registradas en Django"""
    resolver = get_resolver()
    urls = []
    
    def extract_urls(url_patterns, prefix=''):
        for pattern in url_patterns:
            if hasattr(pattern, 'url_patterns'):
                # Es un include()
                new_prefix = prefix + str(pattern.pattern)
                extract_urls(pattern.url_patterns, new_prefix)
            else:
                # Es una URL individual
                if pattern.name:
                    full_pattern = prefix + str(pattern.pattern)
                    urls.append({
                        'pattern': full_pattern,
                        'name': pattern.name,
                        'view': str(pattern.callback)
                    })
    
    extract_urls(resolver.url_patterns)
    return urls

def verificar_modelos():
    """Verifica el estado de los modelos principales"""
    print("📊 ESTADO DE LOS MODELOS:")
    print("=" * 50)
    
    try:
        # Verificar Usuarios
        usuarios = Usuario.objects.all()
        print(f"✅ Usuarios en DB: {usuarios.count()}")
        
        # Contar por roles
        propietarios = Usuario.objects.filter(roles__nombre='Propietario')
        inquilinos = Usuario.objects.filter(roles__nombre='Inquilino')
        admins = Usuario.objects.filter(roles__nombre='Administrador')
        
        print(f"   - Propietarios: {propietarios.count()}")
        print(f"   - Inquilinos: {inquilinos.count()}")
        print(f"   - Administradores: {admins.count()}")
        
        # Verificar Personas
        personas = Persona.objects.all()
        print(f"✅ Personas en DB: {personas.count()}")
        
        # Verificar Viviendas
        viviendas = Vivienda.objects.all()
        print(f"✅ Viviendas en DB: {viviendas.count()}")
        
        # Verificar Propiedades
        propiedades = Propiedad.objects.all()
        print(f"✅ Propiedades en DB: {propiedades.count()}")
        
    except Exception as e:
        print(f"❌ Error verificando modelos: {e}")

def verificar_endpoints_criticos():
    """Verifica si los endpoints críticos están implementados"""
    print("\n🌐 ENDPOINTS CRÍTICOS:")
    print("=" * 50)
    
    urls = obtener_todas_las_urls()
    
    endpoints_criticos = [
        '/api/personas/',
        '/api/viviendas/',
        '/api/propiedades/',
        'authz/propietarios/panel/menu/',
        'authz/propietarios/panel/familiares/',
        'authz/propietarios/panel/inquilinos/',
        'auth/login/',
        'auth/refresh/'
    ]
    
    for endpoint in endpoints_criticos:
        encontrado = False
        for url in urls:
            if endpoint in url['pattern'] or endpoint in url['name']:
                print(f"✅ {endpoint} - IMPLEMENTADO")
                print(f"   Pattern: {url['pattern']}")
                print(f"   View: {url['view']}")
                encontrado = True
                break
        
        if not encontrado:
            print(f"❌ {endpoint} - NO ENCONTRADO")

def verificar_configuracion_cors():
    """Verifica la configuración de CORS"""
    print("\n🔧 CONFIGURACIÓN CORS:")
    print("=" * 50)
    
    try:
        if hasattr(settings, 'CORS_ALLOWED_ORIGINS'):
            print("✅ CORS_ALLOWED_ORIGINS configurado:")
            for origin in settings.CORS_ALLOWED_ORIGINS:
                print(f"   - {origin}")
        else:
            print("❌ CORS_ALLOWED_ORIGINS no configurado")
        
        if hasattr(settings, 'CORS_ALLOW_ALL_ORIGINS'):
            if settings.CORS_ALLOW_ALL_ORIGINS:
                print("⚠️  CORS_ALLOW_ALL_ORIGINS = True (no recomendado para producción)")
            else:
                print("✅ CORS_ALLOW_ALL_ORIGINS = False")
        
        if hasattr(settings, 'CORS_ALLOW_CREDENTIALS'):
            print(f"✅ CORS_ALLOW_CREDENTIALS = {settings.CORS_ALLOW_CREDENTIALS}")
        
    except Exception as e:
        print(f"❌ Error verificando CORS: {e}")

def verificar_jwt_configuracion():
    """Verifica la configuración JWT"""
    print("\n🔐 CONFIGURACIÓN JWT:")
    print("=" * 50)
    
    try:
        if hasattr(settings, 'SIMPLE_JWT'):
            jwt_config = settings.SIMPLE_JWT
            print("✅ SIMPLE_JWT configurado:")
            print(f"   - ACCESS_TOKEN_LIFETIME: {jwt_config.get('ACCESS_TOKEN_LIFETIME')}")
            print(f"   - REFRESH_TOKEN_LIFETIME: {jwt_config.get('REFRESH_TOKEN_LIFETIME')}")
            print(f"   - ALGORITHM: {jwt_config.get('ALGORITHM')}")
        else:
            print("❌ SIMPLE_JWT no configurado")
    except Exception as e:
        print(f"❌ Error verificando JWT: {e}")

def generar_ejemplos_usuarios():
    """Genera ejemplos de usuarios existentes"""
    print("\n👥 USUARIOS DE PRUEBA DISPONIBLES:")
    print("=" * 50)
    
    try:
        # Obtener algunos usuarios ejemplo
        usuarios = Usuario.objects.all()[:5]
        
        for usuario in usuarios:
            roles = ", ".join([rol.nombre for rol in usuario.roles.all()])
            print(f"📧 Email: {usuario.email}")
            print(f"   Roles: {roles}")
            print(f"   Activo: {'Sí' if usuario.is_active else 'No'}")
            print()
        
        if usuarios.count() == 0:
            print("❌ No hay usuarios en la base de datos")
            print("💡 Ejecuta: python manage.py createsuperuser")
            
    except Exception as e:
        print(f"❌ Error obteniendo usuarios: {e}")

def verificar_servidor():
    """Verifica configuración del servidor"""
    print("\n🚀 CONFIGURACIÓN DEL SERVIDOR:")
    print("=" * 50)
    
    try:
        print(f"✅ DEBUG = {settings.DEBUG}")
        print(f"✅ ALLOWED_HOSTS = {settings.ALLOWED_HOSTS}")
        
        if hasattr(settings, 'DATABASES'):
            db_config = settings.DATABASES['default']
            print(f"✅ BASE DE DATOS: {db_config['ENGINE']}")
            if 'sqlite3' in db_config['ENGINE']:
                print(f"   - Archivo: {db_config['NAME']}")
        
    except Exception as e:
        print(f"❌ Error verificando servidor: {e}")

def main():
    """Función principal"""
    print("🔍 VERIFICACIÓN COMPLETA DE APIS - BACKEND DJANGO")
    print("=" * 60)
    print(f"📅 Fecha: 24 de septiembre de 2025")
    print(f"🏠 Proyecto: Sistema de Gestión de Condominios")
    print("=" * 60)
    
    # Ejecutar todas las verificaciones
    verificar_modelos()
    verificar_endpoints_criticos()
    verificar_configuracion_cors()
    verificar_jwt_configuracion()
    generar_ejemplos_usuarios()
    verificar_servidor()
    
    print("\n" + "=" * 60)
    print("✅ VERIFICACIÓN COMPLETADA")
    print("=" * 60)
    print("\n💡 RESPUESTAS A LAS PREGUNTAS DEL FRONTEND:")
    print("1. Servidor corriendo en: http://127.0.0.1:8000")
    print("2. BASE_URL correcta: http://127.0.0.1:8000/api")
    print("3. Autenticación: JWT Bearer Token en header 'Authorization'")
    print("4. Credenciales admin: admin@facial.com / admin123")
    print("5. Endpoints implementados: Ver lista arriba ↑")
    print("\n📋 Para probar endpoints:")
    print("   python manage.py runserver")
    print("   curl -X POST http://127.0.0.1:8000/auth/login/ -d '{\"email\":\"admin@facial.com\",\"password\":\"admin123\"}' -H 'Content-Type: application/json'")

if __name__ == "__main__":
    main()