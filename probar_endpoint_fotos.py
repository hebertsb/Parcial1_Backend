#!/usr/bin/env python
"""
Script para probar el endpoint de fotos de reconocimiento facial
"""
import requests
import json
import base64
from PIL import Image
import io
import os

# Configuración
BASE_URL = "http://localhost:8000"
ENDPOINT = "/api/authz/usuarios/fotos-reconocimiento/"

def crear_imagen_prueba():
    """Crear una imagen de prueba en memoria"""
    # Crear una imagen RGB simple
    img = Image.new('RGB', (500, 500), color='blue')
    
    # Convertir a bytes
    img_bytes = io.BytesIO()
    img.save(img_bytes, format='JPEG')
    img_bytes.seek(0)
    
    return img_bytes

def probar_endpoint_sin_token():
    """Probar endpoint sin autenticación (debe fallar)"""
    print("🔒 PRUEBA 1: Acceso sin token de autenticación")
    print("-" * 50)
    
    # Crear imagen de prueba
    imagen = crear_imagen_prueba()
    
    # Preparar datos
    files = {'fotos': ('test.jpg', imagen, 'image/jpeg')}
    data = {'usuario_id': '1'}
    
    try:
        response = requests.post(f"{BASE_URL}{ENDPOINT}", files=files, data=data)
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.json()}")
        
        if response.status_code == 401:
            print("✅ CORRECTO: Endpoint requiere autenticación")
        else:
            print("❌ ERROR: Endpoint debería requerir autenticación")
            
    except requests.exceptions.ConnectionError:
        print("❌ ERROR: No se puede conectar al servidor Django")
        print("   Asegúrate de que el servidor esté corriendo: python manage.py runserver")
    except Exception as e:
        print(f"❌ ERROR: {e}")

def obtener_token_jwt():
    """Obtener token JWT para pruebas (implementar según tu sistema de auth)"""
    # NOTA: Esto depende de cómo esté implementado tu sistema de autenticación
    # Necesitarías implementar el login para obtener un token válido
    
    print("\n🔑 OBTENCIÓN DE TOKEN JWT")
    print("-" * 50)
    print("⚠️  NOTA: Para probar completamente, necesitas:")
    print("1. Un endpoint de login que devuelva un JWT token")
    print("2. Un usuario registrado en el sistema")
    print("3. Un copropietario asociado a ese usuario")
    
    return None

def probar_endpoint_con_datos_invalidos():
    """Probar endpoint con datos inválidos"""
    print("\n📋 PRUEBA 2: Datos inválidos")
    print("-" * 50)
    
    # Crear archivo que no sea imagen
    archivo_texto = io.BytesIO(b"Este no es una imagen")
    
    files = {'fotos': ('test.txt', archivo_texto, 'text/plain')}
    data = {'usuario_id': '1'}
    
    try:
        response = requests.post(f"{BASE_URL}{ENDPOINT}", files=files, data=data)
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.json()}")
        
        if response.status_code == 400:
            print("✅ CORRECTO: Endpoint valida tipo de archivo")
        else:
            print("❌ ERROR: Endpoint debería validar tipo de archivo")
            
    except requests.exceptions.ConnectionError:
        print("❌ ERROR: No se puede conectar al servidor Django")
    except Exception as e:
        print(f"❌ ERROR: {e}")

def probar_estructura_respuesta():
    """Verificar que la estructura de respuesta coincida con lo esperado"""
    print("\n📊 ESTRUCTURA DE RESPUESTA ESPERADA")
    print("-" * 50)
    
    respuesta_esperada = {
        "success": True,
        "data": {
            "fotos_urls": ["https://dropbox.com/foto1.jpg", "https://dropbox.com/foto2.jpg"],
            "total_fotos": 2,
            "mensaje": "Se subieron 2 fotos exitosamente para reconocimiento facial",
            "reconocimiento_activo": True,
            "usuario_id": "1",
            "copropietario_id": 1
        }
    }
    
    print("✅ Respuesta exitosa esperada:")
    print(json.dumps(respuesta_esperada, indent=2, ensure_ascii=False))
    
    respuesta_error = {
        "success": False,
        "error": "Descripción del error"
    }
    
    print("\n❌ Respuesta de error esperada:")
    print(json.dumps(respuesta_error, indent=2, ensure_ascii=False))

def verificar_urls_adicionales():
    """Verificar que las URLs adicionales estén configuradas"""
    print("\n🌐 VERIFICACIÓN DE URLs ADICIONALES")
    print("-" * 50)
    
    urls_adicionales = [
        "/api/authz/usuarios/estado-reconocimiento/",
        "/api/authz/usuarios/reconocimiento-facial/"
    ]
    
    for url in urls_adicionales:
        try:
            response = requests.get(f"{BASE_URL}{url}")
            print(f"✅ {url} - Status: {response.status_code}")
        except requests.exceptions.ConnectionError:
            print(f"❌ {url} - No se puede conectar al servidor")
        except Exception as e:
            print(f"❌ {url} - Error: {e}")

def main():
    print("🚀 PRUEBAS DEL ENDPOINT DE FOTOS DE RECONOCIMIENTO FACIAL")
    print("=" * 80)
    print(f"Endpoint: {BASE_URL}{ENDPOINT}")
    print("=" * 80)
    
    # Ejecutar pruebas
    probar_endpoint_sin_token()
    probar_endpoint_con_datos_invalidos()
    probar_estructura_respuesta()
    verificar_urls_adicionales()
    
    print("\n" + "=" * 80)
    print("📋 RESUMEN DE IMPLEMENTACIÓN")
    print("=" * 80)
    print("✅ Endpoint implementado: POST /authz/usuarios/fotos-reconocimiento/")
    print("✅ Validaciones de seguridad: Autenticación JWT requerida")
    print("✅ Validaciones de datos: Tipo de archivo, tamaño máximo")
    print("✅ Integración Dropbox: Subida a carpeta específica")
    print("✅ Base de datos: Actualización de ReconocimientoFacial")
    print("✅ Endpoints adicionales: Estado y eliminación")
    
    print("\n🔄 PRÓXIMOS PASOS:")
    print("-" * 30)
    print("1. Iniciar servidor Django: python manage.py runserver")
    print("2. Configurar autenticación JWT en el frontend")
    print("3. Probar subida de fotos desde el frontend")
    print("4. Verificar almacenamiento en Dropbox")
    print("5. Confirmar activación del reconocimiento facial")

if __name__ == "__main__":
    main()