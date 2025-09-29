#!/usr/bin/env python
"""
Script para diagnosticar el problema del endpoint 405
"""
import requests
import json

def diagnosticar_endpoint():
    print("🔍 DIAGNÓSTICO DETALLADO DEL ENDPOINT")
    print("=" * 60)
    
    base_url = "http://localhost:8000"
    endpoint = "/api/authz/usuarios/fotos-reconocimiento/"
    
    print(f"🌐 Probando: {base_url}{endpoint}")
    print("-" * 60)
    
    # 1. Probar GET (para ver si existe)
    print("\n1️⃣ PRUEBA GET (verificar si existe):")
    try:
        response = requests.get(f"{base_url}{endpoint}")
        print(f"   Status: {response.status_code}")
        if response.status_code == 405:
            print("   ✅ Endpoint existe pero no acepta GET (esperado)")
        elif response.status_code == 401:
            print("   ✅ Endpoint existe y requiere autenticación (esperado)")
        elif response.status_code == 404:
            print("   ❌ Endpoint NO EXISTE - revisar URLs")
        else:
            print(f"   ⚠️ Respuesta inesperada: {response.status_code}")
    except requests.exceptions.ConnectionError:
        print("   ❌ No se puede conectar al servidor")
        return
    
    # 2. Probar OPTIONS (para ver métodos permitidos)
    print("\n2️⃣ PRUEBA OPTIONS (métodos permitidos):")
    try:
        response = requests.options(f"{base_url}{endpoint}")
        print(f"   Status: {response.status_code}")
        if 'Allow' in response.headers:
            print(f"   Métodos permitidos: {response.headers['Allow']}")
        else:
            print("   No se encontró header 'Allow'")
    except Exception as e:
        print(f"   Error: {e}")
    
    # 3. Probar POST sin autenticación
    print("\n3️⃣ PRUEBA POST (sin autenticación):")
    try:
        data = {'usuario_id': '8', 'fotos': 'test'}
        response = requests.post(f"{base_url}{endpoint}", data=data)
        print(f"   Status: {response.status_code}")
        if response.status_code == 401:
            print("   ✅ POST funciona pero requiere autenticación (CORRECTO)")
        elif response.status_code == 405:
            print("   ❌ POST NO PERMITIDO - PROBLEMA AQUÍ")
        elif response.status_code == 400:
            print("   ✅ POST funciona pero datos inválidos (esperado)")
        else:
            print(f"   ⚠️ Respuesta: {response.status_code}")
            if response.content:
                try:
                    print(f"   Contenido: {response.json()}")
                except:
                    print(f"   Contenido: {response.text}")
    except Exception as e:
        print(f"   Error: {e}")
    
    # 4. Verificar otros endpoints
    print("\n4️⃣ VERIFICAR OTROS ENDPOINTS:")
    otros_endpoints = [
        "/api/authz/usuarios/estado-reconocimiento/",
        "/api/authz/usuarios/reconocimiento-facial/"
    ]
    
    for ep in otros_endpoints:
        try:
            response = requests.get(f"{base_url}{ep}")
            print(f"   {ep}: {response.status_code}")
        except:
            print(f"   {ep}: ERROR DE CONEXIÓN")

def verificar_configuracion_django():
    print("\n🔧 VERIFICACIÓN DE CONFIGURACIÓN DJANGO")
    print("=" * 60)
    
    # Verificar si los archivos existen
    archivos_importantes = [
        "authz/views_fotos_reconocimiento.py",
        "authz/urls.py"
    ]
    
    for archivo in archivos_importantes:
        try:
            with open(archivo, 'r', encoding='utf-8') as f:
                contenido = f.read()
                if 'subir_fotos_reconocimiento' in contenido:
                    print(f"   ✅ {archivo}: Función encontrada")
                else:
                    print(f"   ❌ {archivo}: Función NO encontrada")
        except FileNotFoundError:
            print(f"   ❌ {archivo}: Archivo NO existe")
        except Exception as e:
            print(f"   ⚠️ {archivo}: Error - {e}")

def mostrar_solucion():
    print("\n🚀 SOLUCIÓN PASO A PASO")
    print("=" * 60)
    print("Si el diagnóstico muestra que POST no está permitido:")
    print()
    print("1. Verificar en authz/views_fotos_reconocimiento.py:")
    print("   @api_view(['POST'])  # ← Debe incluir POST")
    print()
    print("2. Verificar en authz/urls.py:")
    print("   path('usuarios/fotos-reconocimiento/', subir_fotos_reconocimiento, ...)")
    print()
    print("3. Reiniciar servidor Django:")
    print("   python manage.py runserver")
    print()
    print("4. Si sigue fallando, verificar CORS y middleware")

if __name__ == "__main__":
    diagnosticar_endpoint()
    verificar_configuracion_django()
    mostrar_solucion()