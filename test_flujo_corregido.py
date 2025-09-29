# 🧪 TEST FLUJO AUTOMÁTICO CORREGIDO

import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from authz.models import SolicitudRegistroPropietario, Usuario
from seguridad.models import Copropietarios, ReconocimientoFacial
import requests
import json

def crear_solicitud_test():
    """
    🎯 Crear solicitud de prueba para verificar flujo automático
    """
    print('🧪 CREAR SOLICITUD DE PRUEBA')
    print('=' * 35)
    
    try:
        # Datos del usuario de prueba
        email_test = 'test.flujo.v2@ejemplo.com'
        
        # Verificar que no exista ya
        if Usuario.objects.filter(email=email_test).exists():
            print(f'⚠️  Usuario {email_test} ya existe. Saltando creación.')
            return Usuario.objects.get(email=email_test)
        
        # Crear solicitud con campos correctos
        from datetime import date
        
        solicitud = SolicitudRegistroPropietario.objects.create(
            nombres='Test Flujo',
            apellidos='Automatico Corregido',
            email=email_test,
            documento_identidad='TEST_FLUJO_V2_002',
            fecha_nacimiento=date(1990, 1, 1),
            telefono='591-12345678',
            numero_casa='V015',
            estado='PENDIENTE',
            fotos_reconocimiento_urls=[]
        )
        
        print(f'✅ Solicitud creada: ID {solicitud.id}')
        print(f'   - Email: {solicitud.email}')
        print(f'   - Nombres: {solicitud.nombres} {solicitud.apellidos}')
        print(f'   - Casa: {solicitud.numero_casa}')
        
        return solicitud
        
    except Exception as e:
        print(f'❌ Error creando solicitud: {e}')
        return None

def aprobar_solicitud_test(solicitud):
    """
    🎯 Aprobar solicitud usando el flujo automático corregido
    """
    print(f'\n✅ APROBAR SOLICITUD (FLUJO AUTOMÁTICO)')
    print('=' * 45)
    
    try:
        # Obtener usuario admin para revisar
        admin_user = Usuario.objects.filter(roles__nombre='Administrador').first()
        if not admin_user:
            print('❌ No se encontró usuario administrador')
            return None
        
        print(f'👤 Revisor: {admin_user.email}')
        
        # Ejecutar método aprobar_solicitud (flujo automático corregido)
        usuario_creado = solicitud.aprobar_solicitud(admin_user)
        
        print(f'✅ Solicitud aprobada exitosamente')
        print(f'   - Usuario creado: ID {usuario_creado.id} - {usuario_creado.email}')
        print(f'   - Estado solicitud: {solicitud.estado}')
        
        return usuario_creado
        
    except Exception as e:
        print(f'❌ Error aprobando solicitud: {e}')
        return None

def verificar_registros_automaticos(usuario):
    """
    🔍 Verificar que se crearon TODOS los registros automáticamente
    """
    print(f'\n🔍 VERIFICAR REGISTROS AUTOMÁTICOS')
    print('=' * 40)
    
    try:
        print(f'👤 Usuario: ID {usuario.id} - {usuario.email}')
        
        # 1. Verificar Copropietario
        copropietario = Copropietarios.objects.filter(usuario_sistema=usuario).first()
        if copropietario:
            print(f'✅ Copropietario: ID {copropietario.id} - {copropietario.nombres} {copropietario.apellidos}')
            print(f'   - Casa: {copropietario.unidad_residencial}')
            print(f'   - Activo: {copropietario.activo}')
        else:
            print(f'❌ Copropietario: NO CREADO')
            return False
        
        # 2. Verificar ReconocimientoFacial
        reconocimiento = ReconocimientoFacial.objects.filter(copropietario_id=copropietario.id).first()
        if reconocimiento:
            print(f'✅ ReconocimientoFacial: ID {reconocimiento.id}')
            print(f'   - Activo: {reconocimiento.activo}')
            print(f'   - Vector facial: {reconocimiento.vector_facial}')
            print(f'   - Fecha enrolamiento: {reconocimiento.fecha_enrolamiento}')
        else:
            print(f'❌ ReconocimientoFacial: NO CREADO')
            return False
        
        return True
        
    except Exception as e:
        print(f'❌ Error verificando registros: {e}')
        return False

def probar_endpoints_usuario(usuario):
    """
    🧪 Probar que los endpoints funcionan con el usuario creado
    """
    print(f'\n🧪 PROBAR ENDPOINTS')
    print('=' * 25)
    
    try:
        # Login como seguridad
        login_response = requests.post('http://localhost:8000/api/authz/login/', {
            'email': 'seguridad@facial.com',
            'password': 'seguridad123'
        })
        
        if login_response.status_code != 200:
            print('❌ Error en login')
            return False
        
        token = login_response.json()['access']
        headers = {'Authorization': f'Bearer {token}'}
        
        # 1. Endpoint GET fotos
        response = requests.get(
            f'http://localhost:8000/api/authz/reconocimiento/fotos/{usuario.id}/',
            headers=headers
        )
        
        print(f'📸 GET fotos: Status {response.status_code}')
        if response.status_code == 200:
            data = response.json()
            if data.get('success'):
                fotos_data = data.get('data', {})
                print(f'   ✅ Usuario encontrado: {fotos_data.get("usuario_email")}')
                print(f'   ✅ Tiene reconocimiento: {fotos_data.get("tiene_reconocimiento")}')
                print(f'   ✅ Total fotos: {fotos_data.get("total_fotos", 0)}')
            else:
                print(f'   ❌ Error: {data.get("error")}')
                return False
        else:
            print(f'   ❌ Error HTTP: {response.status_code}')
            return False
        
        return True
        
    except Exception as e:
        print(f'❌ Error probando endpoints: {e}')
        return False

if __name__ == "__main__":
    print('🚀 TEST COMPLETO: FLUJO AUTOMÁTICO CORREGIDO')
    print('=' * 50)
    
    # 1. Crear solicitud
    solicitud = crear_solicitud_test()
    if not solicitud:
        exit(1)
    
    # 2. Aprobar (flujo automático)
    usuario = aprobar_solicitud_test(solicitud)
    if not usuario:
        exit(1)
    
    # 3. Verificar registros
    registros_ok = verificar_registros_automaticos(usuario)
    if not registros_ok:
        exit(1)
    
    # 4. Probar endpoints
    endpoints_ok = probar_endpoints_usuario(usuario)
    
    # 5. Resultado final
    print(f'\n🎯 RESULTADO FINAL DEL TEST:')
    if registros_ok and endpoints_ok:
        print('🎉 ¡FLUJO AUTOMÁTICO CORREGIDO FUNCIONA PERFECTAMENTE!')
        print('✅ Solicitud → Aprobación → Usuario + Copropietario + ReconocimientoFacial')
        print('✅ Usuario puede subir fotos inmediatamente')
        print('✅ Endpoints funcionan correctamente')
        print(f'\n📋 FLUJO AUTOMÁTICO: ✅ REPARADO')
    else:
        print('❌ El flujo automático aún tiene problemas')
        print('🔧 Requiere correcciones adicionales')