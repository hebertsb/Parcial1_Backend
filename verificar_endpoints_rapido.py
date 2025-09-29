#!/usr/bin/env python3
"""
PRUEBA RÁPIDA DEL ENDPOINT DE SEGURIDAD
========================================
"""

import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

import requests

def main():
    print("🔌 VERIFICACIÓN ENDPOINTS SEGURIDAD")
    print("=" * 40)
    
    try:
        # Login como seguridad
        print("1. 🔐 Login de seguridad...")
        login_response = requests.post('http://localhost:8000/api/authz/login/', {
            'email': 'seguridad@facial.com',
            'password': 'seguridad123'
        })
        
        if login_response.status_code == 200:
            token = login_response.json()['access']
            headers = {'Authorization': f'Bearer {token}'}
            print("   ✅ Login exitoso")
            
            # Probar diferentes endpoints de reconocimiento
            endpoints = [
                '/api/authz/reconocimiento/',
                '/api/seguridad/reconocimiento-facial/',
                '/api/authz/reconocimiento/fotos/8/',
            ]
            
            for endpoint in endpoints:
                print(f"\n2. 🔍 Probando: {endpoint}")
                response = requests.get(f'http://localhost:8000{endpoint}', headers=headers)
                print(f"   Status: {response.status_code}")
                
                if response.status_code == 200:
                    print("   ✅ Endpoint funcional")
                elif response.status_code == 404:
                    print("   ⚠️  Endpoint no encontrado")
                else:
                    print(f"   ❌ Error: {response.status_code}")
        else:
            print(f"   ❌ Error en login: {login_response.status_code}")
            
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    main()