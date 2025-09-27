#!/usr/bin/env python3
"""
Script simple para hacer solicitud PATCH directa y verificar logs
"""

import requests
import json

def test_direct_patch():
    print("🧪 SOLICITUD PATCH DIRECTA")
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
    
    # Hacer PATCH
    patch_data = {"roles": [3]}
    url = "http://localhost:8000/api/authz/usuarios/36/"
    
    print(f"🔄 Enviando PATCH a: {url}")
    print(f"   Headers: {headers}")
    print(f"   Data: {patch_data}")
    
    response = requests.patch(url, json=patch_data, headers=headers)
    
    print(f"\n📊 RESPUESTA:")
    print(f"   Status: {response.status_code}")
    print(f"   Body: {json.dumps(response.json(), indent=2, ensure_ascii=False)}")

if __name__ == "__main__":
    test_direct_patch()