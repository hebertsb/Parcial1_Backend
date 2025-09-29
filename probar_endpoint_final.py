import requests
import json

def probar_endpoint_get():
    """🧪 Probar el endpoint GET corregido"""
    print("=" * 60)
    print("🧪 PRUEBA ENDPOINT GET CORREGIDO")
    print("=" * 60)
    
    # URL del endpoint GET
    url = "http://127.0.0.1:8000/api/authz/reconocimiento/fotos/8/"
    
    # Headers con autenticación si necesaria
    headers = {
        'Content-Type': 'application/json',
        # Agregar token JWT si es necesario
    }
    
    try:
        print(f"🔗 Probando: {url}")
        response = requests.get(url, headers=headers)
        
        print(f"📊 STATUS CODE: {response.status_code}")
        print(f"📋 HEADERS: {response.headers.get('Content-Type', 'N/A')}")
        
        if response.status_code == 200:
            data = response.json()
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
                
                if total_fotos == 10:
                    print("✅ ÉXITO: Se obtuvieron las 10 fotos esperadas")
                    return True
                else:
                    print(f"⚠️  PARCIAL: Se esperaban 10 fotos, se obtuvieron {total_fotos}")
                    return False
            else:
                print(f"❌ ERROR EN RESPUESTA: {data.get('error', 'Sin detalles')}")
                return False
                
        else:
            print(f"❌ ERROR HTTP: {response.status_code}")
            try:
                error_data = response.json()
                print(f"   Detalles: {error_data}")
            except:
                print(f"   Texto: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ ERROR DE CONEXIÓN: {e}")
        return False

def main():
    """🚀 Ejecutar prueba"""
    print("🎯 PRUEBA FINAL: ENDPOINT GET FOTOS RECONOCIMIENTO")
    
    exito = probar_endpoint_get()
    
    if exito:
        print(f"\n" + "=" * 60)
        print("🎉 ¡PRUEBA EXITOSA!")
        print("=" * 60)
        print("✅ El endpoint GET funciona correctamente")
        print("✅ Se recuperaron las 10 fotos de Dropbox")
        print("✅ Frontend puede mostrar las fotos del usuario")
        print("✅ Problema completamente resuelto")
    else:
        print(f"\n" + "=" * 60)
        print("❌ PRUEBA FALLÓ")
        print("=" * 60)
        print("   Revisar servidor Django y configuración")

if __name__ == '__main__':
    main()