#!/usr/bin/env python
import requests
import json

# Datos de prueba para crear una solicitud
data = {
    "nombres": "Ana María",
    "apellidos": "García Silva",
    "documento_identidad": "7234567",
    "fecha_nacimiento": "1985-03-14",
    "email": "ana.garcia@email.com",
    "telefono": "7234567",
    "numero_casa": "A-101",
    "password": "Password123!",
    "password_confirm": "Password123!",
    "genero": "femenino",
    "acepta_terminos": True,
    "acepta_tratamiento_datos": True
}

print("=== PRUEBA DE API: CREAR SOLICITUD ===")
print(f"📤 Enviando datos: {json.dumps(data, indent=2)}")

try:
    # Realizar petición POST
    response = requests.post(
        'http://127.0.0.1:8000/api/authz/propietarios/solicitud/',
        json=data,
        headers={'Content-Type': 'application/json'}
    )
    
    print(f"\n📊 Status Code: {response.status_code}")
    print(f"📋 Headers: {dict(response.headers)}")
    
    try:
        result = response.json()
        print(f"📄 Response JSON: {json.dumps(result, indent=2)}")
    except:
        print(f"📄 Response Text: {response.text}")
        
except requests.exceptions.ConnectionError:
    print("❌ ERROR: No se puede conectar al servidor Django")
    print("Asegúrate de que Django esté ejecutándose en http://127.0.0.1:8000")
except Exception as e:
    print(f"❌ ERROR: {e}")