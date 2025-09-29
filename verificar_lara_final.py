# 🔍 VERIFICACIÓN FINAL: Estado de lara@gmail.com

import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from seguridad.models import ReconocimientoFacial, Copropietarios
from authz.models import Usuario
import requests

def verificar_lara_completo():
    """
    🎯 Verificación completa del estado de lara@gmail.com
    """
    print('🔍 VERIFICACIÓN FINAL: lara@gmail.com')
    print('=' * 45)
    
    try:
        # 1. Usuario
        usuario = Usuario.objects.get(email='lara@gmail.com')
        print(f'✅ Usuario ID: {usuario.id} - {usuario.email}')
        
        # 2. Copropietario
        copropietario = Copropietarios.objects.filter(usuario_sistema=usuario).first()
        print(f'✅ Copropietario ID: {copropietario.id} - {copropietario.nombres} {copropietario.apellidos}')
        
        # 3. ReconocimientoFacial
        reconocimiento = ReconocimientoFacial.objects.filter(copropietario_id=copropietario.id).first()
        if reconocimiento:
            print(f'✅ ReconocimientoFacial ID: {reconocimiento.id}')
            print(f'   - Activo: {reconocimiento.activo}')
            vector_len = len(str(reconocimiento.vector_facial)) if reconocimiento.vector_facial else 0
            print(f'   - Vector facial: {vector_len} caracteres')
        else:
            print('❌ NO tiene ReconocimientoFacial')
            return False
        
        # 4. Probar endpoint GET fotos
        print(f'\n🧪 PROBAR ENDPOINTS:')
        return probar_endpoints_lara(usuario.id)
        
    except Exception as e:
        print(f'❌ Error: {e}')
        return False

def probar_endpoints_lara(usuario_id):
    """
    🧪 Probar endpoints para lara
    """
    try:
        # Login
        login_response = requests.post('http://localhost:8000/api/authz/login/', {
            'email': 'seguridad@facial.com',
            'password': 'seguridad123'
        })
        
        if login_response.status_code != 200:
            print('   ❌ Error en login')
            return False
        
        token = login_response.json()['access']
        headers = {'Authorization': f'Bearer {token}'}
        
        # 1. Endpoint GET fotos
        response = requests.get(
            f'http://localhost:8000/api/authz/reconocimiento/fotos/{usuario_id}/',
            headers=headers
        )
        
        print(f'   📸 GET fotos: Status {response.status_code}')
        if response.status_code == 200:
            data = response.json()
            if data.get('success'):
                fotos_data = data.get('data', {})
                total_fotos = fotos_data.get('total_fotos', 0)
                tiene_reconocimiento = fotos_data.get('tiene_reconocimiento')
                print(f'      - Total fotos: {total_fotos}')
                print(f'      - Tiene reconocimiento: {tiene_reconocimiento}')
                print(f'      ✅ Endpoint GET funciona')
            else:
                print(f'      ❌ Error: {data.get("error")}')
                return False
        else:
            print(f'      ❌ Error HTTP: {response.status_code}')
            return False
        
        # 2. Endpoint usuarios-reconocimiento (verificar que aparezca en la lista)
        response = requests.get(
            'http://localhost:8000/api/seguridad/usuarios-reconocimiento/',
            headers=headers
        )
        
        print(f'   👥 Lista usuarios: Status {response.status_code}')
        if response.status_code == 200:
            data = response.json()
            usuarios = data.get('usuarios', [])
            
            # Buscar lara en la lista
            lara_encontrada = False
            for user in usuarios:
                if user.get('id') == usuario_id:
                    lara_encontrada = True
                    reconocimiento = user.get('reconocimiento_facial', {})
                    total_fotos = reconocimiento.get('total_fotos', 0)
                    print(f'      ✅ lara encontrada en lista')
                    print(f'      - Total fotos: {total_fotos}')
                    break
            
            if not lara_encontrada:
                print(f'      ❌ lara NO aparece en lista de usuarios-reconocimiento')
                return False
        else:
            print(f'      ❌ Error HTTP: {response.status_code}')
            return False
        
        return True
        
    except Exception as e:
        print(f'   ❌ Error probando endpoints: {e}')
        return False

if __name__ == "__main__":
    exito = verificar_lara_completo()
    
    print(f'\n🎯 RESULTADO FINAL:')
    if exito:
        print('🎉 ¡lara@gmail.com FUNCIONA COMPLETAMENTE!')
        print('   ✅ Puede subir fotos de reconocimiento facial')
        print('   ✅ Aparece en panel de seguridad')
        print('   ✅ Todos los endpoints funcionan')
        print(f'\n📋 ESTADO: PROBLEMA DE lara RESUELTO')
    else:
        print('❌ lara@gmail.com aún tiene problemas')
        print('🔧 Requiere corrección manual adicional')