# 🧪 PRUEBA INMEDIATA DEL ENDPOINT CORREGIDO

import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

import json
from django.test import RequestFactory
from django.contrib.auth import get_user_model
from authz.models import Usuario

def probar_endpoint_corregido():
    """
    🎯 Probar el endpoint GET corregido directamente
    """
    print("🧪 PRUEBA ENDPOINT GET CORREGIDO")
    print("=" * 40)
    
    try:
        # 1. Configurar request simulado
        factory = RequestFactory()
        
        # 2. Obtener usuario de seguridad para autenticación
        User = get_user_model()
        security_user = User.objects.filter(email='seguridad@facial.com').first()
        
        if not security_user:
            print("❌ Usuario de seguridad no encontrado")
            return False
        
        # 3. Crear request GET
        request = factory.get('/api/authz/reconocimiento/fotos/8/')
        request.user = security_user
        
        print(f"✅ Request configurado para usuario ID: 8")
        print(f"✅ Autenticado como: {security_user.email}")
        
        # 4. Llamar al endpoint corregido
        from authz.views_fotos_reconocimiento_corregido import obtener_fotos_reconocimiento_corregido
        
        response = obtener_fotos_reconocimiento_corregido(request, 8)
        
        # 5. Analizar respuesta
        print(f"\n📊 RESPUESTA DEL ENDPOINT:")
        print(f"   - Status Code: {response.status_code}")
        
        if hasattr(response, 'data'):
            data = response.data
            print(f"   - Success: {data.get('success')}")
            
            if data.get('success'):
                fotos_data = data.get('data', {})
                total_fotos = fotos_data.get('total_fotos', 0)
                fotos_urls = fotos_data.get('fotos_urls', [])
                
                print(f"   - Usuario ID: {fotos_data.get('usuario_id')}")
                print(f"   - Email: {fotos_data.get('usuario_email')}")
                print(f"   - Total fotos: {total_fotos}")
                print(f"   - Tiene reconocimiento: {fotos_data.get('tiene_reconocimiento')}")
                
                if fotos_urls:
                    print(f"\n📸 FOTOS ENCONTRADAS:")
                    for i, url in enumerate(fotos_urls):
                        print(f"      {i+1}. {url}")
                    return True
                else:
                    print("   ❌ No se encontraron URLs de fotos")
                    return False
            else:
                error = data.get('error', 'Error desconocido')
                print(f"   ❌ Error: {error}")
                return False
        else:
            print("   ❌ Respuesta sin datos")
            return False
    
    except Exception as e:
        print(f"❌ Error ejecutando prueba: {e}")
        return False

def verificar_comparacion():
    """
    📊 Comparar con el endpoint de la lista de usuarios
    """
    print(f"\n🔗 COMPARACIÓN CON ENDPOINT USUARIOS-RECONOCIMIENTO:")
    
    try:
        import requests
        
        # Login
        login_response = requests.post('http://localhost:8000/api/authz/login/', {
            'email': 'seguridad@facial.com',
            'password': 'admin123'
        })
        
        if login_response.status_code != 200:
            print("❌ Error en login")
            return
        
        token = login_response.json()['access']
        headers = {'Authorization': f'Bearer {token}'}
        
        # Endpoint usuarios-reconocimiento
        usuarios_response = requests.get(
            'http://localhost:8000/api/seguridad/usuarios-reconocimiento/',
            headers=headers
        )
        
        if usuarios_response.status_code == 200:
            usuarios_data = usuarios_response.json()
            
            # Buscar usuario ID 8
            usuario_8 = None
            for user in usuarios_data.get('usuarios', []):
                if user.get('id') == 8:
                    usuario_8 = user
                    break
            
            if usuario_8:
                reconocimiento = usuario_8.get('reconocimiento_facial', {})
                total_fotos = reconocimiento.get('total_fotos', 0)
                print(f"   - Usuarios-reconocimiento: {total_fotos} fotos")
                
                # Endpoint GET fotos
                fotos_response = requests.get(
                    'http://localhost:8000/api/authz/reconocimiento/fotos/8/',
                    headers=headers
                )
                
                if fotos_response.status_code == 200:
                    fotos_data = fotos_response.json()
                    endpoint_fotos = fotos_data.get('data', {}).get('total_fotos', 0)
                    print(f"   - GET fotos: {endpoint_fotos} fotos")
                    
                    if total_fotos == endpoint_fotos and total_fotos > 0:
                        print("   ✅ AMBOS ENDPOINTS COINCIDEN - PROBLEMA RESUELTO!")
                    else:
                        print("   ❌ Los endpoints no coinciden")
                else:
                    print(f"   ❌ Error en endpoint fotos: {fotos_response.status_code}")
            else:
                print("   ❌ Usuario 8 no encontrado en usuarios-reconocimiento")
        else:
            print(f"   ❌ Error en usuarios-reconocimiento: {usuarios_response.status_code}")
    
    except Exception as e:
        print(f"   ❌ Error en comparación: {e}")

if __name__ == "__main__":
    # Ejecutar pruebas
    exito = probar_endpoint_corregido()
    
    if exito:
        verificar_comparacion()
        print(f"\n🎉 ¡ENDPOINT GET CORREGIDO EXITOSAMENTE!")
    else:
        print(f"\n❌ El endpoint aún tiene problemas")