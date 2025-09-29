#!/usr/bin/env python
"""
Prueba completa del endpoint con autenticación real
"""
import requests
import json

def obtener_token():
    """Obtener token JWT para las pruebas"""
    print("🔑 OBTENIENDO TOKEN DE AUTENTICACIÓN")
    print("-" * 40)
    
    login_url = "http://localhost:8000/api/authz/login/"
    
    # Credenciales de admin por defecto (usando email como identificador)
    credentials = {
        "email": "test@facial.com",
        "password": "test123"
    }
    
    try:
        response = requests.post(login_url, json=credentials)
        print(f"Login Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            token = data.get('access')
            if token:
                print("✅ Token obtenido exitosamente")
                return token
            else:
                print("❌ No se encontró token en la respuesta")
                print(f"Respuesta: {data}")
                return None
        else:
            print(f"❌ Error en login: {response.status_code}")
            print(f"Respuesta: {response.text}")
            return None
            
    except Exception as e:
        print(f"❌ Error de conexión: {e}")
        return None

def probar_endpoint_con_auth(token):
    """Probar el endpoint con autenticación"""
    print("\n📸 PROBANDO ENDPOINT CON AUTENTICACIÓN")
    print("-" * 40)
    
    endpoint = "http://localhost:8000/api/authz/usuarios/fotos-reconocimiento/"
    
    headers = {
        'Authorization': f'Bearer {token}'
    }
    
    # Crear datos de prueba (simulando FormData)
    data = {
        'usuario_id': '8'  # ID del usuario copropietario
    }
    
    # Simular archivo (el frontend envía archivos reales)
    files = {
        'fotos': ('test.jpg', b'fake_image_data', 'image/jpeg')
    }
    
    try:
        print("Enviando POST con:")
        print(f"  - Headers: Authorization Bearer {token[:20]}...")
        print(f"  - Data: {data}")
        print(f"  - Files: {list(files.keys())}")
        
        response = requests.post(endpoint, headers=headers, data=data, files=files)
        
        print(f"\n📋 RESPUESTA:")
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            print("✅ ¡ÉXITO! El endpoint funciona correctamente")
            try:
                resultado = response.json()
                print(f"Respuesta JSON: {json.dumps(resultado, indent=2)}")
            except:
                print(f"Respuesta texto: {response.text}")
        elif response.status_code == 400:
            print("⚠️ Error de validación (esperado con datos de prueba)")
            try:
                error = response.json()
                print(f"Error: {json.dumps(error, indent=2)}")
            except:
                print(f"Error texto: {response.text}")
        elif response.status_code == 401:
            print("❌ Token inválido o expirado")
        elif response.status_code == 405:
            print("❌ Método no permitido - AÚN HAY PROBLEMA")
        else:
            print(f"⚠️ Código inesperado: {response.status_code}")
            print(f"Respuesta: {response.text}")
            
        return response.status_code
        
    except Exception as e:
        print(f"❌ Error en la petición: {e}")
        return None

def verificar_usuarios_disponibles(token):
    """Verificar qué usuarios copropietarios existen"""
    print("\n👥 VERIFICANDO USUARIOS DISPONIBLES")
    print("-" * 40)
    
    endpoint = "http://localhost:8000/api/authz/copropietarios/"
    headers = {'Authorization': f'Bearer {token}'}
    
    try:
        response = requests.get(endpoint, headers=headers)
        if response.status_code == 200:
            usuarios = response.json()
            print(f"Usuarios encontrados: {len(usuarios)}")
            for usuario in usuarios[:3]:  # Mostrar solo los primeros 3
                print(f"  - ID: {usuario.get('id')}, Usuario: {usuario.get('usuario', {}).get('username', 'N/A')}")
            return usuarios
        else:
            print(f"No se pudieron obtener usuarios: {response.status_code}")
            return []
    except Exception as e:
        print(f"Error: {e}")
        return []

def main():
    print("🧪 PRUEBA COMPLETA DEL SISTEMA DE RECONOCIMIENTO FACIAL")
    print("=" * 60)
    
    # 1. Obtener token
    token = obtener_token()
    if not token:
        print("\n❌ No se pudo obtener token. Verifica:")
        print("  - Que el servidor esté corriendo")
        print("  - Que exista un usuario 'admin' con contraseña 'admin123'")
        print("  - O ajusta las credenciales en el script")
        return
    
    # 2. Verificar usuarios disponibles
    usuarios = verificar_usuarios_disponibles(token)
    
    # 3. Probar endpoint principal
    status = probar_endpoint_con_auth(token)
    
    # 4. Conclusión
    print("\n🎯 CONCLUSIÓN")
    print("=" * 40)
    if status == 200:
        print("✅ SISTEMA FUNCIONANDO PERFECTAMENTE")
        print("   El frontend debe funcionar sin problemas")
    elif status == 400:
        print("✅ ENDPOINT FUNCIONANDO (error de validación esperado)")
        print("   El problema está en los datos que envía el frontend")
    elif status == 401:
        print("❌ PROBLEMA DE AUTENTICACIÓN")
        print("   Verificar que el frontend envíe el token correctamente")
    elif status == 405:
        print("❌ AÚN HAY PROBLEMA CON EL MÉTODO")
        print("   Necesitamos revisar la configuración de Django")
    else:
        print("⚠️ RESULTADO INESPERADO")
        print("   Revisar logs del servidor Django")

if __name__ == "__main__":
    main()