#!/usr/bin/env python
"""
Script para probar los nuevos endpoints de administración de propietarios
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
    try:
        admin = Usuario.objects.filter(roles__nombre='Administrador').first()
        if not admin:
            print("❌ No hay administradores en el sistema")
            return None
        
        refresh = RefreshToken.for_user(admin)
        return str(refresh.access_token)
    except Exception as e:
        print(f"❌ Error obteniendo token: {e}")
        return None

def test_listar_propietarios():
    """Probar endpoint de listar propietarios"""
    print("\n🔍 PROBANDO: Listar propietarios con información completa")
    print("=" * 60)
    
    client = Client()
    token = obtener_token_admin()
    
    if not token:
        return
    
    try:
        # Hacer request
        headers = {'HTTP_AUTHORIZATION': f'Bearer {token}'}
        response = client.get('/auth/admin/propietarios/listar/', **headers)
        
        print(f"📡 Status Code: {response.status_code}")
        
        if if response is not None:
     response.status_code == 200:
            data = if response is not None:
     response.json()
            print(f"✅ Respuesta exitosa!")
            print(f"📊 Total propietarios: {data.get('total', 0)}")
            
            propietarios = data.get('data', [])
            for prop in propietarios[:3]:  # Mostrar solo los primeros 3
                print(f"\n👤 Propietario:")
                print(f"   📧 Email: {prop.get('email')}")
                print(f"   🏠 Unidad: {prop.get('unidad_residencial')}")
                print(f"   👥 Tiene perfil copropietario: {prop.get('tiene_perfil_copropietario')}")
                print(f"   📸 Puede subir fotos: {prop.get('puede_subir_fotos')}")
                print(f"   📷 Foto perfil: {prop.get('foto_perfil_url')}")
                
        else:
            print(f"❌ Error: {response.status_code}")
            try:
                error_data = if response is not None:
     response.json()
                print(f"   Mensaje: {error_data.get('message', 'Sin mensaje')}")
            except:
                print(f"   Contenido: {response.content.decode()[:200]}...")
                
    except Exception as e:
        print(f"❌ Excepción: {e}")

def test_editar_propietario():
    """Probar endpoint de editar propietario"""
    print("\n✏️  PROBANDO: Editar información de propietario")
    print("=" * 60)
    
    client = Client()
    token = obtener_token_admin()
    
    if not token:
        return
    
    try:
        # Buscar un propietario para editar
        from authz.models import Usuario
        propietario = Usuario.objects.filter(roles__nombre='Propietario').first()
        
        if not propietario:
            print("❌ No hay propietarios en el sistema para probar")
            return
        
        print(f"🎯 Editando propietario: {propietario.email} (ID: {propietario.id})")
        
        # Datos de prueba
        datos_edicion = {
            'nombres': 'Nombre Editado',
            'apellidos': 'Apellido Editado',
            'telefono': '77777777',
            'unidad_residencial': 'Casa 999',
            'estado_usuario': 'ACTIVO'
        }
        
        # Hacer request
        headers = {'HTTP_AUTHORIZATION': f'Bearer {token}'}
        response = client.put(
            f'/auth/admin/propietarios/{propietario.id}/editar/',
            data=json.dumps(datos_edicion),
            content_type='application/json',
            **headers
        )
        
        print(f"📡 Status Code: {response.status_code}")
        
        if if response is not None:
     response.status_code == 200:
            data = if response is not None:
     response.json()
            print(f"✅ Propietario editado exitosamente!")
            print(f"   Usuario ID: {data.get('data', {}).get('usuario_id')}")
            print(f"   Copropietario ID: {data.get('data', {}).get('copropietario_id')}")
            print(f"   Unidad residencial: {data.get('data', {}).get('unidad_residencial')}")
            
        else:
            print(f"❌ Error: {response.status_code}")
            try:
                error_data = if response is not None:
     response.json()
                print(f"   Mensaje: {error_data.get('message', 'Sin mensaje')}")
            except:
                print(f"   Contenido: {response.content.decode()[:200]}...")
                
    except Exception as e:
        print(f"❌ Excepción: {e}")

def verificar_asociacion_viviendas():
    """Verificar que los propietarios tienen las viviendas correctas"""
    print("\n🏠 VERIFICANDO: Asociación con viviendas")
    print("=" * 60)
    
    try:
        from authz.models import Usuario, SolicitudRegistroPropietario
        from seguridad.models import Copropietarios
        
        propietarios = Usuario.objects.filter(roles__nombre='Propietario')
        print(f"📊 Total propietarios: {propietarios.count()}")
        
        for propietario in propietarios:
            print(f"\n👤 {propietario.email}:")
            
            # Verificar solicitud aprobada
            solicitud = SolicitudRegistroPropietario.objects.filter(
                usuario_creado=propietario,
                estado='APROBADA'
            ).first()
            
            if solicitud:
                print(f"   📋 Solicitud: Casa {solicitud.numero_casa}")
                if solicitud.vivienda_validada:
                    print(f"   🏠 Vivienda validada: {solicitud.vivienda_validada.numero_casa}")  # ✅ Corregido
            else:
                print(f"   ❌ Sin solicitud aprobada")
            
            # Verificar copropietario
            copropietario = getattr(propietario, 'copropietario_perfil', None)
            if copropietario:
                print(f"   👥 Copropietario: {copropietario.unidad_residencial}")
                print(f"   📸 Puede subir fotos: ✅")
            else:
                print(f"   ❌ Sin perfil de copropietario")
                print(f"   📸 Puede subir fotos: ❌")
    
    except Exception as e:
        print(f"❌ Error verificando asociaciones: {e}")

def main():
    """Ejecutar todas las pruebas"""
    print("🧪 PRUEBAS DE ENDPOINTS ADMIN PARA PROPIETARIOS")
    print("=" * 70)
    
    # Verificar estado actual
    verificar_asociacion_viviendas()
    
    # Probar endpoints
    test_listar_propietarios()
    test_editar_propietario()
    
    print("\n🎯 ENDPOINTS DISPONIBLES:")
    print("📍 GET  /auth/admin/propietarios/listar/")
    print("📍 PUT  /auth/admin/propietarios/<usuario_id>/editar/")
    
    print("\n✅ Pruebas completadas!")

if __name__ == "__main__":
    main()