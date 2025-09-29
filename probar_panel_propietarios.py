#!/usr/bin/env python3
"""
Script para probar los nuevos endpoints del panel de propietarios implementados
"""

import requests
import json
import sys
import io
from PIL import Image

BASE_URL = "http://localhost:8000"

def crear_imagen_test():
    """Crear una imagen de prueba en memoria"""
    # Crear imagen RGB de 100x100 pixels color azul
    img = Image.new('RGB', (100, 100), color='blue')
    
    # Guardar en buffer
    buffer = io.BytesIO()
    img.save(buffer, format='PNG')
    buffer.seek(0)
    
    return buffer

def login_propietario():
    """Login con usuario propietario"""
    print("🔐 INICIANDO SESIÓN COMO PROPIETARIO...")
    
    login_data = {
        'email': 'lara@gmail.com',
        'password': 'testing123'
    }
    
    response = requests.post(f"{BASE_URL}/api/authz/login/", json=login_data)
    
    if response.status_code == 200:
        data = response.json()
        token = data.get('access_token')
        print(f"✅ Login exitoso - Token obtenido")
        return token
    else:
        print(f"❌ Error en login: {response.status_code} - {response.text}")
        return None

def probar_mi_informacion(token):
    """Probar endpoint para obtener información del propietario"""
    print("\n📋 PROBANDO MI-INFORMACION...")
    
    headers = {'Authorization': f'Bearer {token}'}
    response = requests.get(f"{BASE_URL}/api/authz/propietarios/mi-informacion/", headers=headers)
    
    print(f"Status: {response.status_code}")
    
    if response.status_code == 200:
        data = response.json()
        print("✅ Información obtenida correctamente:")
        print(f"   • Email: {data.get('data', {}).get('email')}")
        print(f"   • Nombre: {data.get('data', {}).get('nombre_completo')}")
        print(f"   • Total fotos: {data.get('data', {}).get('total_fotos')}")
        print(f"   • Tiene reconocimiento: {data.get('data', {}).get('tiene_reconocimiento')}")
        return True
    else:
        print(f"❌ Error: {response.text}")
        return False

def probar_mis_fotos(token):
    """Probar endpoint para obtener fotos del propietario"""
    print("\n📸 PROBANDO MIS-FOTOS...")
    
    headers = {'Authorization': f'Bearer {token}'}
    response = requests.get(f"{BASE_URL}/api/authz/propietarios/mis-fotos/", headers=headers)
    
    print(f"Status: {response.status_code}")
    
    if response.status_code == 200:
        data = response.json()
        print("✅ Fotos obtenidas correctamente:")
        fotos_data = data.get('data', {})
        print(f"   • Total fotos: {fotos_data.get('total_fotos')}")
        print(f"   • Tiene reconocimiento: {fotos_data.get('tiene_reconocimiento')}")
        
        fotos_urls = fotos_data.get('fotos_urls', [])
        if fotos_urls:
            print(f"   • URLs de fotos:")
            for i, url in enumerate(fotos_urls[:3], 1):  # Mostrar solo las primeras 3
                print(f"     - Foto {i}: {url[:80]}...")
        
        return True
    else:
        print(f"❌ Error: {response.text}")
        return False

def probar_subir_foto(token):
    """Probar endpoint para subir foto de reconocimiento"""
    print("\n⬆️ PROBANDO SUBIR-FOTO...")
    
    # Crear imagen de prueba
    imagen_buffer = crear_imagen_test()
    
    headers = {'Authorization': f'Bearer {token}'}
    
    files = {
        'foto': ('test_propietario.png', imagen_buffer, 'image/png')
    }
    
    response = requests.post(
        f"{BASE_URL}/api/authz/propietarios/subir-foto/", 
        headers=headers, 
        files=files
    )
    
    print(f"Status: {response.status_code}")
    
    if response.status_code == 200:
        data = response.json()
        print("✅ Foto subida correctamente:")
        foto_data = data.get('data', {})
        print(f"   • URL: {foto_data.get('foto_url', '')[:80]}...")
        print(f"   • Total fotos: {foto_data.get('total_fotos')}")
        print(f"   • ID reconocimiento: {foto_data.get('reconocimiento_id')}")
        return True
    else:
        print(f"❌ Error: {response.text}")
        return False

def main():
    """Función principal"""
    print("🚀 PROBANDO ENDPOINTS DEL PANEL DE PROPIETARIOS")
    print("=" * 60)
    
    # 1. Login
    token = login_propietario()
    if not token:
        print("❌ No se pudo obtener token, terminando pruebas")
        sys.exit(1)
    
    # 2. Probar endpoints
    resultados = []
    
    # Mi información
    resultado_info = probar_mi_informacion(token)
    resultados.append(("Mi Información", resultado_info))
    
    # Mis fotos
    resultado_fotos = probar_mis_fotos(token)
    resultados.append(("Mis Fotos", resultado_fotos))
    
    # Subir foto
    resultado_subir = probar_subir_foto(token)
    resultados.append(("Subir Foto", resultado_subir))
    
    # Resumen
    print("\n" + "=" * 60)
    print("📊 RESUMEN DE PRUEBAS:")
    print("=" * 60)
    
    exitosos = 0
    for nombre, resultado in resultados:
        estado = "✅ EXITOSO" if resultado else "❌ FALLÓ"
        print(f"{nombre:<20} : {estado}")
        if resultado:
            exitosos += 1
    
    print(f"\nResultado final: {exitosos}/{len(resultados)} endpoints funcionando")
    
    if exitosos == len(resultados):
        print("\n🎉 ¡TODOS LOS ENDPOINTS DEL PANEL FUNCIONAN CORRECTAMENTE!")
        print("✅ Frontend puede usar estos endpoints sin problemas")
    else:
        print(f"\n⚠️ Hay {len(resultados) - exitosos} endpoints con problemas")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n⏹️ Pruebas interrumpidas por el usuario")
    except Exception as e:
        print(f"\n💥 Error inesperado: {e}")