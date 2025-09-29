#!/usr/bin/env python
"""
Prueba del endpoint CORREGIDO con usuarios que tienen rol Propietario
"""
import requests
import json

def probar_endpoint_corregido():
    print("🎯 PRUEBA ENDPOINT CORREGIDO - PROPIETARIOS")
    print("=" * 60)
    
    base_url = "http://localhost:8000"
    endpoint = "/api/authz/reconocimiento/fotos/"
    
    # Usuarios con rol Propietario para probar
    usuarios_propietarios = [
        {"id": 3, "email": "maria.gonzalez@facial.com", "nombre": "María Elena"},
        {"id": 6, "email": "laura.gonzález10@test.com", "nombre": "Laura"},
        {"id": 7, "email": "hebertsuarezb@gmail.com", "nombre": "Diego"},
        {"id": 8, "email": "tito@gmail.com", "nombre": "Tito"}
    ]
    
    for usuario in usuarios_propietarios:
        print(f"\n🧪 PROBANDO USUARIO ID {usuario['id']}: {usuario['nombre']}")
        print("-" * 50)
        
        # 1. Obtener token para este usuario
        login_url = f"{base_url}/api/authz/login/"
        credentials = {"email": usuario["email"], "password": "test123"}  # Usar password genérico
        
        try:
            login_response = requests.post(login_url, json=credentials)
            if login_response.status_code != 200:
                print(f"   ❌ Login falló: {login_response.status_code}")
                continue
            
            token = login_response.json().get('access')
            headers = {'Authorization': f'Bearer {token}'}
            print(f"   ✅ Token obtenido")
            
            # 2. Probar endpoint
            data = {'usuario_id': str(usuario['id'])}
            files = {'fotos': ('test.jpg', b'fake_image_data', 'image/jpeg')}
            
            response = requests.post(f"{base_url}{endpoint}", headers=headers, data=data, files=files)
            
            print(f"   Status: {response.status_code}")
            
            if response.status_code == 200:
                print("   🎉 ¡ÉXITO! Endpoint funcionando con usuario propietario")
                try:
                    result = response.json()
                    print(f"   Usuario: {result['data']['propietario_nombre']}")
                    print(f"   Fotos subidas: {result['data']['total_fotos']}")
                except:
                    print(f"   Respuesta: {response.text[:200]}...")
                    
            elif response.status_code == 400:
                print("   ⚠️ Error de validación")
                try:
                    error = response.json()
                    print(f"   Error: {error.get('error', 'Sin detalles')}")
                except:
                    print(f"   Error: {response.text}")
                    
            elif response.status_code == 403:
                print("   ❌ Sin permisos - verificar rol")
                
            elif response.status_code == 404:
                print("   ❌ Usuario/persona no encontrado")
                
            else:
                print(f"   ⚠️ Código inesperado: {response.text}")
                
        except Exception as e:
            print(f"   ❌ Error de conexión: {e}")

def probar_endpoint_estado():
    print(f"\n🔍 PROBANDO ENDPOINT DE ESTADO")
    print("=" * 60)
    
    base_url = "http://localhost:8000"
    endpoint = "/api/authz/reconocimiento/estado/"
    
    # Usar un usuario propietario conocido
    login_url = f"{base_url}/api/authz/login/"
    credentials = {"email": "maria.gonzalez@facial.com", "password": "test123"}
    
    try:
        login_response = requests.post(login_url, json=credentials)
        if login_response.status_code == 200:
            token = login_response.json().get('access')
            headers = {'Authorization': f'Bearer {token}'}
            
            response = requests.get(f"{base_url}{endpoint}", headers=headers)
            print(f"Status: {response.status_code}")
            
            if response.status_code == 200:
                result = response.json()
                print(f"✅ Estado obtenido:")
                print(f"   Tiene reconocimiento: {result['data']['tiene_reconocimiento']}")
                if result['data']['tiene_reconocimiento']:
                    print(f"   Total fotos: {result['data']['total_fotos']}")
            else:
                print(f"❌ Error: {response.text}")
                
    except Exception as e:
        print(f"❌ Error: {e}")

def mostrar_resumen():
    print(f"\n📋 RESUMEN DE LA CORRECCIÓN")
    print("=" * 60)
    
    print("✅ PROBLEMA SOLUCIONADO:")
    print("   - Endpoint original buscaba en tabla 'Copropietarios'")
    print("   - Sistema real usa usuarios con rol 'Propietario'")
    print("   - Nuevo endpoint corregido busca rol 'Propietario'")
    print()
    
    print("🎯 USUARIOS VÁLIDOS:")
    print("   - ID 3: maria.gonzalez@facial.com (Propietario)")
    print("   - ID 6: laura.gonzález10@test.com (Propietario)")  
    print("   - ID 7: hebertsuarezb@gmail.com (Propietario)")
    print("   - ID 8: tito@gmail.com (Propietario)")
    print()
    
    print("📡 ENDPOINT FINAL:")
    print("   URL: POST /api/authz/reconocimiento/fotos/")
    print("   Busca: Usuarios con rol 'Propietario' + persona asociada")
    print("   Compatible con: Flujo de registro y aprobación de solicitudes")

if __name__ == "__main__":
    probar_endpoint_corregido()
    probar_endpoint_estado()
    mostrar_resumen()