#!/usr/bin/env python
"""
Script para probar login de usuarios de seguridad
"""

import os
import sys
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from django.test import Client
import json

def probar_login(email, password):
    """Probar login con credenciales específicas"""
    print(f"🔍 Probando login para: {email}")
    
    client = Client()
    
    response = client.post(
        '/api/authz/auth/login/',
        data=json.dumps({
            'email': email,
            'password': password
        }),
        content_type='application/json'
    )
    
    print(f"📊 Status Code: {response.status_code}")
    
    if response.status_code == 200:
        try:
            data = response.json()
            print(f"✅ LOGIN EXITOSO!")
            print(f"🎟️ Token: {data.get('access', 'No token')[:50]}...")
            print(f"🔄 Refresh: {data.get('refresh', 'No refresh')[:50]}...")
            return True
        except:
            print(f"✅ Login exitoso pero sin JSON response")
            return True
    else:
        try:
            error_data = response.json()
            print(f"❌ ERROR: {error_data}")
        except:
            print(f"❌ ERROR: {response.content.decode()}")
        return False

def main():
    """Probar login con diferentes usuarios"""
    print("🔐 PRUEBAS DE LOGIN - USUARIOS DE SEGURIDAD")
    print("=" * 50)
    
    # Credenciales para probar
    credenciales = [
        ("prueba.seguridad@test.com", "prueba123"),
        ("carlos.test@condominio.com", "segTEST2024"),
        ("seguridad@facial.com", "seguridad2024"),
        ("seguridad1@condominio.com", "seguridad2024"),
    ]
    
    resultados = []
    
    for email, password in credenciales:
        print(f"\n{'='*30}")
        resultado = probar_login(email, password)
        resultados.append((email, resultado))
        print()
    
    # Resumen
    print("="*50)
    print("📊 RESUMEN DE PRUEBAS:")
    exitosos = 0
    for email, exitoso in resultados:
        estado = "✅ ÉXITO" if exitoso else "❌ FALLO"
        print(f"  {estado} - {email}")
        if exitoso:
            exitosos += 1
    
    print(f"\n🎯 Total exitosos: {exitosos}/{len(resultados)}")
    
    if exitosos > 0:
        print("\n💡 CREDENCIALES VÁLIDAS ENCONTRADAS:")
        for email, exitoso in resultados:
            if exitoso:
                # Encontrar password correspondiente
                password = next(p for e, p in credenciales if e == email)
                print(f"📧 Email: {email}")
                print(f"🔑 Password: {password}")
                print()

if __name__ == "__main__":
    main()