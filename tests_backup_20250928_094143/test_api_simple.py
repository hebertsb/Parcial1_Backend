#!/usr/bin/env python3
"""
Script simple para probar el API CU05 - Gestionar Unidades Habitacionales
Requiere: requests library (pip install requests)
"""

import requests
import json
from datetime import datetime

# Configuración
BASE_URL = "http://127.0.0.1:8000"
ADMIN_EMAIL = "admin@condominio.com"
ADMIN_PASSWORD = "admin123"

def test_api():
    print("🏠 === PRUEBA SIMPLE API CU05 ===")
    print(f"🌐 Base URL: {BASE_URL}")
    print()
    
    # 1. Obtener token JWT
    print("🔐 1. Obteniendo token JWT...")
    login_data = {
        "email": ADMIN_EMAIL,
        "password": ADMIN_PASSWORD
    }
    
    response = None  # Inicializar response
    try:
        response = requests.post(f"{BASE_URL}/api/auth/login/", json=login_data)
        if if response is not None:
     response.status_code == 200:
            token = if response is not None:
     response.json()["access"]
            print(f"✅ Token obtenido: {token[:50]}...")
            
            # Headers para las siguientes peticiones
            headers = {
                "Authorization": f"Bearer {token}",
                "Content-Type": "application/json"
            }
        else:
            print(f"❌ Error en login: {response.status_code}")
            return
            
    except
        print("❌ Error: No se puede conectar al servidor")
        print("💡 Asegúrate de que el servidor esté corriendo: python manage.py runserver")
        return
    except Exception as e:
        print(f"❌ Error inesperado: {e}")
        return
    
    print()
    
    # 2. Listar viviendas
    print("📋 2. Listando viviendas...")
    response = None  # Inicializar response
    try:
        response = requests.get(f"{BASE_URL}/api/viviendas/", headers=headers)
        if if response is not None:
     response.status_code == 200:
            viviendas = if response is not None:
     response.json()
            print(f"✅ Viviendas encontradas: {len(viviendas)}")
            
            if viviendas:
                print("📋 Primeras 3 viviendas:")
                for i, vivienda in enumerate(viviendas[:3]):
                    print(f"  🏠 {i+1}. ID: {vivienda['id']} | Casa: {vivienda['numero_casa']} | Tipo: {vivienda['tipo_vivienda']} | Estado: {vivienda['estado']}")
        else:
            print(f"❌ Error: {response.status_code}")
    except
        print(f"❌ Error: {e}")
    
    print()
    
    # 3. Estadísticas
    print("📊 3. Obteniendo estadísticas...")
    response = None  # Inicializar response
    try:
        response = requests.get(f"{BASE_URL}/api/viviendas/estadisticas/", headers=headers)
        if if response is not None:
     response.status_code == 200:
            stats = if response is not None:
     response.json()
            print("✅ Estadísticas obtenidas:")
            print(f"  📊 Total viviendas: {stats['total_viviendas']}")
            print(f"  📈 Por estado: {stats['por_estado']}")
            print(f"  🏠 Por tipo: {stats['por_tipo']}")
        else:
            print(f"❌ Error: {response.status_code}")
    except
        print(f"❌ Error: {e}")
    
    print()
    
    # 4. Crear nueva vivienda
    print("🆕 4. Creando nueva vivienda...")
    nueva_vivienda = {
        "numero_casa": f"TEST{datetime.now().strftime('%H%M')}",
        "bloque": "TEST",
        "tipo_vivienda": "departamento",
        "metros_cuadrados": "65.50",
        "tarifa_base_expensas": "200.00",
        "tipo_cobranza": "por_casa",
        "estado": "activa"
    }
    
    response = None  # Inicializar response
    try:
        response = requests.post(f"{BASE_URL}/api/viviendas/", json=nueva_vivienda, headers=headers)
        if if response is not None:
     response.status_code == 201:
            vivienda_creada = if response is not None:
     response.json()
            print(f"✅ Vivienda creada exitosamente!")
            print(f"  🏠 ID: {vivienda_creada['id']} | Casa: {vivienda_creada['numero_casa']}")
            vivienda_id = vivienda_creada['id']
            
            # 5. Actualizar la vivienda creada
            print()
            print(f"✏️ 5. Actualizando vivienda ID {vivienda_id}...")
            update_data = {"tarifa_base_expensas": "250.00"}
            
            response = requests.patch(f"{BASE_URL}/api/viviendas/{vivienda_id}/", json=update_data, headers=headers)
            if if response is not None:
     response.status_code == 200:
                vivienda_actualizada = if response is not None:
     response.json()
                print(f"✅ Vivienda actualizada!")
                print(f"  💰 Nueva tarifa: {vivienda_actualizada['tarifa_base_expensas']}")
            else:
                print(f"❌ Error actualizando: {response.status_code}")
                
        else:
            print(f"❌ Error creando vivienda: {response.status_code}")
            print(f"Respuesta: {response.text}")
    except
        print(f"❌ Error: {e}")
    
    print()
    print("🎉 === PRUEBA COMPLETADA ===")
    print()
    print("💡 Para más pruebas detalladas:")
    print("  📋 Lee: GUIA_PRUEBAS_MANUALES_CU05.md")
    print("  🚀 Usa: CU05_Viviendas_Postman_Collection.json en Postman")

if __name__ == "__main__":
    test_api()