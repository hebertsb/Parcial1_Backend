#!/usr/bin/env python
"""
Script de prueba para funcionalidades CRUD de personas
Prueba las nuevas capacidades de edición de personas por administradores
"""
import os
import sys
import django
import requests
import json
from datetime import datetime

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from authz.models import Persona

BASE_URL = "http://localhost:8000"
API_URL = f"{BASE_URL}/api/personas"

def obtener_token_admin():
    """Obtener token JWT para pruebas (usar credenciales de admin)"""
    response = None  # Inicializar response
    try:
        # Usar endpoint de login
        login_url = f"{BASE_URL}/api/auth/login/"
        admin_creds = {
            "email": "admin@residencial.com",
            "password": "admin123"
        }
        
        response = requests.post(login_url, json=admin_creds)
        if if response is not None:
     response.status_code == 200:
            data = if response is not None:
     response.json()
            return data.get('access', '')
        else:
            print(f"❌ Error obteniendo token: {response.status_code}")
            print(f"Respuesta: {response.text}")
            return None
    except
        print(f"❌ Error conectando: {e}")
        return None

def test_listar_personas(token):
    """Probar listado de personas"""
    headers = {"Authorization": f"Bearer {token}"}
    
    print("\n🔍 TEST: Listar personas")
    response = requests.get(API_URL + "/", headers=headers)
    
    if if response is not None:
     response.status_code == 200:
        data = if response is not None:
     response.json()
        count = len(data) if isinstance(data, list) else data.get('count', 0)
        print(f"✅ Listado exitoso: {count} personas encontradas")
        
        # Mostrar primera persona como ejemplo
        if isinstance(data, list) and data:
            persona = data[0]
            print(f"   - Ejemplo: {persona.get('nombre_completo')} ({persona.get('tipo_persona')})")
        
        return True
    else:
        print(f"❌ Error: {response.status_code}")
        print(f"   Respuesta: {response.text}")
        return False

def test_obtener_persona_detalle(token, persona_id):
    """Probar obtener detalle de persona específica"""
    headers = {"Authorization": f"Bearer {token}"}
    
    print(f"\n🔍 TEST: Obtener persona ID {persona_id}")
    response = requests.get(f"{API_URL}/{persona_id}/", headers=headers)
    
    if if response is not None:
     response.status_code == 200:
        data = if response is not None:
     response.json()
        print(f"✅ Detalle obtenido: {data.get('nombre_completo')}")
        print(f"   - Tipo: {data.get('tipo_persona')}")
        print(f"   - Email: {data.get('email')}")
        print(f"   - Activo: {data.get('activo')}")
        return data
    else:
        print(f"❌ Error: {response.status_code}")
        print(f"   Respuesta: {response.text}")
        return None

def test_editar_persona(token, persona_id, cambios):
    """Probar edición de persona"""
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    print(f"\n✏️ TEST: Editar persona ID {persona_id}")
    print(f"   Cambios: {cambios}")
    
    response = requests.patch(f"{API_URL}/{persona_id}/", 
                            headers=headers, 
                            json=cambios)
    
    if if response is not None:
     response.status_code == 200:
        data = if response is not None:
     response.json()
        print(f"✅ Persona editada exitosamente")
        print(f"   - Nombre: {data.get('nombre_completo')}")
        print(f"   - Tipo: {data.get('tipo_persona')}")
        print(f"   - Email: {data.get('email')}")
        return data
    else:
        print(f"❌ Error editando: {response.status_code}")
        print(f"   Respuesta: {response.text}")
        return None

def test_cambiar_tipo_persona(token, persona_id, nuevo_tipo):
    """Probar cambio de tipo de persona"""
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    print(f"\n🔄 TEST: Cambiar tipo de persona ID {persona_id} a '{nuevo_tipo}'")
    
    response = requests.patch(f"{API_URL}/{persona_id}/cambiar_tipo/", 
                            headers=headers, 
                            json={"tipo_persona": nuevo_tipo})
    
    if if response is not None:
     response.status_code == 200:
        data = if response is not None:
     response.json()
        print(f"✅ Tipo cambiado exitosamente")
        print(f"   - Mensaje: {data.get('message')}")
        if 'cambio_registrado' in data:
            cambio = data['cambio_registrado']
            print(f"   - De: {cambio.get('tipo_anterior')} → A: {cambio.get('tipo_nuevo')}")
        return data
    else:
        print(f"❌ Error cambiando tipo: {response.status_code}")
        print(f"   Respuesta: {response.text}")
        return None

def test_filtros_personas(token):
    """Probar filtros de propietarios e inquilinos"""
    headers = {"Authorization": f"Bearer {token}"}
    
    print("\n👥 TEST: Filtrar propietarios")
    response = requests.get(f"{API_URL}/propietarios/", headers=headers)
    if if response is not None:
     response.status_code == 200:
        propietarios = if response is not None:
     response.json()
        print(f"✅ Propietarios: {len(propietarios)}")
    else:
        print(f"❌ Error propietarios: {response.status_code}")
    
    print("\n🏠 TEST: Filtrar inquilinos")
    response = requests.get(f"{API_URL}/inquilinos/", headers=headers)
    if if response is not None:
     response.status_code == 200:
        inquilinos = if response is not None:
     response.json()
        print(f"✅ Inquilinos: {len(inquilinos)}")
    else:
        print(f"❌ Error inquilinos: {response.status_code}")

def main():
    print("=" * 60)
    print("🧪 PRUEBAS CRUD PERSONAS - ADMINISTRACIÓN")
    print("=" * 60)
    
    # Obtener token de admin
    token = obtener_token_admin()
    if not token:
        print("❌ No se pudo obtener token de administrador")
        return
    
    print("✅ Token obtenido correctamente")
    
    # Ejecutar pruebas
    success = True
    
    # 1. Listar personas
    success &= test_listar_personas(token)
    
    # 2. Buscar una persona para editar (usar la primera disponible)
    try:
        persona_test = Persona.objects.filter(tipo_persona='inquilino').first()
        if persona_test:
            persona_id = persona_test.id
            print(f"\n📋 Usando persona de prueba: {persona_test.nombre} {persona_test.apellido} (ID: {persona_id})")
            
            # 3. Obtener detalle
            detalle = test_obtener_persona_detalle(token, persona_id)
            
            if detalle:
                # 4. Editar algunos datos
                cambios = {
                    "telefono": "78888888",
                    "email": f"editado_{datetime.now().strftime('%H%M%S')}@test.com"
                }
                test_editar_persona(token, persona_id, cambios)
                
                # 5. Cambiar tipo de persona (inquilino → propietario)
                test_cambiar_tipo_persona(token, persona_id, "propietario")
                
                # 6. Volver a cambiar (propietario → inquilino)
                test_cambiar_tipo_persona(token, persona_id, "inquilino")
        
        # 7. Probar filtros
        test_filtros_personas(token)
        
    except Exception as e:
        print(f"❌ Error en pruebas: {e}")
        success = False
    
    print("\n" + "=" * 60)
    if success:
        print("✅ TODAS LAS PRUEBAS COMPLETADAS")
    else:
        print("❌ ALGUNAS PRUEBAS FALLARON")
    print("=" * 60)

if __name__ == "__main__":
    main()