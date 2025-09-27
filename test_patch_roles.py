#!/usr/bin/env python3
"""
Script para probar la corrección del endpoint PATCH /api/authz/usuarios/{id}/
que ahora debería procesar correctamente los cambios de roles.
"""

import os
import django
import requests
import json

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from authz.models import Usuario, Rol
from django.contrib.auth.hashers import make_password

def test_patch_roles():
    print("🧪 INICIANDO PRUEBAS DE PATCH ROLES")
    print("=" * 50)
    
    # 1. Crear usuario admin de prueba si no existe
    admin_email = "admin@test.com"
    admin_password = "admin123"
    
    try:
        admin_user = Usuario.objects.get(email=admin_email)
        print(f"✅ Admin usuario encontrado: {admin_email}")
    except Usuario.DoesNotExist:
        admin_user = Usuario.objects.create(
            email=admin_email,
            password=make_password(admin_password),
            estado="ACTIVO"
        )
        # Asignar rol de administrador
        admin_rol, _ = Rol.objects.get_or_create(nombre="Administrador")
        admin_user.roles.add(admin_rol)
        print(f"✅ Admin usuario creado: {admin_email}")
    
    # 2. Crear usuario de prueba
    test_email = "usuario_prueba@test.com"
    test_password = "test123"
    
    try:
        test_user = Usuario.objects.get(email=test_email)
        print(f"✅ Usuario de prueba encontrado: {test_email}")
    except Usuario.DoesNotExist:
        test_user = Usuario.objects.create(
            email=test_email,
            password=make_password(test_password),
            estado="ACTIVO"
        )
        # Asignar rol inicial de inquilino
        inquilino_rol, _ = Rol.objects.get_or_create(nombre="Inquilino")
        test_user.roles.add(inquilino_rol)
        print(f"✅ Usuario de prueba creado: {test_email}")
    
    # 3. Verificar estado inicial
    print(f"\n📊 ESTADO INICIAL:")
    print(f"   Usuario: {test_user.email}")
    print(f"   Roles actuales: {[r.nombre for r in test_user.roles.all()]}")
    
    # 4. Simular login del admin para obtener token
    login_data = {
        "email": admin_email,
        "password": admin_password
    }
    
    login_response = requests.post("http://localhost:8000/api/authz/login/", json=login_data)
    if login_response.status_code != 200:
        print(f"❌ Error en login: {login_response.status_code}")
        print(f"   Respuesta: {login_response.text}")
        return
    
    token = login_response.json()["access"]
    headers = {"Authorization": f"Bearer {token}"}
    print(f"✅ Login exitoso, token obtenido")
    
    # 5. Obtener ID del rol Propietario
    try:
        propietario_rol = Rol.objects.get(nombre="Propietario")
        propietario_id = propietario_rol.id
        print(f"✅ Rol Propietario encontrado con ID: {propietario_id}")
    except Rol.DoesNotExist:
        propietario_rol = Rol.objects.create(nombre="Propietario")
        propietario_id = propietario_rol.id
        print(f"✅ Rol Propietario creado con ID: {propietario_id}")
    
    # 6. Realizar PATCH para cambiar roles
    patch_data = {
        "roles": [propietario_id]
    }
    
    print(f"\n🔄 EJECUTANDO PATCH:")
    print(f"   URL: http://localhost:8000/api/authz/usuarios/{test_user.id}/")
    print(f"   Data: {patch_data}")
    
    patch_response = requests.patch(
        f"http://localhost:8000/api/authz/usuarios/{test_user.id}/",
        json=patch_data,
        headers=headers
    )
    
    print(f"📊 RESPUESTA PATCH:")
    print(f"   Status: {patch_response.status_code}")
    print(f"   Headers: {dict(patch_response.headers)}")
    
    if patch_response.status_code == 200:
        response_data = patch_response.json()
        print(f"   Response body: {json.dumps(response_data, indent=2, ensure_ascii=False)}")
        
        # 7. Verificar cambios en la base de datos
        test_user.refresh_from_db()
        roles_actuales = [r.nombre for r in test_user.roles.all()]
        
        print(f"\n📊 ESTADO DESPUÉS DEL PATCH:")
        print(f"   Usuario: {test_user.email}")
        print(f"   Roles actuales: {roles_actuales}")
        
        if "Propietario" in roles_actuales:
            print("✅ ¡ÉXITO! El endpoint PATCH ahora procesa los roles correctamente")
            print("✅ El rol Propietario fue asignado correctamente")
        else:
            print("❌ FALLO: El rol no fue asignado correctamente")
            print(f"   Roles esperados: ['Propietario']")
            print(f"   Roles actuales: {roles_actuales}")
    else:
        print(f"❌ Error en PATCH: {patch_response.status_code}")
        print(f"   Respuesta: {patch_response.text}")
    
    print("\n" + "=" * 50)
    print("🧪 PRUEBAS COMPLETADAS")

if __name__ == "__main__":
    test_patch_roles()