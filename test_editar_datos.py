#!/usr/bin/env python3
"""
Script para probar el endpoint PUT /api/authz/usuarios/{id}/editar-datos/
que maneja datos personales del usuario
"""

import requests
import json

def test_editar_datos_admin():
    print("🧪 PRUEBA EDITAR DATOS ADMIN")
    print("=" * 40)
    
    # Hacer login primero para obtener token
    login_data = {
        "email": "admin@test.com",
        "password": "admin123"
    }
    
    login_response = requests.post("http://localhost:8000/api/authz/login/", json=login_data)
    if login_response.status_code != 200:
        print(f"❌ Error en login: {login_response.status_code}")
        return
    
    token = login_response.json()["access"]
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    print(f"✅ Token obtenido")
    
    # Probar editar datos personales
    data = {
        "nombres": "Usuario Actualizado",
        "apellidos": "Apellidos Nuevos",
        "telefono": "70123456",
        "genero": "Masculino"
    }
    
    url = "http://localhost:8000/api/authz/usuarios/36/editar-datos/"
    
    print(f"🔄 Enviando PUT a: {url}")
    print(f"   Data: {data}")
    
    response = requests.put(url, json=data, headers=headers)
    
    print(f"\n📊 RESPUESTA:")
    print(f"   Status: {response.status_code}")
    if response.status_code == 200:
        print(f"   Body: {json.dumps(response.json(), indent=2, ensure_ascii=False)}")
        print("✅ ¡ÉXITO! El endpoint editar-datos funciona correctamente")
    else:
        print(f"   Error: {response.text}")

if __name__ == "__main__":
    test_editar_datos_admin()