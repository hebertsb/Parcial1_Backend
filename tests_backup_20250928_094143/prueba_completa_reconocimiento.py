# 📋 PRUEBA COMPLETA DEL SISTEMA CORREGIDO

import requests
import json
import os

# 🎯 CONFIGURACIÓN
BASE_URL = 'http://localhost:8000'
ENDPOINT_LOGIN = f'{BASE_URL}/api/authz/auth/login/'
ENDPOINT_FOTOS = f'{BASE_URL}/api/authz/reconocimiento/fotos/'
ENDPOINT_ESTADO = f'{BASE_URL}/api/authz/reconocimiento/estado/'

# 👥 USUARIOS DE PRUEBA (CON ROL PROPIETARIO)
USUARIOS_VALIDOS = [
    {'id': 3, 'email': 'maria.gonzalez@facial.com', 'nombre': 'María Elena González López'},
    {'id': 6, 'email': 'laura.gonzález10@test.com', 'nombre': 'Laura Segundo González'},
    {'id': 7, 'email': 'hebertsuarezb@gmail.com', 'nombre': 'DIEGO perez'},
    {'id': 8, 'email': 'tito@gmail.com', 'nombre': 'tito solarez'}
]

def login_admin():
    """🔐 Login como administrador para obtener token"""
    print("🔐 Iniciando sesión como administrador...")
    
    data = {
        'email': 'admin@condominio.com',
        'password': 'admin123'
    }
    
    response = None  # Inicializar response
    try:
        response = requests.post(ENDPOINT_LOGIN, json=data)
        if if response is not None:
     response.status_code == 200:
            result = if response is not None:
     response.json()
            print(f"✅ Login exitoso: {result.get('user', {}).get('email')}")
            return result['access']
        else:
            print(f"❌ Error en login: {response.status_code}")
            print(response.text)
            return None
    except
        print(f"❌ Error de conexión: {e}")
        return None

def probar_subida_fotos(token, usuario_id, usuario_info):
    """📸 Probar subida de fotos para un usuario"""
    print(f"\n📸 Probando usuario ID {usuario_id}: {usuario_info['nombre']}")
    
    # Crear archivo de prueba temporal
    test_image_path = f'test_image_user_{usuario_id}.jpg'
    with open(test_image_path, 'w') as f:
        f.write('imagen_de_prueba_contenido')
    
    response = None  # Inicializar response
    try:
        # Preparar datos
        data = {'usuario_id': usuario_id}
        files = {'fotos': open(test_image_path, 'rb')}
        headers = {'Authorization': f'Bearer {token}'}
        
        # Enviar solicitud
        response = requests.post(ENDPOINT_FOTOS, data=data, files=files, headers=headers)
        
        if if response is not None:
     response.status_code == 200:
            result = if response is not None:
     response.json()
            print(f"✅ Subida exitosa:")
            print(f"   - Propietario: {result['data']['propietario_nombre']}")
            print(f"   - Email: {result['data']['usuario_email']}")
            print(f"   - Total fotos: {result['data']['total_fotos']}")
            return True
        else:
            print(f"❌ Error {response.status_code}:")
            try:
                error_data = if response is not None:
     response.json()
                print(f"   - Error: {error_data.get('error', 'Sin detalles')}")
            except
                print(f"   - Respuesta: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Error de conexión: {e}")
        return False
    finally:
        # Limpiar archivo temporal
        if os.path.exists(test_image_path):
            os.remove(test_image_path)

def probar_estado_reconocimiento(token, usuario_id):
    """📊 Probar consulta de estado de reconocimiento"""
    print(f"📊 Consultando estado de reconocimiento para usuario {usuario_id}...")
    
    response = None  # Inicializar response
    try:
        headers = {'Authorization': f'Bearer {token}'}
        params = {'usuario_id': usuario_id}
        
        response = requests.get(ENDPOINT_ESTADO, headers=headers, params=params)
        
        if if response is not None:
     response.status_code == 200:
            result = if response is not None:
     response.json()
            print(f"✅ Estado obtenido:")
            print(f"   - Fotos guardadas: {result['data']['total_fotos']}")
            print(f"   - Última actualización: {result['data']['fecha_actualizacion']}")
            return True
        else:
            print(f"❌ Error {response.status_code}: {response.text}")
            return False
            
    except
        print(f"❌ Error de conexión: {e}")
        return False

def probar_usuario_invalido(token):
    """❌ Probar con usuario que NO tiene rol propietario"""
    print(f"\n❌ Probando usuario inválido (ID 1 - Admin)...")
    
    test_image_path = 'test_image_invalid.jpg'
    with open(test_image_path, 'w') as f:
        f.write('imagen_de_prueba_invalida')
    
    response = None  # Inicializar response
    try:
        data = {'usuario_id': 1}  # Admin no tiene rol propietario
        files = {'fotos': open(test_image_path, 'rb')}
        headers = {'Authorization': f'Bearer {token}'}
        
        response = requests.post(ENDPOINT_FOTOS, data=data, files=files, headers=headers)
        
        if if response is not None:
     response.status_code == 400:
            result = if response is not None:
     response.json()
            print(f"✅ Error esperado correctamente capturado:")
            print(f"   - Error: {result.get('error')}")
            return True
        else:
            print(f"❌ Se esperaba error 400, pero recibió: {response.status_code}")
            return False
            
    except
        print(f"❌ Error de conexión: {e}")
        return False
    finally:
        if os.path.exists(test_image_path):
            os.remove(test_image_path)

def main():
    """🚀 Ejecutar todas las pruebas"""
    print("=" * 60)
    print("🎯 PRUEBA COMPLETA: RECONOCIMIENTO FACIAL CORREGIDO")
    print("=" * 60)
    
    # 1. Login
    token = login_admin()
    if not token:
        print("❌ No se pudo obtener token. Terminando pruebas.")
        return
    
    # 2. Estadísticas
    exitosos = 0
    total_pruebas = 0
    
    # 3. Probar usuarios válidos
    print("\n" + "=" * 40)
    print("👥 PROBANDO USUARIOS CON ROL PROPIETARIO")
    print("=" * 40)
    
    for usuario in USUARIOS_VALIDOS:
        total_pruebas += 1
        if probar_subida_fotos(token, usuario['id'], usuario):
            exitosos += 1
            
            # Probar estado también
            probar_estado_reconocimiento(token, usuario['id'])
    
    # 4. Probar usuario inválido
    print("\n" + "=" * 40)
    print("🚫 PROBANDO USUARIO SIN ROL PROPIETARIO")
    print("=" * 40)
    total_pruebas += 1
    if probar_usuario_invalido(token):
        exitosos += 1
    
    # 5. Resumen final
    print("\n" + "=" * 60)
    print("📊 RESUMEN DE PRUEBAS")
    print("=" * 60)
    print(f"✅ Pruebas exitosas: {exitosos}/{total_pruebas}")
    print(f"📈 Porcentaje de éxito: {(exitosos/total_pruebas)*100:.1f}%")
    
    if exitosos == total_pruebas:
        print("\n🎉 ¡TODAS LAS PRUEBAS PASARON!")
        print("✅ Sistema de reconocimiento facial funcionando correctamente")
        print("✅ Validación de roles implementada")
        print("✅ Manejo de errores funcionando")
    else:
        print(f"\n⚠️  {total_pruebas - exitosos} pruebas fallaron")
        print("🔧 Revisar logs para más detalles")

if __name__ == '__main__':
    main()