#!/usr/bin/env python3
"""
Script para probar login del usuario de seguridad
"""

import requests
import json

# Configuración
BASE_URL = "http://127.0.0.1:8000"

# Diferentes combinaciones de credenciales para probar
credenciales_a_probar = [
    {"email": "seguridad@facial.com", "password": "Admin123456*"},
    {"email": "seguridad@facial.com", "password": "seguridad123"},
    {"email": "seguridad@facial.com", "password": "admin123"},
    {"email": "seguridad@facial.com", "password": "123456"},
]

def probar_login(credenciales):
    """Probar login con diferentes credenciales"""
    try:
        url = f"{BASE_URL}/api/auth/login/"
        response = requests.post(url, json=credenciales)
        
        print(f"🔐 Probando: {credenciales['email']} / {credenciales['password']}")
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            token = data.get('access', data.get('token'))
            print(f"✅ LOGIN EXITOSO! Token: {token[:20] if token else 'No token'}...")
            return token
        else:
            print(f"❌ Error: {response.text}")
            return None
    except Exception as e:
        print(f"❌ Exception: {e}")
        return None

def main():
    print("🚀 PROBANDO LOGIN DEL USUARIO DE SEGURIDAD")
    print("=" * 50)
    
    for credenciales in credenciales_a_probar:
        token = probar_login(credenciales)
        if token:
            print(f"\n🎉 ¡CREDENCIALES CORRECTAS ENCONTRADAS!")
            print(f"Email: {credenciales['email']}")
            print(f"Password: {credenciales['password']}")
            return token
        print()
    
    print("❌ Ninguna combinación de credenciales funcionó")
    print("💡 Sugerencia: Resetear la contraseña del usuario")
    return None

if __name__ == "__main__":
    main()