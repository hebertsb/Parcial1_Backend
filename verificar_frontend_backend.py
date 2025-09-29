#!/usr/bin/env python3
"""
VERIFICACIÓN COMPLETA ENDPOINTS FRONTEND/BACKEND
===============================================
Verifica que todos los endpoints que espera el frontend estén funcionando
"""

import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

import requests
import json
from authz.models import Usuario
from seguridad.models import Copropietarios, ReconocimientoFacial

def main():
    print("🔍 VERIFICACIÓN ENDPOINTS FRONTEND/BACKEND")
    print("=" * 50)
    
    # Credenciales para pruebas
    print("\n1. 📋 PREPARANDO USUARIOS DE PRUEBA")
    
    # Verificar usuario lara (ID 13 según frontend)
    try:
        lara_user = Usuario.objects.get(email='lara@gmail.com')
        lara_coprop = Copropietarios.objects.get(usuario_sistema=lara_user)
        lara_reconoc = ReconocimientoFacial.objects.get(copropietario=lara_coprop)
        print(f"   ✅ Usuario lara: User ID {lara_user.id}, Reconocimiento ID {lara_reconoc.id}")
    except Exception as e:
        print(f"   ❌ Error con usuario lara: {e}")
        return
    
    # Login como lara (propietario)
    print("\n2. 🔐 LOGIN COMO PROPIETARIO (lara)")
    try:
        login_response = requests.post('http://localhost:8000/api/authz/login/', {
            'email': 'lara@gmail.com',
            'password': 'lara123'
        })
        
        if login_response.status_code == 200:
            lara_token = login_response.json()['access']
            print("   ✅ Login lara exitoso")
        else:
            print(f"   ❌ Error login lara: {login_response.status_code}")
            return
    except Exception as e:
        print(f"   ❌ Error login lara: {e}")
        return
    
    # Login como seguridad
    print("\n3. 🔐 LOGIN COMO SEGURIDAD")
    try:
        login_response = requests.post('http://localhost:8000/api/authz/login/', {
            'email': 'seguridad@facial.com',
            'password': 'seguridad123'
        })
        
        if login_response.status_code == 200:
            security_token = login_response.json()['access']
            print("   ✅ Login seguridad exitoso")
        else:
            print(f"   ❌ Error login seguridad: {login_response.status_code}")
            return
    except Exception as e:
        print(f"   ❌ Error login seguridad: {e}")
        return
    
    # Probar endpoints según frontend
    print("\n4. 🔌 PROBANDO ENDPOINTS QUE ESPERA EL FRONTEND")
    
    endpoints_frontend = [
        {
            'name': 'GET Fotos Usuario Lara',
            'method': 'GET',
            'url': f'/api/authz/reconocimiento/fotos/{lara_user.id}/',
            'token': lara_token,
            'expected': 'Debe devolver fotos_urls con URLs de Dropbox'
        },
        {
            'name': 'GET Lista Usuarios con Reconocimiento',
            'method': 'GET', 
            'url': '/api/authz/seguridad/usuarios-reconocimiento/',
            'token': security_token,
            'expected': 'Lista de usuarios con fotos'
        },
        {
            'name': 'GET Fotos desde Seguridad',
            'method': 'GET',
            'url': f'/api/authz/reconocimiento/fotos/{lara_reconoc.id}/',
            'token': security_token,
            'expected': 'Fotos del usuario específico'
        }
    ]
    
    for endpoint in endpoints_frontend:
        print(f"\n   🔍 {endpoint['name']}")
        
        try:
            headers = {'Authorization': f'Bearer {endpoint["token"]}'}
            response = requests.get(f'http://localhost:8000{endpoint["url"]}', headers=headers)
            
            print(f"      URL: {endpoint['url']}")
            print(f"      Status: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                print(f"      ✅ Respuesta exitosa")
                
                # Análisis específico según endpoint
                if 'fotos' in endpoint['url']:
                    success = data.get('success', False)
                    fotos_data = data.get('data', {})
                    fotos_urls = fotos_data.get('fotos_urls', [])
                    
                    print(f"      Success: {success}")
                    print(f"      Fotos encontradas: {len(fotos_urls)}")
                    
                    if fotos_urls:
                        print(f"      📸 Primera foto: {fotos_urls[0][:50]}...")
                        is_dropbox = 'dropbox' in fotos_urls[0].lower()
                        print(f"      🔗 Es URL de Dropbox: {'✅' if is_dropbox else '❌'}")
                    else:
                        print("      ⚠️  No se encontraron fotos_urls")
                
                elif 'usuarios-reconocimiento' in endpoint['url']:
                    usuarios = data.get('data', [])
                    print(f"      👥 Usuarios encontrados: {len(usuarios)}")
                    
                    if usuarios:
                        lara_found = any(u.get('email') == 'lara@gmail.com' for u in usuarios)
                        print(f"      🔍 Lara encontrada: {'✅' if lara_found else '❌'}")
                        
                        primer_usuario = usuarios[0]
                        print(f"      📋 Primer usuario: {primer_usuario.get('email')}")
                        print(f"      📸 Tiene fotos: {primer_usuario.get('tiene_fotos', False)}")
                
            elif response.status_code == 404:
                print(f"      ❌ Endpoint no encontrado (404)")
            else:
                print(f"      ❌ Error: {response.status_code}")
                print(f"      Respuesta: {response.text[:100]}...")
                
        except Exception as e:
            print(f"      ❌ Error de conexión: {e}")
    
    # Resumen final
    print("\n\n5. 📊 RESUMEN PARA FRONTEND")
    print("   " + "="*40)
    
    print(f"   👤 Usuario lara ID: {lara_user.id} (para GET fotos)")
    print(f"   📸 ReconocimientoFacial ID: {lara_reconoc.id}")
    print(f"   🔑 Credenciales lara: lara@gmail.com / lara123")
    print(f"   🔑 Credenciales seguridad: seguridad@facial.com / seguridad123")
    
    print("\n   📱 ENDPOINTS PARA EL FRONTEND:")
    print(f"      GET /api/authz/reconocimiento/fotos/{lara_user.id}/")
    print(f"      GET /api/authz/seguridad/usuarios-reconocimiento/")
    print(f"      POST /api/authz/reconocimiento/fotos/ (subir)")
    
    print("\n   🎯 TESTING EN CONSOLE NAVEGADOR:")
    print("      const response = await fetch('/api/authz/reconocimiento/fotos/13/', {")
    print("        headers: { 'Authorization': `Bearer ${token}` }")
    print("      });")
    print("      console.log(await response.json());")

if __name__ == "__main__":
    main()