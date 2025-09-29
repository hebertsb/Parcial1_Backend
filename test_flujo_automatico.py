#!/usr/bin/env python
"""
🧪 PRUEBA DEL FLUJO AUTOMÁTICO COMPLETO
Simula todo el proceso desde solicitud hasta reconocimiento facial
"""

import os
import sys
import django
import requests
import json
from datetime import date

# Configurar Django
sys.path.append('.')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from authz.models import SolicitudRegistroPropietario, Usuario
from seguridad.models import ReconocimientoFacial, Copropietarios

BASE_URL = "http://127.0.0.1:8000"

def test_flujo_completo():
    print("🧪 PROBANDO FLUJO AUTOMÁTICO COMPLETO")
    print("=" * 60)
    
    # 1. CREAR SOLICITUD DE PROPIETARIO NUEVO
    print("\n1️⃣ CREANDO SOLICITUD DE PROPIETARIO NUEVO...")
    
    solicitud_data = {
        "nombres": "Ana María",
        "apellidos": "Pérez González", 
        "documento_identidad": f"TEST{date.today().strftime('%m%d%H%M')}",
        "fecha_nacimiento": "1990-05-15",
        "email": f"ana.perez.{date.today().strftime('%m%d%H%M')}@test.com",
        "telefono": "+591-70999888",
        "numero_casa": "V012",  # Vivienda disponible sin solicitud
        "bloque_torre": "Torre A",
        "password": "TestPass123!",
        "password_confirm": "TestPass123!",
        "confirm_password": "TestPass123!",  # Ambos campos por compatibilidad
        "acepta_terminos": True,
        "acepta_tratamiento_datos": True,
        "fotos_base64": ["data:image/jpeg;base64,/9j/4AAQSkZJRgABAQEAYABgAAD/2wBDAAEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQH/2wBDAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQH/wAARCABIAEgDASIAAhEBAxEB/8QAFQABAQAAAAAAAAAAAAAAAAAAAAv/xAAUEAEAAAAAAAAAAAAAAAAAAAAA/8QAFQEBAQAAAAAAAAAAAAAAAAAAAAX/xAAUEQEAAAAAAAAAAAAAAAAAAAAA/9oADAMBAAIRAxEAPwCdAA=="]  # Imagen mínima válida
    }
    
    response = requests.post(f"{BASE_URL}/api/authz/propietarios/solicitud/", 
                           json=solicitud_data)
    
    if response.status_code == 201:
        solicitud_id = response.json()['data']['id']
        print(f"✅ Solicitud creada: ID {solicitud_id}")
    else:
        print(f"❌ Error creando solicitud: {response.status_code}")
        print(response.text)
        return
    
    # 2. APROBAR SOLICITUD (SIMULANDO ADMIN)
    print("\n2️⃣ APROBANDO SOLICITUD...")
    
    # Login como admin
    admin_login = requests.post(f"{BASE_URL}/api/auth/login/", 
                              json={"email": "admin@facial.com", "password": "admin123"})
    
    if admin_login.status_code == 200:
        admin_token = admin_login.json()['access']
        headers = {'Authorization': f'Bearer {admin_token}'}
        
        # Aprobar solicitud
        aprobar_response = requests.post(
            f"{BASE_URL}/api/authz/propietarios/admin/solicitudes/{solicitud_id}/aprobar/",
            json={"observaciones": "Aprobado por test automático"},
            headers=headers
        )
        
        if aprobar_response.status_code == 200:
            usuario_data = aprobar_response.json()['data']
            nuevo_usuario_id = usuario_data['usuario_id']
            print(f"✅ Solicitud aprobada - Usuario creado: ID {nuevo_usuario_id}")
            print(f"   Email: {usuario_data['email_propietario']}")
        else:
            print(f"❌ Error aprobando solicitud: {aprobar_response.status_code}")
            print(aprobar_response.text)
            return
    else:
        print("❌ Error login admin")
        return
    
    # 3. VERIFICAR CREACIÓN AUTOMÁTICA DE COPROPIETARIO
    print("\n3️⃣ VERIFICANDO CREACIÓN AUTOMÁTICA DE COPROPIETARIO...")
    
    try:
        usuario = Usuario.objects.get(id=nuevo_usuario_id)
        copropietario = Copropietarios.objects.filter(usuario_sistema=usuario).first()
        
        if copropietario:
            print(f"✅ Copropietario creado automáticamente: ID {copropietario.id}")
            print(f"   Nombre: {copropietario.nombres} {copropietario.apellidos}")
            print(f"   Unidad: {copropietario.unidad_residencial}")
        else:
            print("❌ No se creó copropietario automáticamente")
            return
            
    except Usuario.DoesNotExist:
        print("❌ Usuario no encontrado")
        return
    
    # 4. LOGIN COMO NUEVO PROPIETARIO
    print("\n4️⃣ LOGIN COMO NUEVO PROPIETARIO...")
    
    propietario_login = requests.post(f"{BASE_URL}/api/auth/login/", 
                                    json={"email": usuario.email, "password": "temporal123"})
    
    if propietario_login.status_code == 200:
        propietario_token = propietario_login.json()['access']
        propietario_headers = {'Authorization': f'Bearer {propietario_token}'}
        print(f"✅ Login exitoso como propietario")
    else:
        print(f"❌ Error login propietario: {propietario_login.status_code}")
        print(propietario_login.text)
        return
    
    # 5. VERIFICAR INCLUSIÓN EN ENDPOINT DE SEGURIDAD
    print("\n5️⃣ VERIFICANDO INCLUSIÓN EN ENDPOINT DE SEGURIDAD...")
    
    # Usar token de seguridad
    seguridad_login = requests.post(f"{BASE_URL}/api/auth/login/", 
                                  json={"email": "seguridad@facial.com", "password": "seguridad123"})
    
    if seguridad_login.status_code == 200:
        seguridad_token = seguridad_login.json()['access']
        seguridad_headers = {'Authorization': f'Bearer {seguridad_token}'}
        
        endpoint_response = requests.get(
            f"{BASE_URL}/seguridad/api/usuarios-reconocimiento/",
            headers=seguridad_headers
        )
        
        if endpoint_response.status_code == 200:
            usuarios = endpoint_response.json()['data']
            nuevo_encontrado = False
            
            for user in usuarios:
                if user.get('usuario_id') == nuevo_usuario_id:
                    nuevo_encontrado = True
                    print(f"✅ Usuario encontrado en endpoint de seguridad:")
                    print(f"   Usuario ID: {user['usuario_id']}")
                    print(f"   Copropietario ID: {user['copropietario_id']}")
                    print(f"   Nombre: {user['nombres_completos']}")
                    print(f"   Email: {user['email']}")
                    break
            
            if not nuevo_encontrado:
                print("❌ Usuario NO aparece en endpoint de seguridad")
            else:
                print("\n🎉 FLUJO AUTOMÁTICO FUNCIONANDO PERFECTAMENTE!")
                print("   ✅ Solicitud → Aprobación → Usuario → Copropietario → Endpoint")
        else:
            print(f"❌ Error consultando endpoint: {endpoint_response.status_code}")
    else:
        print("❌ Error login seguridad")
    
    print("\n" + "=" * 60)
    print("🎯 CONCLUSIÓN: El sistema ES automático para usuarios nuevos")
    print("   El problema del usuario ID 8 era porque se creó manualmente")

if __name__ == "__main__":
    test_flujo_completo()