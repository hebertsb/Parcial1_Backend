#!/usr/bin/env python3
"""
Test del endpoint de registro de inquilinos con campos de contraseña
POST /api/authz/propietarios/panel/inquilinos/
"""

import requests
import json

# Configuración
BASE_URL = "http://127.0.0.1:8000"
LOGIN_URL = f"{BASE_URL}/api/authz/login/"
REGISTRO_INQUILINO_URL = f"{BASE_URL}/api/authz/propietarios/panel/inquilinos/"

def login_propietario():
    """Login como propietario para obtener token"""
    login_data = {
        "email": "propietario@test.com",
        "password": "test123456"
    }
    
    print("🔐 Haciendo login como propietario...")
    response = requests.post(LOGIN_URL, json=login_data)
    
    if if response is not None:
     response.status_code == 200:
        token = if response is not None:
     response.json().get('access')
        print(f"✅ Login exitoso. Token obtenido.")
        return token
    else:
        print(f"❌ Error en login: {response.status_code}")
        print(f"Response: {response.text}")
        return None

def test_registro_inquilino_con_password(token):
    """Test del registro de inquilino con contraseña personalizada"""
    
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    # Payload con los nuevos campos de contraseña
    payload = {
        "nombre": "María",
        "apellido": "González",
        "documento_identidad": "9876543212",
        "fecha_nacimiento": "1995-05-15",
        "telefono": "59171234567",
        "email": "maria.gonzalez@gmail.com",
        "genero": "F",
        "password": "maria2025*",  # Contraseña personalizada
        "confirm_password": "maria2025*",  # Confirmación
        "fecha_inicio": "2025-10-01",
        "fecha_fin": "2026-10-01",
        "monto_alquiler": 2500.00,
        "observaciones": "Inquilina responsable con referencias",
        "vivienda_id": 15
    }
    
    print("\n🏠 Registrando inquilino con contraseña personalizada...")
    print(f"📧 Email: {payload['email']}")
    print(f"🔑 Password: {payload['password']}")
    print(f"🏡 Vivienda ID: {payload['vivienda_id']}")
    
    response = requests.post(REGISTRO_INQUILINO_URL, json=payload, headers=headers)
    
    print(f"\n📊 Status Code: {response.status_code}")
    
    if if response is not None:
     response.status_code == 201:
        data = if response is not None:
     response.json()
        print("✅ ¡Inquilino registrado exitosamente!")
        print(f"📄 Respuesta: {json.dumps(data, indent=2, ensure_ascii=False)}")
        return True
    else:
        print("❌ Error en el registro:")
        try:
            error_data = if response is not None:
     response.json()
            print(f"📄 Error JSON: {json.dumps(error_data, indent=2, ensure_ascii=False)}")
        except:
            print(f"📄 Error texto: {response.text}")
        return False

def test_registro_password_no_coinciden(token):
    """Test con contraseñas que no coinciden"""
    
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    payload = {
        "nombre": "Carlos",
        "apellido": "Ruiz",
        "documento_identidad": "9876543213",
        "fecha_nacimiento": "1990-03-20",
        "telefono": "59171234568",
        "email": "carlos.ruiz@gmail.com",
        "genero": "M",
        "password": "carlos2025*",
        "confirm_password": "diferente123",  # ❌ Contraseña diferente
        "fecha_inicio": "2025-11-01",
        "fecha_fin": "2026-11-01",
        "monto_alquiler": 2200.00,
        "observaciones": "Test de validación",
        "vivienda_id": 15
    }
    
    print("\n🧪 Testing contraseñas que no coinciden...")
    response = requests.post(REGISTRO_INQUILINO_URL, json=payload, headers=headers)
    
    print(f"📊 Status Code: {response.status_code}")
    
    if if response is not None:
     response.status_code == 400:
        data = if response is not None:
     response.json()
        print("✅ Validación funcionando correctamente:")
        print(f"📄 Error esperado: {json.dumps(data, indent=2, ensure_ascii=False)}")
        return True
    else:
        print("❌ La validación no funcionó como esperado:")
        print(f"📄 Respuesta: {response.text}")
        return False

def test_password_debil(token):
    """Test con contraseña muy débil"""
    
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    payload = {
        "nombre": "Ana",
        "apellido": "López",
        "documento_identidad": "9876543214",
        "fecha_nacimiento": "1988-12-10",
        "telefono": "59171234569",
        "email": "ana.lopez@gmail.com",
        "genero": "F",
        "password": "123",  # ❌ Contraseña muy débil
        "confirm_password": "123",
        "fecha_inicio": "2025-12-01",
        "fecha_fin": "2026-12-01",
        "monto_alquiler": 2000.00,
        "observaciones": "Test validación password",
        "vivienda_id": 15
    }
    
    print("\n🧪 Testing contraseña muy débil...")
    response = requests.post(REGISTRO_INQUILINO_URL, json=payload, headers=headers)
    
    print(f"📊 Status Code: {response.status_code}")
    
    if if response is not None:
     response.status_code == 400:
        data = if response is not None:
     response.json()
        print("✅ Validación de fortaleza funcionando:")
        print(f"📄 Error esperado: {json.dumps(data, indent=2, ensure_ascii=False)}")
        return True
    else:
        print("❌ La validación de fortaleza no funcionó:")
        print(f"📄 Respuesta: {response.text}")
        return False

def main():
    print("🚀 INICIANDO TESTS DE REGISTRO DE INQUILINOS CON PASSWORD")
    print("=" * 60)
    
    # Login
    token = login_propietario()
    if not token:
        print("❌ No se pudo obtener token. Abortando tests.")
        return
    
    # Test 1: Registro exitoso con contraseña personalizada
    print("\n" + "="*50)
    print("TEST 1: REGISTRO CON CONTRASEÑA PERSONALIZADA")
    print("="*50)
    test1_ok = test_registro_inquilino_con_password(token)
    
    # Test 2: Contraseñas no coinciden
    print("\n" + "="*50)
    print("TEST 2: CONTRASEÑAS NO COINCIDEN")
    print("="*50)
    test2_ok = test_registro_password_no_coinciden(token)
    
    # Test 3: Contraseña muy débil
    print("\n" + "="*50)
    print("TEST 3: CONTRASEÑA MUY DÉBIL")
    print("="*50)
    test3_ok = test_password_debil(token)
    
    # Resumen
    print("\n" + "="*50)
    print("RESUMEN DE TESTS")
    print("="*50)
    print(f"✅ Test 1 (Registro exitoso): {'PASÓ' if test1_ok else 'FALLÓ'}")
    print(f"✅ Test 2 (Contraseñas no coinciden): {'PASÓ' if test2_ok else 'FALLÓ'}")
    print(f"✅ Test 3 (Contraseña débil): {'PASÓ' if test3_ok else 'FALLÓ'}")
    
    total_tests = 3
    tests_pasados = sum([test1_ok, test2_ok, test3_ok])
    
    print(f"\n🎯 RESULTADO FINAL: {tests_pasados}/{total_tests} tests pasaron")
    
    if tests_pasados == total_tests:
        print("🎉 ¡TODOS LOS TESTS PASARON! El endpoint funciona correctamente.")
    else:
        print("⚠️  Algunos tests fallaron. Revisar la implementación.")

if __name__ == "__main__":
    main()