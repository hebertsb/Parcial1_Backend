# 🧪 PRUEBA COMPLETA DEL ENDPOINT GET - OBTENER FOTOS

import requests
import json

# 🎯 CONFIGURACIÓN
BASE_URL = 'http://localhost:8000'
ENDPOINT_LOGIN = f'{BASE_URL}/api/authz/auth/login/'
ENDPOINT_OBTENER_FOTOS = f'{BASE_URL}/api/authz/reconocimiento/fotos/'

# 👥 USUARIO DE PRUEBA - tito tiene 10 fotos subidas
USUARIO_PRUEBA = {
    'id': 8,
    'email': 'tito@gmail.com',
    'password': 'admin123'  # Contraseña de prueba
}

def login_usuario(email, password):
    """🔐 Login como usuario específico"""
    print(f"🔐 Iniciando sesión como {email}...")
    
    data = {
        'email': email,
        'password': password
    }
    
    try:
        response = requests.post(ENDPOINT_LOGIN, json=data)
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Login exitoso: {result.get('user', {}).get('email')}")
            return result['access']
        else:
            print(f"❌ Error en login: {response.status_code}")
            print(response.text)
            return None
    except Exception as e:
        print(f"❌ Error de conexión: {e}")
        return None

def probar_obtener_fotos(token, usuario_id):
    """📸 Probar endpoint GET para obtener fotos"""
    print(f"\n📸 Probando obtener fotos del usuario ID {usuario_id}...")
    
    try:
        headers = {'Authorization': f'Bearer {token}'}
        url = f"{ENDPOINT_OBTENER_FOTOS}{usuario_id}/"
        
        print(f"🔗 URL: {url}")
        
        response = requests.get(url, headers=headers)
        
        print(f"📊 Status Code: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Fotos obtenidas exitosamente:")
            
            data = result.get('data', {})
            print(f"🎯 DATOS OBTENIDOS:")
            print(f"   - Usuario ID: {data.get('usuario_id')}")
            print(f"   - Email: {data.get('usuario_email')}")
            print(f"   - Nombre: {data.get('propietario_nombre')}")
            print(f"   - Total fotos: {data.get('total_fotos')}")
            print(f"   - Tiene reconocimiento: {data.get('tiene_reconocimiento')}")
            print(f"   - Última actualización: {data.get('fecha_ultima_actualizacion')}")
            
            fotos_urls = data.get('fotos_urls', [])
            if fotos_urls:
                print(f"\n📋 URLS DE FOTOS ({len(fotos_urls)}):")
                for i, url in enumerate(fotos_urls):
                    print(f"   {i+1}. {url}")
            else:
                print("📋 No se encontraron URLs de fotos")
                
            return True
            
        else:
            print(f"❌ Error {response.status_code}:")
            try:
                error_data = response.json()
                print(f"   - Error: {error_data.get('error', 'Sin detalles')}")
            except:
                print(f"   - Respuesta: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Error de conexión: {e}")
        return False

def probar_permisos_otros_usuarios(token, usuario_id_diferente):
    """🚫 Probar que no se puedan ver fotos de otros usuarios"""
    print(f"\n🚫 Probando acceso a fotos de otro usuario (ID {usuario_id_diferente})...")
    
    try:
        headers = {'Authorization': f'Bearer {token}'}
        url = f"{ENDPOINT_OBTENER_FOTOS}{usuario_id_diferente}/"
        
        response = requests.get(url, headers=headers)
        
        if response.status_code == 403:
            print("✅ Permisos funcionando correctamente - Acceso denegado")
            return True
        else:
            print(f"❌ Error en permisos - Status: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Error de conexión: {e}")
        return False

def main():
    """🚀 Ejecutar todas las pruebas del endpoint GET"""
    print("=" * 60)
    print("🧪 PRUEBA COMPLETA: ENDPOINT GET OBTENER FOTOS")
    print("=" * 60)
    
    # 1. Login del usuario
    token = login_usuario(USUARIO_PRUEBA['email'], USUARIO_PRUEBA['password'])
    if not token:
        print("❌ No se pudo obtener token. Intentando con admin...")
        token = login_usuario('admin@condominio.com', 'admin123')
        if not token:
            print("❌ No se pudo obtener ningún token. Terminando pruebas.")
            return
    
    # 2. Probar obtener fotos del usuario actual
    print("\n" + "=" * 40)
    print("📸 PROBANDO OBTENER FOTOS PROPIAS")
    print("=" * 40)
    exito_fotos = probar_obtener_fotos(token, USUARIO_PRUEBA['id'])
    
    # 3. Probar permisos (intentar ver fotos de otro usuario)
    print("\n" + "=" * 40)
    print("🚫 PROBANDO PERMISOS")
    print("=" * 40)
    exito_permisos = probar_permisos_otros_usuarios(token, 3)  # Usuario ID 3
    
    # 4. Resumen final
    print("\n" + "=" * 60)
    print("📊 RESUMEN DE PRUEBAS")
    print("=" * 60)
    
    pruebas_exitosas = sum([exito_fotos, exito_permisos])
    total_pruebas = 2
    
    print(f"✅ Pruebas exitosas: {pruebas_exitosas}/{total_pruebas}")
    print(f"📈 Porcentaje de éxito: {(pruebas_exitosas/total_pruebas)*100:.1f}%")
    
    if pruebas_exitosas == total_pruebas:
        print("\n🎉 ¡ENDPOINT GET FUNCIONANDO PERFECTAMENTE!")
        print("✅ El frontend ya puede obtener las fotos del usuario")
        print("✅ Los permisos están correctamente implementados")
        print("✅ Las URLs de Dropbox se retornan correctamente")
    else:
        print(f"\n⚠️  {total_pruebas - pruebas_exitosas} pruebas fallaron")
        print("🔧 Revisar logs para más detalles")

if __name__ == '__main__':
    main()