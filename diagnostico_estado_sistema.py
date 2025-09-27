#!/usr/bin/env python3
"""
Script para verificar el estado actual de todas las personas
y identificar si hay problemas masivos ya existentes
"""

import requests
import json
from collections import Counter

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

def analizar_estado_personas(token):
    """Análisis completo del estado de las personas"""
    headers = {"Authorization": f"Bearer {token}"}
    
    print("\n📊 ANALIZANDO ESTADO ACTUAL DE PERSONAS...")
    print("=" * 50)
    
    response = requests.get(PERSONAS_URL, headers=headers)
    
    if response.status_code != 200:
        print(f"❌ Error obteniendo personas: {response.status_code}")
        return
    
    personas = response.json().get('results', [])
    total_personas = len(personas)
    
    print(f"📋 Total de personas en sistema: {total_personas}")
    
    # Análisis por estado activo
    activas = [p for p in personas if p.get('activo', True)]
    inactivas = [p for p in personas if not p.get('activo', True)]
    
    print(f"✅ Personas activas: {len(activas)}")
    print(f"❌ Personas inactivas: {len(inactivas)}")
    
    # Análisis por tipo de persona
    tipos = Counter(p.get('tipo_persona', 'undefined') for p in personas)
    
    print(f"\n📊 DISTRIBUCIÓN POR TIPO:")
    for tipo, cantidad in tipos.items():
        print(f"   {tipo}: {cantidad}")
    
    # Personas inactivas detalladas
    if inactivas:
        print(f"\n⚠️ PERSONAS INACTIVAS DETECTADAS:")
        for persona in inactivas:
            print(f"   • {persona.get('nombre_completo', 'Sin nombre')} (ID: {persona.get('id')}) - Tipo: {persona.get('tipo_persona', 'undefined')}")
        
        # Verificar si hay muchas inactivas (posible problema masivo)
        porcentaje_inactivas = (len(inactivas) / total_personas) * 100
        print(f"\n📈 Porcentaje de personas inactivas: {porcentaje_inactivas:.1f}%")
        
        if porcentaje_inactivas > 30:  # Threshold del 30%
            print("🚨 ¡ALERTA! Alto porcentaje de personas inactivas")
            print("🚨 Posible problema masivo detectado")
        elif porcentaje_inactivas > 10:
            print("⚠️ Porcentaje moderado de personas inactivas")
        else:
            print("✅ Porcentaje normal de personas inactivas")
    
    # Análisis de distribución esperada vs actual
    print(f"\n🔍 ANÁLISIS DE COHERENCIA:")
    
    propietarios = tipos.get('propietario', 0)
    inquilinos = tipos.get('inquilino', 0) 
    residentes = tipos.get('residente', 0)
    familiares = tipos.get('familiar', 0)
    
    print(f"   Propietarios: {propietarios}")
    print(f"   Inquilinos: {inquilinos}")
    print(f"   Residentes: {residentes}")
    print(f"   Familiares: {familiares}")
    
    # Verificar patrones anómalos
    anomalias = []
    
    if propietarios == 0:
        anomalias.append("No hay propietarios registrados")
    
    if inquilinos == 0:
        anomalias.append("No hay inquilinos registrados")
    
    if propietarios > inquilinos * 3:  # Ratio anómalo
        anomalias.append("Ratio propietarios/inquilinos anómalo")
    
    if anomalias:
        print(f"\n⚠️ ANOMALÍAS DETECTADAS:")
        for anomalia in anomalias:
            print(f"   • {anomalia}")
    else:
        print(f"\n✅ Distribución parece normal")
    
    return {
        'total': total_personas,
        'activas': len(activas),
        'inactivas': len(inactivas),
        'tipos': dict(tipos),
        'anomalias': anomalias
    }

def obtener_propiedades_activas(token):
    """Verificar propiedades activas en el sistema"""
    # Este endpoint podría no existir, intentar con diferentes URLs
    posibles_urls = [
        f"{BASE_URL}/api/viviendas/propiedades/",
        f"{BASE_URL}/api/core/propiedades/",
    ]
    
    headers = {"Authorization": f"Bearer {token}"}
    
    print(f"\n🏠 VERIFICANDO PROPIEDADES ACTIVAS...")
    
    for url in posibles_urls:
        try:
            response = requests.get(url, headers=headers)
            if response.status_code == 200:
                propiedades = response.json().get('results', [])
                print(f"📋 Propiedades encontradas: {len(propiedades)}")
                
                activas = [p for p in propiedades if p.get('activo', True)]
                print(f"✅ Propiedades activas: {len(activas)}")
                
                # Análisis por tipo de tenencia
                tipos_tenencia = Counter(p.get('tipo_tenencia', 'undefined') for p in propiedades)
                print(f"📊 Por tipo de tenencia: {dict(tipos_tenencia)}")
                
                return propiedades
        except:
            continue
    
    print("⚠️ No se pudieron obtener datos de propiedades")
    return []

def main():
    print("🚀 DIAGNÓSTICO DEL ESTADO ACTUAL DEL SISTEMA")
    print("=" * 60)
    
    # Login
    token = login_admin()
    if not token:
        print("❌ No se pudo obtener token. Abortando diagnóstico.")
        return
    
    # Análisis de personas
    resultado_personas = analizar_estado_personas(token)
    
    # Análisis de propiedades (opcional)
    obtener_propiedades_activas(token)
    
    # Resumen final
    print("\n" + "=" * 60)
    print("📋 RESUMEN DEL DIAGNÓSTICO")
    print("=" * 60)
    
    if resultado_personas:
        print(f"👥 Total personas: {resultado_personas['total']}")
        print(f"✅ Activas: {resultado_personas['activas']}")
        print(f"❌ Inactivas: {resultado_personas['inactivas']}")
        
        if resultado_personas['anomalias']:
            print(f"⚠️ Anomalías detectadas: {len(resultado_personas['anomalias'])}")
            print("🔧 RECOMENDACIÓN: Revisar y corregir antes de hacer transferencias")
        else:
            print("✅ Sistema parece estable para hacer transferencias")
    
    print("\n💡 Próximos pasos recomendados:")
    print("   1. Si hay muchas personas inactivas, considerar reactivar")
    print("   2. Verificar que la lógica de transferencia esté corregida")
    print("   3. Hacer backup antes de cualquier transferencia")
    print("   4. Ejecutar transferencias de prueba con datos específicos")

if __name__ == "__main__":
    main()