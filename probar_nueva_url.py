#!/usr/bin/env python
"""
Probar la nueva URL del endpoint después del fix
"""
import requests
import json

def probar_nueva_url():
    print("🚀 PROBANDO NUEVA URL - FIX DEL ERROR 405")
    print("=" * 60)
    
    base_url = "http://localhost:8000"
    
    # Nueva URL del endpoint
    nueva_url = f"{base_url}/api/authz/reconocimiento/fotos/"
    
    # URL del diagnóstico
    diagnostico_url = f"{base_url}/api/authz/reconocimiento/diagnostico/"
    
    print(f"🎯 Nueva URL: {nueva_url}")
    print(f"🔧 Diagnóstico: {diagnostico_url}")
    
    # Obtener token
    login_url = f"{base_url}/api/authz/login/"
    credentials = {"email": "test@facial.com", "password": "test123"}
    
    try:
        print("\n🔑 1. OBTENIENDO TOKEN...")
        login_response = requests.post(login_url, json=credentials)
        if login_response.status_code != 200:
            print(f"❌ Error en login: {login_response.status_code}")
            return
        
        token = login_response.json().get('access')
        headers = {'Authorization': f'Bearer {token}'}
        print(f"✅ Token obtenido")
        
        # Probar endpoint de diagnóstico primero
        print("\n🧪 2. PROBANDO ENDPOINT DE DIAGNÓSTICO:")
        diag_response = requests.get(diagnostico_url, headers=headers)
        print(f"   GET Status: {diag_response.status_code}")
        if diag_response.status_code == 200:
            print("   ✅ Diagnóstico GET funcionando")
        
        diag_post = requests.post(diagnostico_url, headers=headers, json={'test': 'data'})
        print(f"   POST Status: {diag_post.status_code}")
        if diag_post.status_code == 200:
            print("   ✅ Diagnóstico POST funcionando")
        
        # Probar nuevo endpoint principal
        print("\n🎯 3. PROBANDO NUEVO ENDPOINT PRINCIPAL:")
        
        # Primero probar GET (debería dar 405 porque solo acepta POST)
        get_response = requests.get(nueva_url, headers=headers)
        print(f"   GET Status: {get_response.status_code}")
        if get_response.status_code == 405:
            print("   ✅ GET da 405 (correcto, solo acepta POST)")
        
        # Ahora probar POST (el método que debería funcionar)
        data = {'usuario_id': '8'}
        files = {'fotos': ('test.jpg', b'fake_image_data', 'image/jpeg')}
        
        post_response = requests.post(nueva_url, headers=headers, data=data, files=files)
        print(f"   POST Status: {post_response.status_code}")
        
        if post_response.status_code == 200:
            print("   🎉 ¡ÉXITO! POST funciona correctamente")
            try:
                result = post_response.json()
                print(f"   Respuesta: {json.dumps(result, indent=2)}")
            except:
                print(f"   Respuesta texto: {post_response.text}")
                
        elif post_response.status_code == 400:
            print("   ⚠️ Error de validación (esperado con datos de prueba)")
            try:
                error = post_response.json()
                print(f"   Error: {json.dumps(error, indent=2)}")
            except:
                print(f"   Error texto: {post_response.text}")
                
        elif post_response.status_code == 405:
            print("   ❌ AÚN DA 405 - revisar configuración")
            
        else:
            print(f"   ⚠️ Código inesperado: {post_response.status_code}")
            print(f"   Respuesta: {post_response.text}")
        
        # Probar la URL antigua para confirmar que ya no funciona
        print("\n🔍 4. VERIFICANDO QUE LA URL ANTIGUA NO FUNCIONA:")
        url_antigua = f"{base_url}/api/authz/usuarios/fotos-reconocimiento/"
        old_response = requests.post(url_antigua, headers=headers, data=data, files=files)
        print(f"   URL antigua Status: {old_response.status_code}")
        
        if old_response.status_code == 405:
            print("   ✅ URL antigua da 405 (confirma que el problema era el conflicto)")
        
    except Exception as e:
        print(f"❌ Error: {e}")

def mostrar_resumen():
    print("\n📋 RESUMEN DE LA SOLUCIÓN")
    print("=" * 60)
    print("🔍 PROBLEMA IDENTIFICADO:")
    print("   - Conflicto entre router DRF (/usuarios/) y endpoint personalizado")
    print("   - Django interpretaba /usuarios/fotos-reconocimiento/ como /usuarios/{id}/")
    print("   - UsuarioViewSet capturaba la URL antes que nuestro endpoint")
    print()
    print("✅ SOLUCIÓN IMPLEMENTADA:")
    print("   - Cambio de URL: /usuarios/fotos-reconocimiento/ → /reconocimiento/fotos/")
    print("   - Nueva URL completa: /api/authz/reconocimiento/fotos/")
    print("   - Evita conflicto con el router de usuarios")
    print()
    print("🎯 RESULTADO ESPERADO:")
    print("   - POST /api/authz/reconocimiento/fotos/ → 200 OK o 400 Bad Request")
    print("   - GET /api/authz/reconocimiento/fotos/ → 405 Method Not Allowed (correcto)")

if __name__ == "__main__":
    probar_nueva_url()
    mostrar_resumen()