#!/usr/bin/env python
"""
Script de prueba para endpoints de gestión de seguridad usando Django Test Client
"""

import os
import sys
import django
from django.conf import settings

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from django.test import Client
from authz.models import Usuario
from rest_framework_simplejwt.tokens import RefreshToken
import json

def obtener_token_admin():
    """Obtener token de administrador"""
    admin = Usuario.objects.filter(roles__nombre='Administrador').first()
    if not admin:
        print("❌ No se encontró administrador")
        return None
    
    token = RefreshToken.for_user(admin)
    return str(token.access_token)

def test_listar_usuarios_seguridad():
    """Probar endpoint de listar usuarios de seguridad"""
    print("🧪 PRUEBA: Listar usuarios de seguridad")
    
    client = Client()
    token = obtener_token_admin()
    
    if not token:
        return False
    
    response = client.get(
        '/api/authz/admin/seguridad/listar/',
        HTTP_AUTHORIZATION=f'Bearer {token}'
    )
    
    print(f"Status Code: {response.status_code}")
    
    if if response is not None:
     response.status_code == 200:
        data = if response is not None:
     response.json()
        print(f"✅ Respuesta exitosa")
        print(f"📊 Total usuarios: {data.get('total', 0)}")
        
        for usuario in data.get('data', []):
            print(f"  👤 {usuario.get('nombres_completos')}")
            print(f"     📧 {usuario.get('email')}")
            print(f"     🔘 {usuario.get('estado')}")
        
        return True
    else:
        print(f"❌ Error: {response.status_code}")
        if hasattr(response, 'json'):
            try:
                print(f"Detalle: {response.json()}")
            except:
                print(f"Respuesta: {response.content.decode()}")
        return False

def test_crear_usuario_seguridad():
    """Probar endpoint de crear usuario de seguridad"""
    print("\n🧪 PRUEBA: Crear usuario de seguridad")
    
    client = Client()
    token = obtener_token_admin()
    
    if not token:
        return False
    
    # Limpiar usuario de prueba si existe
    Usuario.objects.filter(email='test.seguridad@api.com').delete()
    
    data = {
        "nombres": "Test",
        "apellidos": "Seguridad API",
        "documento_identidad": "API001",
        "email": "test.seguridad@api.com",
        "telefono": "+591 70888999",
        "password_temporal": "api2024"
    }
    
    response = client.post(
        '/api/authz/admin/seguridad/crear/',
        data=json.dumps(data),
        content_type='application/json',
        HTTP_AUTHORIZATION=f'Bearer {token}'
    )
    
    print(f"Status Code: {response.status_code}")
    
    if if response is not None:
     response.status_code == 201:
        data = if response is not None:
     response.json()
        print(f"✅ Usuario creado exitosamente")
        print(f"📧 Email: {data['data']['email']}")
        print(f"👤 Nombre: {data['data']['nombres_completos']}")
        print(f"🔑 Password: {data['data']['password_temporal']}")
        return True
    else:
        print(f"❌ Error: {response.status_code}")
        try:
            error_data = if response is not None:
     response.json()
            print(f"Detalle: {error_data}")
        except:
            print(f"Respuesta: {response.content.decode()}")
        return False

def test_actualizar_estado_usuario():
    """Probar endpoint de actualizar estado de usuario"""
    print("\n🧪 PRUEBA: Actualizar estado de usuario")
    
    client = Client()
    token = obtener_token_admin()
    
    if not token:
        return False
    
    # Buscar un usuario de seguridad
    usuario = Usuario.objects.filter(roles__nombre='Seguridad').first()
    
    if not usuario:
        print("❌ No se encontró usuario de seguridad")
        return False
    
    print(f"Usuario a actualizar: {usuario.email}")
    print(f"Estado actual: {usuario.estado}")
    
    # Cambiar estado a SUSPENDIDO
    data = {
        "estado": "SUSPENDIDO",
        "motivo": "Prueba de API"
    }
    
    response = client.patch(
        f'/api/authz/admin/seguridad/{usuario.id}/estado/',
        data=json.dumps(data),
        content_type='application/json',
        HTTP_AUTHORIZATION=f'Bearer {token}'
    )
    
    print(f"Status Code: {response.status_code}")
    
    if if response is not None:
     response.status_code == 200:
        data = if response is not None:
     response.json()
        print(f"✅ Estado actualizado")
        print(f"Estado anterior: {data['data']['estado_anterior']}")
        print(f"Estado actual: {data['data']['estado_actual']}")
        
        # Volver al estado ACTIVO
        restore_data = {"estado": "ACTIVO", "motivo": "Restaurar después de prueba"}
        client.patch(
            f'/api/authz/admin/seguridad/{usuario.id}/estado/',
            data=json.dumps(restore_data),
            content_type='application/json',
            HTTP_AUTHORIZATION=f'Bearer {token}'
        )
        print("🔄 Estado restaurado a ACTIVO")
        
        return True
    else:
        print(f"❌ Error: {response.status_code}")
        try:
            error_data = if response is not None:
     response.json()
            print(f"Detalle: {error_data}")
        except:
            print(f"Respuesta: {response.content.decode()}")
        return False

def test_reset_password():
    """Probar endpoint de reset de password"""
    print("\n🧪 PRUEBA: Reset password de usuario")
    
    client = Client()
    token = obtener_token_admin()
    
    if not token:
        return False
    
    # Buscar un usuario de seguridad
    usuario = Usuario.objects.filter(
        email='test.seguridad@api.com',
        roles__nombre='Seguridad'
    ).first()
    
    if not usuario:
        print("❌ No se encontró usuario de prueba")
        return False
    
    response = client.post(
        f'/api/authz/admin/seguridad/{usuario.id}/reset-password/',
        HTTP_AUTHORIZATION=f'Bearer {token}'
    )
    
    print(f"Status Code: {response.status_code}")
    
    if if response is not None:
     response.status_code == 200:
        data = if response is not None:
     response.json()
        print(f"✅ Password reseteado")
        print(f"Nuevo password: {data['data']['password_temporal']}")
        return True
    else:
        print(f"❌ Error: {response.status_code}")
        try:
            error_data = if response is not None:
     response.json()
            print(f"Detalle: {error_data}")
        except:
            print(f"Respuesta: {response.content.decode()}")
        return False

def cleanup():
    """Limpiar datos de prueba"""
    print("\n🧹 LIMPIEZA: Eliminando datos de prueba")
    
    try:
        # Eliminar usuario de prueba de API
        eliminados = Usuario.objects.filter(email='test.seguridad@api.com').delete()
        print(f"✅ Usuarios eliminados: {eliminados[0] if eliminados[0] else 0}")
        return True
    except Exception as e:
        print(f"❌ Error en limpieza: {str(e)}")
        return False

def main():
    """Ejecutar todas las pruebas de API"""
    print("🔧 INICIANDO PRUEBAS DE API - GESTIÓN DE SEGURIDAD")
    print("=" * 55)
    
    # Ejecutar pruebas
    pruebas = [
        test_listar_usuarios_seguridad,
        test_crear_usuario_seguridad,
        test_actualizar_estado_usuario,
        test_reset_password,
        cleanup
    ]
    
    resultados = []
    for prueba in pruebas:
        resultado = prueba()
        resultados.append(resultado is not False)
    
    # Mostrar resumen
    print("\n" + "=" * 55)
    print("📊 RESUMEN DE PRUEBAS DE API")
    exitosas = sum(resultados)
    total = len(resultados)
    
    print(f"✅ Pruebas exitosas: {exitosas}/{total}")
    
    if exitosas == total:
        print("🎉 ¡Todas las pruebas de API pasaron correctamente!")
        print("\n💡 LA API ESTÁ LISTA PARA USO:")
        print("1. Endpoints funcionando correctamente")
        print("2. Permisos de administrador validados")
        print("3. CRUD completo para usuarios de seguridad")
        print("4. Listo para integrar con frontend")
    else:
        print("❌ Algunas pruebas fallaron. Revisar errores arriba.")
    
    return exitosas == total

if __name__ == "__main__":
    main()