#!/usr/bin/env python
"""
Script de prueba para el endpoint de registro de inquilinos
Verifica que el error de 'tipo_usuario' esté corregido
"""
import os
import sys
import django
import requests
import json
from datetime import datetime, date

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

BASE_URL = "http://localhost:8000"

def obtener_token_propietario():
    """Obtener token JWT de un propietario"""
    try:
        login_url = f"{BASE_URL}/api/auth/login/"
        # Usar credenciales de un propietario existente
        propietario_creds = {
            "email": "propietario@test.com",  # Cambiar por email real
            "password": "test123"  # Cambiar por password real
        }
        
        response = requests.post(login_url, json=propietario_creds)
        print(f"🔍 Login response status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            token = data.get('access', '')
            print(f"✅ Token obtenido exitosamente")
            return token
        else:
            print(f"❌ Error obteniendo token: {response.status_code}")
            print(f"Response: {response.text}")
            return None
    except Exception as e:
        print(f"❌ Error conectando: {e}")
        return None

def test_registro_inquilino(token):
    """Probar el registro de inquilino con el payload original"""
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    # Payload exacto del frontend que estaba fallando
    payload = {
        "nombre": "lara",
        "apellido": "mendoza", 
        "documento_identidad": "9876543211",
        "fecha_nacimiento": "2000-01-01",
        "telefono": "59171000000",
        "email": "lara@gmail.com",
        "genero": "M",
        "fecha_inicio": "2025-09-02",
        "fecha_fin": "2026-01-01", 
        "monto_alquiler": 2000,
        "observaciones": "",
        "vivienda_id": 15
    }
    
    print("\n🧪 PROBANDO REGISTRO DE INQUILINO")
    print("=" * 50)
    print(f"📤 Payload enviado:")
    print(json.dumps(payload, indent=2, ensure_ascii=False))
    
    url = f"{BASE_URL}/api/authz/propietarios/panel/inquilinos/"
    print(f"🌐 URL: {url}")
    
    try:
        response = requests.post(url, headers=headers, json=payload)
        print(f"\n📥 Response Status: {response.status_code}")
        
        try:
            response_data = response.json()
            print(f"📄 Response Data:")
            print(json.dumps(response_data, indent=2, ensure_ascii=False))
        except:
            print(f"📄 Response Text: {response.text}")
        
        if response.status_code == 201:
            print(f"\n✅ ÉXITO: Inquilino registrado correctamente")
            return True
        elif response.status_code == 500:
            print(f"\n❌ ERROR 500: Aún hay errores del servidor")
            return False
        elif response.status_code == 400:
            print(f"\n⚠️ ERROR 400: Error de validación")
            return False
        elif response.status_code == 403:
            print(f"\n🔒 ERROR 403: Sin permisos de propietario")
            return False
        else:
            print(f"\n❓ ERROR {response.status_code}: Código inesperado")
            return False
            
    except Exception as e:
        print(f"\n💥 EXCEPCIÓN: {str(e)}")
        return False

def test_con_admin():
    """Probar con credenciales de admin si no hay propietario disponible"""
    try:
        login_url = f"{BASE_URL}/api/auth/login/"
        admin_creds = {
            "email": "admin@residencial.com",
            "password": "admin123"
        }
        
        response = requests.post(login_url, json=admin_creds)
        print(f"🔍 Admin login response status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            token = data.get('access', '')
            print(f"✅ Token de admin obtenido")
            
            # Probar endpoint con admin (debería dar 403 - sin permisos de propietario)
            return test_registro_inquilino(token)
        
        return False
    except Exception as e:
        print(f"❌ Error con admin: {e}")
        return False

def main():
    print("🏠" * 30)
    print("🧪 PRUEBA DE CORRECCIÓN - REGISTRO DE INQUILINOS")
    print("🎯 Objetivo: Verificar que se corrigió el error 'tipo_usuario'")
    print("🏠" * 30)
    
    # Intentar con propietario primero
    token = obtener_token_propietario()
    
    if token:
        print(f"✅ Usando token de propietario")
        success = test_registro_inquilino(token)
    else:
        print(f"⚠️ No se pudo obtener token de propietario, probando con admin...")
        success = test_con_admin()
    
    print("\n" + "=" * 60)
    
    if success:
        print("✅ PRUEBA EXITOSA")
        print("   - El error 'tipo_usuario' fue corregido")
        print("   - El endpoint está funcionando correctamente")
    else:
        print("❌ PRUEBA FALLÓ")
        print("   - Revisar logs del servidor para más detalles")
        print("   - Verificar que el servidor esté corriendo")
        print("   - Verificar credenciales de propietario")
    
    print("=" * 60)

if __name__ == "__main__":
    main()