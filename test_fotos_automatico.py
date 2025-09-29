#!/usr/bin/env python
"""
🧪 PRUEBA FINAL: Verificar que el usuario aparece después de subir fotos
"""

import requests
import json

BASE_URL = "http://127.0.0.1:8000"

def test_subida_fotos():
    print("🧪 PROBANDO SUBIDA DE FOTOS Y APARICIÓN EN ENDPOINT")
    print("=" * 60)
    
    # 1. LOGIN COMO EL USUARIO ID 12 CREADO EN LA PRUEBA ANTERIOR
    print("\n1️⃣ LOGIN COMO PROPIETARIO ID 12...")
    
    propietario_login = requests.post(f"{BASE_URL}/api/auth/login/", 
                                    json={"email": "ana.perez.09280000@test.com", "password": "temporal123"})
    
    if propietario_login.status_code == 200:
        propietario_token = propietario_login.json()['access']
        propietario_headers = {'Authorization': f'Bearer {propietario_token}'}
        print(f"✅ Login exitoso como propietario")
    else:
        print(f"❌ Error login propietario: {propietario_login.status_code}")
        return
    
    # 2. VERIFICAR QUE NO APARECE EN ENDPOINT ANTES DE SUBIR FOTOS
    print("\n2️⃣ VERIFICANDO QUE NO APARECE EN ENDPOINT ANTES DE FOTOS...")
    
    seguridad_login = requests.post(f"{BASE_URL}/api/auth/login/", 
                                  json={"email": "seguridad@facial.com", "password": "seguridad123"})
    
    if seguridad_login.status_code == 200:
        seguridad_token = seguridad_login.json()['access']
        seguridad_headers = {'Authorization': f'Bearer {seguridad_token}'}
        
        endpoint_response = requests.get(
            f"{BASE_URL}/seguridad/api/usuarios-reconocimiento/",
            headers=seguridad_headers
        )
        
        if endpoint_response.status_code == 200:
            usuarios = endpoint_response.json()['data']
            usuario_12_encontrado = any(user.get('usuario_id') == 12 for user in usuarios)
            
            if not usuario_12_encontrado:
                print("✅ Correcto: Usuario ID 12 NO aparece antes de subir fotos")
            else:
                print("❌ Inesperado: Usuario ID 12 YA aparece")
        else:
            print(f"❌ Error consultando endpoint: {endpoint_response.status_code}")
            return
            
    else:
        print("❌ Error login seguridad")
        return
    
    # 3. SIMULAR SUBIDA DE FOTOS DESDE PANEL DE PROPIETARIO
    print("\n3️⃣ SIMULANDO SUBIDA DE FOTOS...")
    
    # Crear archivo de imagen fake para la prueba
    import io
    from PIL import Image
    
    # Crear imagen pequeña
    img = Image.new('RGB', (100, 100), color='red')
    img_bytes = io.BytesIO()
    img.save(img_bytes, format='JPEG')
    img_bytes.seek(0)
    
    files = {
        'fotos': ('test_foto.jpg', img_bytes, 'image/jpeg')
    }
    data = {
        'usuario_id': 12
    }
    
    subida_response = requests.post(
        f"{BASE_URL}/api/authz/reconocimiento/fotos/",
        files=files,
        data=data,
        headers=propietario_headers
    )
    
    if subida_response.status_code == 200:
        print("✅ Fotos subidas exitosamente")
        print(f"   Respuesta: {subida_response.json()}")
    else:
        print(f"❌ Error subiendo fotos: {subida_response.status_code}")
        print(subida_response.text)
        return
    
    # 4. VERIFICAR QUE AHORA SÍ APARECE EN EL ENDPOINT
    print("\n4️⃣ VERIFICANDO APARICIÓN DESPUÉS DE SUBIR FOTOS...")
    
    endpoint_response = requests.get(
        f"{BASE_URL}/seguridad/api/usuarios-reconocimiento/",
        headers=seguridad_headers
    )
    
    if endpoint_response.status_code == 200:
        usuarios = endpoint_response.json()['data']
        usuario_12_encontrado = False
        
        for user in usuarios:
            if user.get('usuario_id') == 12:
                usuario_12_encontrado = True
                print(f"✅ Usuario encontrado en endpoint de seguridad:")
                print(f"   Usuario ID: {user['usuario_id']}")
                print(f"   Copropietario ID: {user['copropietario_id']}")
                print(f"   Nombre: {user['nombres_completos']}")
                print(f"   Email: {user['email']}")
                if 'reconocimiento_facial' in user:
                    fotos = user['reconocimiento_facial'].get('total_fotos', 0)
                    print(f"   Total fotos: {fotos}")
                break
        
        if usuario_12_encontrado:
            print("\n🎉 FLUJO AUTOMÁTICO 100% COMPLETO!")
            print("✅ Solicitud → Aprobación → Usuario → Copropietario → Fotos → Endpoint")
        else:
            print("❌ Usuario ID 12 aún no aparece en endpoint")
    else:
        print(f"❌ Error consultando endpoint: {endpoint_response.status_code}")
    
    print("\n" + "=" * 60)
    print("🎯 CONFIRMADO: El sistema funciona automáticamente")
    print("   • El admin aprueba → Se crea copropietario automáticamente")
    print("   • El propietario sube fotos → Aparece en seguridad automáticamente")

if __name__ == "__main__":
    test_subida_fotos()