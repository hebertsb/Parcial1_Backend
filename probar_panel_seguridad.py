#!/usr/bin/env python3
"""
Script para probar los endpoints del panel de seguridad
"""

import os
import sys
import django

# Configurar Django
sys.path.append('.')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from django.test import Client
import json

# Credenciales de usuario de seguridad
EMAIL_SEGURIDAD = "seguridad@facial.com"
PASSWORD_SEGURIDAD = "admin123"

def probar_endpoints_seguridad():
    """Probar todos los endpoints del panel de seguridad"""
    
    print("🛡️ PROBANDO ENDPOINTS DEL PANEL DE SEGURIDAD")
    print("=" * 60)
    
    # Crear cliente de prueba
    client = Client()
    
    # 1. Login con usuario de seguridad
    print("🔐 1. LOGIN SEGURIDAD...")
    
    login_response = client.post('/api/authz/login/', 
                                data=json.dumps({
                                    'email': EMAIL_SEGURIDAD,
                                    'password': PASSWORD_SEGURIDAD
                                }), 
                                content_type='application/json')
    
    print(f"   Status: {login_response.status_code}")
    
    if login_response.status_code != 200:
        print(f"   ❌ Error en login: {login_response.content.decode()}")
        return False
    
    # Obtener token
    login_data = login_response.json()
    token = login_data.get('access')
    print(f"   ✅ Login exitoso - Token obtenido")
    
    # Headers para requests autenticados
    auth_headers = {'HTTP_AUTHORIZATION': f'Bearer {token}'}
    
    # 2. Listar usuarios con fotos
    print("\n👥 2. LISTAR USUARIOS CON FOTOS...")
    
    usuarios_response = client.get('/api/authz/seguridad/usuarios-con-fotos/', **auth_headers)
    print(f"   Status: {usuarios_response.status_code}")
    
    if usuarios_response.status_code == 200:
        usuarios_data = usuarios_response.json()
        print("   ✅ Usuarios obtenidos:")
        data = usuarios_data.get('data', {})
        total_usuarios = data.get('total_usuarios', 0)
        usuarios = data.get('usuarios', [])
        
        print(f"      • Total usuarios con fotos: {total_usuarios}")
        
        if usuarios:
            print("      • Usuarios encontrados:")
            for i, usuario in enumerate(usuarios[:3], 1):  # Mostrar solo los primeros 3
                print(f"        {i}. {usuario.get('nombre_completo')} - {usuario.get('unidad_residencial')}")
                print(f"           Fotos: {usuario.get('total_fotos')}")
        else:
            print("      • No se encontraron usuarios con fotos")
    else:
        print(f"   ❌ Error: {usuarios_response.content.decode()}")
    
    # 3. Estadísticas del sistema
    print("\n📊 3. ESTADÍSTICAS DEL SISTEMA...")
    
    stats_response = client.get('/api/authz/seguridad/estadisticas-reconocimiento/', **auth_headers)
    print(f"   Status: {stats_response.status_code}")
    
    if stats_response.status_code == 200:
        stats_data = stats_response.json()
        print("   ✅ Estadísticas obtenidas:")
        data = stats_data.get('data', {})
        totales = data.get('totales', {})
        porcentajes = data.get('porcentajes', {})
        
        print(f"      • Copropietarios activos: {totales.get('copropietarios_activos')}")
        print(f"      • Usuarios con reconocimiento: {totales.get('usuarios_con_reconocimiento')}")
        print(f"      • Usuarios con fotos: {totales.get('usuarios_con_fotos')}")
        print(f"      • Total fotos en sistema: {totales.get('total_fotos_sistema')}")
        print(f"      • Cobertura reconocimiento: {porcentajes.get('cobertura_reconocimiento')}%")
    else:
        print(f"   ❌ Error: {stats_response.content.decode()}")
    
    # 4. Detalle de usuario específico (si hay usuarios)
    if usuarios_response.status_code == 200 and usuarios:
        primer_usuario = usuarios[0]
        copropietario_id = primer_usuario.get('copropietario_id')
        
        print(f"\n🔍 4. DETALLE DE USUARIO (ID: {copropietario_id})...")
        
        detalle_response = client.get(f'/api/authz/seguridad/usuario-fotos/{copropietario_id}/', **auth_headers)
        print(f"   Status: {detalle_response.status_code}")
        
        if detalle_response.status_code == 200:
            detalle_data = detalle_response.json()
            print("   ✅ Detalle obtenido:")
            data = detalle_data.get('data', {})
            copropietario = data.get('copropietario', {})
            reconocimiento = data.get('reconocimiento', {})
            
            print(f"      • Nombre: {copropietario.get('nombre_completo')}")
            print(f"      • Documento: {copropietario.get('documento')}")
            print(f"      • Unidad: {copropietario.get('unidad_residencial')}")
            print(f"      • Total fotos: {reconocimiento.get('total_fotos')}")
            
            fotos_urls = reconocimiento.get('fotos_urls', [])
            if fotos_urls:
                print("      • URLs de fotos:")
                for i, url in enumerate(fotos_urls[:2], 1):  # Mostrar solo las primeras 2
                    print(f"        {i}. {url[:60]}...")
        else:
            print(f"   ❌ Error: {detalle_response.content.decode()}")
    
    # Resumen
    print("\n" + "=" * 60)
    print("📊 RESUMEN DE PRUEBAS:")
    print("=" * 60)
    
    endpoints = [
        ("Login Seguridad", login_response.status_code == 200),
        ("Listar Usuarios con Fotos", usuarios_response.status_code == 200),
        ("Estadísticas Sistema", stats_response.status_code == 200),
    ]
    
    if usuarios_response.status_code == 200 and usuarios:
        endpoints.append(("Detalle Usuario", detalle_response.status_code == 200))
    
    exitosos = 0
    for nombre, resultado in endpoints:
        estado = "✅ EXITOSO" if resultado else "❌ FALLÓ"
        print(f"{nombre:<25}: {estado}")
        if resultado:
            exitosos += 1
    
    print(f"\nResultado final: {exitosos}/{len(endpoints)} endpoints funcionando")
    
    if exitosos == len(endpoints):
        print("\n🎉 ¡TODOS LOS ENDPOINTS DEL PANEL DE SEGURIDAD FUNCIONAN!")
        print("✅ El frontend puede usar estos endpoints para mostrar usuarios con fotos")
    else:
        print(f"\n⚠️ Hay {len(endpoints) - exitosos} endpoints con problemas")
    
    return exitosos == len(endpoints)

if __name__ == "__main__":
    try:
        resultado = probar_endpoints_seguridad()
        
        if resultado:
            print("\n🚀 ENDPOINTS LISTOS PARA EL FRONTEND:")
            print("=" * 50)
            print("✅ Panel de seguridad implementado completamente")
            print("✅ Autenticación JWT operativa")
            print("✅ Integración con base de datos funcionando")
            print("\n🔗 URLs disponibles para el frontend:")
            print("   • GET  /api/authz/seguridad/usuarios-con-fotos/")
            print("   • GET  /api/authz/seguridad/usuario-fotos/<id>/")
            print("   • GET  /api/authz/seguridad/estadisticas-reconocimiento/")
            
    except Exception as e:
        print(f"\n💥 Error: {e}")
        import traceback
        traceback.print_exc()