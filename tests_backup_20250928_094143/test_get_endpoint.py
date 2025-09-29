#!/usr/bin/env python3
"""
Script para verificar si el endpoint GET funciona correctamente
"""

import requests
import json

def test_get_endpoint():
    print("🧪 VERIFICACIÓN GET ENDPOINT")
    print("=" * 30)
    
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
    
    # Hacer GET
    url = "http://localhost:8000/api/authz/usuarios/36/"
    
    print(f"🔄 Enviando GET a: {url}")
    
    response = requests.get(url, headers=headers)
    
    print(f"\n📊 RESPUESTA GET:")
    print(f"   Status: {response.status_code}")
    if if response is not None:
     response.status_code == 200:
        print(f"   Body: {json.dumps(response.json(), indent=2, ensure_ascii=False)}")
    else:
        print(f"   Error: {response.text}")

if __name__ == "__main__":
    test_get_endpoint()