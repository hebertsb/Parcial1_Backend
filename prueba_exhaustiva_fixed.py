#!/usr/bin/env python
"""
Prueba exhaustiva del endpoint con diferentes métodos HTTP
"""
import requests
import json

def probar_todos_los_metodos():
    print("🔍 PRUEBA EXHAUSTIVA DE MÉTODOS HTTP")
    print("=" * 60)
    
    base_url = "http://localhost:8000"
    endpoint = "/api/authz/usuarios/fotos-reconocimiento/"
    full_url = f"{base_url}{endpoint}"
    
    # Obtener token primero
    login_url = f"{base_url}/api/authz/login/"
    credentials = {"email": "test@facial.com", "password": "test123"}
    
    try:
        print("🔑 1. OBTENIENDO TOKEN...")
        login_response = requests.post(login_url, json=credentials)
        if login_response.status_code != 200:
            print(f"❌ Error en login: {login_response.status_code}")
            print(f"Respuesta: {login_response.text}")
            return
        
        token = login_response.json().get('access')
        headers = {'Authorization': f'Bearer {token}'}
        print(f"✅ Token obtenido: {token[:20]}...")
        
        # Probar diferentes métodos
        metodos = ['GET', 'POST', 'PUT', 'DELETE', 'PATCH', 'OPTIONS']
        
        for metodo in metodos:
            print(f"\n🧪 2.{metodos.index(metodo)+1} PROBANDO {metodo}:")
            
            response = None  # Inicializar response
            try:
                if metodo == 'GET':
                    response = requests.get(full_url, headers=headers)
                elif metodo == 'POST':
                    # Usar FormData para POST
                    data = {'usuario_id': '8'}
                    files = {'fotos': ('test.jpg', b'fake_image_data', 'image/jpeg')}
                    response = requests.post(full_url, headers=headers, data=data, files=files)
                elif metodo == 'PUT':
                    response = requests.put(full_url, headers=headers, json={'test': 'data'})
                elif metodo == 'DELETE':
                    response = requests.delete(full_url, headers=headers)
                elif metodo == 'PATCH':
                    response = requests.patch(full_url, headers=headers, json={'test': 'data'})
                elif metodo == 'OPTIONS':
                    response = requests.options(full_url, headers=headers)
                
                # Verificar que response esté definido antes de usarlo
                if response is not None:
                    print(f"   Status: {response.status_code}")
                    
                    # Mostrar headers importantes
                    if 'Allow' in response.headers:
                        print(f"   Métodos permitidos: {response.headers['Allow']}")
                    
                    # Mostrar contenido si es relevante
                    if response.status_code == 405:
                        print("   ❌ MÉTODO NO PERMITIDO")
                    elif response.status_code == 401:
                        print("   ⚠️ No autorizado (pero método aceptado)")
                    elif response.status_code == 400:
                        print("   ⚠️ Datos inválidos (pero método aceptado)")
                    elif response.status_code == 200:
                        print("   ✅ ÉXITO")
                    else:
                        print(f"   ⚠️ Código: {response.status_code}")
                    
                    # Mostrar contenido de error si es 405
                    if response.status_code == 405:
                        try:
                            error_content = response.json()
                            print(f"   Error: {error_content}")
                        except:
                            print(f"   Error texto: {response.text}")
                else:
                    print("   ❌ No se pudo realizar la petición")
                        
            except Exception as e:
                print(f"   ❌ Error en petición: {e}")
    
    except Exception as e:
        print(f"❌ Error general: {e}")

def verificar_urls_django():
    print("\n🔍 VERIFICACIÓN DE URLs DJANGO")
    print("=" * 60)
    
    import os
    import django
    
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
    django.setup()
    
    from django.urls import resolve
    
    path = "/api/authz/usuarios/fotos-reconocimiento/"
    
    try:
        match = resolve(path)
        print(f"✅ URL resolve:")
        print(f"   Función: {match.func}")
        print(f"   Nombre: {match.url_name}")
        print(f"   Args: {match.args}")
        print(f"   Kwargs: {match.kwargs}")
        
        # Verificar decoradores de la función de forma segura
        func = match.func
        func_attrs = [attr for attr in dir(func) if not attr.startswith('_')]
        print(f"   Atributos disponibles: {func_attrs[:5]}...")  # Mostrar solo los primeros 5
        
        # Verificar atributos específicos de forma segura
        if hasattr(func, 'cls'):
            cls_attr = getattr(func, 'cls', None)
            print(f"   Clase wrapper: {cls_attr}")
        if hasattr(func, 'actions'):
            actions_attr = getattr(func, 'actions', None)
            print(f"   Acciones: {actions_attr}")
            
    except Exception as e:
        print(f"❌ Error en resolve: {e}")

if __name__ == "__main__":
    verificar_urls_django()
    probar_todos_los_metodos()