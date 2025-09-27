#!/usr/bin/env python3
"""
Test específico para verificar que la transferencia de propiedad
sea específica por vivienda y NO afecte otros usuarios masivamente
"""

import requests
import json
import sys

# Configuración
BASE_URL = "http://127.0.0.1:8000"
LOGIN_URL = f"{BASE_URL}/api/authz/login/"
PERSONAS_URL = f"{BASE_URL}/api/viviendas/personas/"

def login_admin():
    """Login como administrador"""
    login_data = {
        "email": "admin@test.com",
        "password": "admin123"
    }
    
    print("🔐 Haciendo login como administrador...")
    response = requests.post(LOGIN_URL, json=login_data)
    
    if response.status_code == 200:
        token = response.json().get('access')
        print(f"✅ Login exitoso.")
        return token
    else:
        print(f"❌ Error en login: {response.status_code}")
        print(f"Response: {response.text}")
        return None

def obtener_personas_antes(token):
    """Obtener estado de todas las personas ANTES de la transferencia"""
    headers = {"Authorization": f"Bearer {token}"}
    
    print("\n📊 Obteniendo estado de todas las personas ANTES...")
    response = requests.get(PERSONAS_URL, headers=headers)
    
    if response.status_code == 200:
        personas = response.json().get('results', [])
        print(f"📋 Total de personas encontradas: {len(personas)}")
        
        # Contar por tipo
        tipos = {}
        activas = 0
        for persona in personas:
            tipo = persona.get('tipo_persona', 'undefined')
            tipos[tipo] = tipos.get(tipo, 0) + 1
            if persona.get('activo', True):
                activas += 1
        
        print(f"📊 Personas activas: {activas}/{len(personas)}")
        print(f"📊 Por tipo: {tipos}")
        
        return personas
    else:
        print(f"❌ Error obteniendo personas: {response.status_code}")
        return []

def encontrar_inquilino_con_propiedades(personas):
    """Encontrar un inquilino que tenga propiedades activas"""
    inquilinos = [p for p in personas if p.get('tipo_persona') == 'inquilino' and p.get('activo', True)]
    
    print(f"\n🔍 Inquilinos activos encontrados: {len(inquilinos)}")
    
    if inquilinos:
        inquilino = inquilinos[0]  # Tomar el primero
        print(f"🎯 Seleccionado inquilino: {inquilino.get('nombre_completo')} (ID: {inquilino.get('id')})")
        return inquilino
    
    return None

def realizar_transferencia(token, inquilino_id):
    """Realizar la transferencia de propiedad específica"""
    headers = {"Authorization": f"Bearer {token}"}
    
    transfer_url = f"{PERSONAS_URL}{inquilino_id}/transferir_propiedad/"
    transfer_data = {
        "accion_propietario_anterior": "desactivar"
    }
    
    print(f"\n🔄 Iniciando transferencia para inquilino ID: {inquilino_id}")
    print(f"🌐 URL: {transfer_url}")
    
    response = requests.post(transfer_url, json=transfer_data, headers=headers)
    
    print(f"📊 Status Code: {response.status_code}")
    
    if response.status_code == 200:
        data = response.json()
        print("✅ ¡Transferencia exitosa!")
        print(f"📄 Respuesta: {json.dumps(data, indent=2, ensure_ascii=False)}")
        return True
    else:
        print("❌ Error en transferencia:")
        try:
            error_data = response.json()
            print(f"📄 Error JSON: {json.dumps(error_data, indent=2, ensure_ascii=False)}")
        except:
            print(f"📄 Error texto: {response.text}")
        return False

def obtener_personas_despues(token):
    """Obtener estado de todas las personas DESPUÉS de la transferencia"""
    headers = {"Authorization": f"Bearer {token}"}
    
    print("\n📊 Obteniendo estado de todas las personas DESPUÉS...")
    response = requests.get(PERSONAS_URL, headers=headers)
    
    if response.status_code == 200:
        personas = response.json().get('results', [])
        print(f"📋 Total de personas encontradas: {len(personas)}")
        
        # Contar por tipo
        tipos = {}
        activas = 0
        for persona in personas:
            tipo = persona.get('tipo_persona', 'undefined')
            tipos[tipo] = tipos.get(tipo, 0) + 1
            if persona.get('activo', True):
                activas += 1
        
        print(f"📊 Personas activas: {activas}/{len(personas)}")
        print(f"📊 Por tipo: {tipos}")
        
        return personas
    else:
        print(f"❌ Error obteniendo personas: {response.status_code}")
        return []

def comparar_cambios(personas_antes, personas_despues):
    """Comparar los cambios para verificar que sean específicos"""
    print("\n🔍 ANÁLISIS DE CAMBIOS:")
    print("=" * 50)
    
    # Crear diccionarios por ID para comparación
    antes_dict = {p['id']: p for p in personas_antes}
    despues_dict = {p['id']: p for p in personas_despues}
    
    cambios_detectados = []
    
    for persona_id, persona_despues in despues_dict.items():
        persona_antes = antes_dict.get(persona_id)
        
        if not persona_antes:
            continue
        
        # Verificar cambios
        cambios_persona = []
        
        # Cambio de tipo
        if persona_antes.get('tipo_persona') != persona_despues.get('tipo_persona'):
            cambios_persona.append(f"tipo_persona: {persona_antes.get('tipo_persona')} → {persona_despues.get('tipo_persona')}")
        
        # Cambio de estado activo
        if persona_antes.get('activo') != persona_despues.get('activo'):
            cambios_persona.append(f"activo: {persona_antes.get('activo')} → {persona_despues.get('activo')}")
        
        if cambios_persona:
            cambios_detectados.append({
                'id': persona_id,
                'nombre': persona_despues.get('nombre_completo'),
                'cambios': cambios_persona
            })
    
    # Mostrar resultados
    if cambios_detectados:
        print(f"📋 Total de personas que cambiaron: {len(cambios_detectados)}")
        for cambio in cambios_detectados:
            print(f"👤 {cambio['nombre']} (ID: {cambio['id']}):")
            for detalle in cambio['cambios']:
                print(f"   • {detalle}")
            print()
        
        # Verificar si los cambios son específicos o masivos
        if len(cambios_detectados) > 5:  # Threshold arbitrario
            print("⚠️ ¡ALERTA! Muchas personas cambiaron - posible error masivo")
            return False
        else:
            print("✅ Cambios parecen específicos - cantidad normal")
            return True
    else:
        print("ℹ️ No se detectaron cambios en personas")
        return True

def main():
    print("🚀 INICIANDO TEST DE TRANSFERENCIA ESPECÍFICA")
    print("=" * 60)
    
    # 1. Login
    token = login_admin()
    if not token:
        print("❌ No se pudo obtener token. Abortando test.")
        return
    
    # 2. Obtener estado inicial
    personas_antes = obtener_personas_antes(token)
    if not personas_antes:
        print("❌ No se pudieron obtener personas. Abortando test.")
        return
    
    # 3. Encontrar inquilino para transferir
    inquilino = encontrar_inquilino_con_propiedades(personas_antes)
    if not inquilino:
        print("❌ No se encontró inquilino válido. Abortando test.")
        return
    
    # 4. Realizar transferencia
    transferencia_exitosa = realizar_transferencia(token, inquilino['id'])
    if not transferencia_exitosa:
        print("❌ Transferencia falló. Abortando test.")
        return
    
    # 5. Obtener estado final
    personas_despues = obtener_personas_despues(token)
    if not personas_despues:
        print("❌ No se pudieron obtener personas después. Test incompleto.")
        return
    
    # 6. Comparar cambios
    cambios_especificos = comparar_cambios(personas_antes, personas_despues)
    
    # 7. Resultado final
    print("\n" + "=" * 60)
    print("🎯 RESULTADO FINAL DEL TEST")
    print("=" * 60)
    
    if cambios_especificos:
        print("✅ ¡TEST EXITOSO! Los cambios son específicos por vivienda")
        print("✅ No se detectaron cambios masivos erróneos")
    else:
        print("❌ ¡TEST FALLIDO! Se detectaron cambios masivos")
        print("❌ El bug de transferencia masiva aún existe")
    
    return cambios_especificos

if __name__ == "__main__":
    exito = main()
    sys.exit(0 if exito else 1)