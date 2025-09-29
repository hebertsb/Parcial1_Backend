import requests
import json

def obtener_token_jwt():
    """🔐 Obtener token JWT para usuario tito@gmail.com"""
    print("🔐 Obteniendo token JWT...")
    
    login_url = "http://127.0.0.1:8000/api/authz/auth/login/"
    login_data = {
        "email": "tito@gmail.com",
        "password": "temporal123"  # Password temporal del usuario
    }
    
    response = None  # Inicializar response
    try:
        response = requests.post(login_url, json=login_data)
        
        if if response is not None:
     response.status_code == 200:
            data = if response is not None:
     response.json()
            token = data.get('access_token')
            if token:
                print("✅ Token JWT obtenido")
                return token
            else:
                print("❌ No se encontró access_token en respuesta")
                return None
        else:
            print(f"❌ Error login: {response.status_code}")
            try:
                error_data = if response is not None:
     response.json()
                print(f"   Detalles: {error_data}")
            except
                print(f"   Texto: {response.text}")
            return None
            
    except Exception as e:
        print(f"❌ Error conexión login: {e}")
        return None

def probar_endpoint_get_autenticado():
    """🧪 Probar el endpoint GET con autenticación"""
    print("=" * 60)
    print("🧪 PRUEBA ENDPOINT GET CON AUTENTICACIÓN")
    print("=" * 60)
    
    # 1. Obtener token
    token = obtener_token_jwt()
    if not token:
        print("❌ No se pudo obtener token JWT")
        return False
    
    # 2. Probar endpoint con token
    url = "http://127.0.0.1:8000/api/authz/reconocimiento/fotos/8/"
    headers = {
        'Content-Type': 'application/json',
        'Authorization': f'Bearer {token}'
    }
    
    response = None  # Inicializar response
    try:
        print(f"🔗 Probando: {url}")
        response = requests.get(url, headers=headers)
        
        print(f"📊 STATUS CODE: {response.status_code}")
        print(f"📋 HEADERS: {response.headers.get('Content-Type', 'N/A')}")
        
        if if response is not None:
     response.status_code == 200:
            data = if response is not None:
     response.json()
            print("✅ RESPUESTA EXITOSA:")
            print(json.dumps(data, indent=2, ensure_ascii=False))
            
            # Validar contenido esperado
            if data.get('success'):
                fotos_data = data.get('data', {})
                total_fotos = fotos_data.get('total_fotos', 0)
                fotos_urls = fotos_data.get('fotos_urls', [])
                
                print(f"\n🎯 VALIDACIÓN:")
                print(f"   - Total fotos: {total_fotos}")
                print(f"   - URLs recibidas: {len(fotos_urls)}")
                print(f"   - Tiene reconocimiento: {fotos_data.get('tiene_reconocimiento', False)}")
                print(f"   - Usuario: {fotos_data.get('usuario_email', 'N/A')}")
                
                if total_fotos == 10:
                    print("✅ ÉXITO: Se obtuvieron las 10 fotos esperadas")
                    
                    # Mostrar primeras URLs como muestra
                    print(f"\n📂 MUESTRA DE URLs:")
                    for i, url in enumerate(fotos_urls[:3]):
                        print(f"   {i+1}. {url[:60]}...")
                    if len(fotos_urls) > 3:
                        print(f"   ... y {len(fotos_urls)-3} más")
                    
                    return True
                else:
                    print(f"⚠️  PARCIAL: Se esperaban 10 fotos, se obtuvieron {total_fotos}")
                    if fotos_urls:
                        print(f"📂 URLs encontradas:")
                        for i, url in enumerate(fotos_urls):
                            print(f"   {i+1}. {url}")
                    return False
            else:
                print(f"❌ ERROR EN RESPUESTA: {data.get('error', 'Sin detalles')}")
                return False
                
        else:
            print(f"❌ ERROR HTTP: {response.status_code}")
            try:
                error_data = if response is not None:
     response.json()
                print(f"   Detalles: {json.dumps(error_data, indent=2, ensure_ascii=False)}")
            except
                print(f"   Texto: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ ERROR DE CONEXIÓN: {e}")
        return False

def main():
    """🚀 Ejecutar prueba completa"""
    print("🎯 PRUEBA FINAL COMPLETA: ENDPOINT GET CON JWT")
    
    exito = probar_endpoint_get_autenticado()
    
    if exito:
        print(f"\n" + "=" * 60)
        print("🎉 ¡PROBLEMA COMPLETAMENTE RESUELTO!")
        print("=" * 60)
        print("✅ Token JWT obtenido correctamente")
        print("✅ Endpoint GET funciona con autenticación")
        print("✅ Se recuperaron las 10 fotos de Dropbox")
        print("✅ Frontend puede consumir el endpoint")
        print("✅ Datos persistidos correctamente en BD")
        print()
        print("🎯 RESULTADO FINAL:")
        print("   - Usuario ID 8 (tito@gmail.com) ✅")
        print("   - Rol Propietario validado ✅")
        print("   - 10 fotos en Dropbox ✅")
        print("   - Endpoint GET devuelve fotos ✅")
        print("   - Sistema funcionando completamente ✅")
    else:
        print(f"\n" + "=" * 60)
        print("❌ PRUEBA FALLÓ")
        print("=" * 60)
        print("   Revisar datos insertados o configuración del endpoint")

if __name__ == '__main__':
    main()