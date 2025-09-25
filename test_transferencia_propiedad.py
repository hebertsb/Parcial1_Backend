#!/usr/bin/env python
"""
Script de prueba para transferencia de propiedad
Simula el caso donde un inquilino compra la casa y se convierte en propietario
"""
import os
import sys
import django
import requests
import json
from datetime import datetime, date

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from authz.models import Persona, RelacionesPropietarioInquilino
from core.models.propiedades_residentes import Vivienda, Propiedad

BASE_URL = "http://localhost:8000"
API_URL = f"{BASE_URL}/api/personas"

def obtener_token_admin():
    """Obtener token JWT para pruebas"""
    try:
        login_url = f"{BASE_URL}/api/auth/login/"
        admin_creds = {
            "email": "admin@residencial.com",
            "password": "admin123"
        }
        
        response = requests.post(login_url, json=admin_creds)
        if response.status_code == 200:
            data = response.json()
            return data.get('access', '')
        else:
            print(f"❌ Error obteniendo token: {response.status_code}")
            return None
    except Exception as e:
        print(f"❌ Error conectando: {e}")
        return None

def crear_escenario_prueba():
    """
    Crear un escenario de prueba con:
    - Una vivienda
    - Un propietario original
    - Un inquilino que va a comprar
    """
    print("\n🏗️ Creando escenario de prueba...")
    
    # Crear vivienda si no existe
    vivienda, created = Vivienda.objects.get_or_create(
        numero_casa="CASA-TEST-001",
        defaults={
            'bloque': 'A',
            'tipo_vivienda': 'casa',
            'metros_cuadrados': 120.00,
            'tarifa_base_expensas': 150.00,
            'tipo_cobranza': 'por_casa',
            'estado': 'activa'
        }
    )
    
    if created:
        print(f"✅ Vivienda creada: {vivienda.numero_casa}")
    else:
        print(f"ℹ️ Vivienda existente: {vivienda.numero_casa}")
    
    # Crear propietario original si no existe
    propietario_original, created = Persona.objects.get_or_create(
        documento_identidad="12345678-PROP",
        defaults={
            'nombre': 'Carlos',
            'apellido': 'Propietario',
            'email': 'carlos.propietario@test.com',
            'telefono': '70111111',
            'tipo_persona': 'propietario',
            'activo': True
        }
    )
    
    if created:
        print(f"✅ Propietario original creado: {propietario_original.nombre_completo}")
    else:
        print(f"ℹ️ Propietario original existente: {propietario_original.nombre_completo}")
    
    # Crear inquilino comprador si no existe
    inquilino_comprador, created = Persona.objects.get_or_create(
        documento_identidad="87654321-INQ",
        defaults={
            'nombre': 'Ana',
            'apellido': 'Inquilina',
            'email': 'ana.inquilina@test.com',
            'telefono': '70222222',
            'tipo_persona': 'inquilino',
            'activo': True
        }
    )
    
    if created:
        print(f"✅ Inquilino comprador creado: {inquilino_comprador.nombre_completo}")
    else:
        print(f"ℹ️ Inquilino comprador existente: {inquilino_comprador.nombre_completo}")
    
    # Crear propiedad del propietario original si no existe
    propiedad_propietario, created = Propiedad.objects.get_or_create(
        vivienda=vivienda,
        persona=propietario_original,
        tipo_tenencia='propietario',
        defaults={
            'porcentaje_propiedad': 100.00,
            'fecha_inicio_tenencia': date(2023, 1, 1),
            'activo': True
        }
    )
    
    if created:
        print(f"✅ Propiedad del propietario creada")
    else:
        print(f"ℹ️ Propiedad del propietario existente")
    
    # Crear propiedad del inquilino si no existe
    propiedad_inquilino, created = Propiedad.objects.get_or_create(
        vivienda=vivienda,
        persona=inquilino_comprador,
        tipo_tenencia='inquilino',
        defaults={
            'porcentaje_propiedad': 100.00,
            'fecha_inicio_tenencia': date(2024, 1, 1),
            'activo': True
        }
    )
    
    if created:
        print(f"✅ Propiedad del inquilino creada")
    else:
        print(f"ℹ️ Propiedad del inquilino existente")
    
    return vivienda, propietario_original, inquilino_comprador

def mostrar_estado_antes(vivienda, propietario_original, inquilino_comprador):
    """Mostrar el estado antes de la transferencia"""
    print("\n📊 ESTADO ANTES DE LA TRANSFERENCIA:")
    print("=" * 50)
    
    # Mostrar datos del propietario original
    propiedades_prop = Propiedad.objects.filter(
        persona=propietario_original,
        vivienda=vivienda,
        activo=True
    )
    
    print(f"👤 Propietario Original: {propietario_original.nombre_completo}")
    print(f"   - Tipo: {propietario_original.tipo_persona}")
    print(f"   - Activo: {propietario_original.activo}")
    print(f"   - Propiedades activas: {propiedades_prop.count()}")
    
    for prop in propiedades_prop:
        print(f"     • {prop.vivienda.numero_casa} ({prop.tipo_tenencia}) - {prop.porcentaje_propiedad}%")
    
    # Mostrar datos del inquilino
    propiedades_inq = Propiedad.objects.filter(
        persona=inquilino_comprador,
        vivienda=vivienda,
        activo=True
    )
    
    print(f"\n🏠 Inquilino Comprador: {inquilino_comprador.nombre_completo}")
    print(f"   - Tipo: {inquilino_comprador.tipo_persona}")
    print(f"   - Activo: {inquilino_comprador.activo}")
    print(f"   - Propiedades activas: {propiedades_inq.count()}")
    
    for prop in propiedades_inq:
        print(f"     • {prop.vivienda.numero_casa} ({prop.tipo_tenencia}) - {prop.porcentaje_propiedad}%")

def test_transferencia_propiedad(token, inquilino_id, accion_propietario='desactivar'):
    """Probar la transferencia de propiedad"""
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    print(f"\n🔄 EJECUTANDO TRANSFERENCIA DE PROPIEDAD")
    print(f"   Inquilino ID: {inquilino_id}")
    print(f"   Acción propietario anterior: {accion_propietario}")
    
    payload = {
        "accion_propietario_anterior": accion_propietario
    }
    
    response = requests.post(
        f"{API_URL}/{inquilino_id}/transferir_propiedad/",
        headers=headers,
        json=payload
    )
    
    if response.status_code == 200:
        data = response.json()
        print(f"✅ TRANSFERENCIA EXITOSA!")
        print(f"   Mensaje: {data.get('message')}")
        print(f"   Propiedades transferidas: {data.get('total_propiedades_transferidas')}")
        print(f"   Nuevo propietario: {data.get('nuevo_propietario', {}).get('nombre_completo')}")
        
        # Mostrar detalles de transferencias
        for transferencia in data.get('transferencias_realizadas', []):
            print(f"\n   📋 Transferencia:")
            print(f"      • Vivienda: {transferencia.get('vivienda')}")
            print(f"      • De: {transferencia.get('propietario_anterior')}")
            print(f"      • A: {transferencia.get('nuevo_propietario')}")
            print(f"      • Porcentaje: {transferencia.get('porcentaje_transferido')}%")
            print(f"      • Estado anterior: {transferencia.get('estado_propietario_anterior')}")
        
        return data
    else:
        print(f"❌ Error en transferencia: {response.status_code}")
        print(f"   Respuesta: {response.text}")
        return None

def mostrar_estado_despues(vivienda, propietario_original, inquilino_comprador):
    """Mostrar el estado después de la transferencia"""
    print("\n📊 ESTADO DESPUÉS DE LA TRANSFERENCIA:")
    print("=" * 50)
    
    # Refrescar objetos desde la DB
    propietario_original.refresh_from_db()
    inquilino_comprador.refresh_from_db()
    
    # Mostrar datos del ex-propietario
    propiedades_prop = Propiedad.objects.filter(
        persona=propietario_original,
        vivienda=vivienda,
        activo=True
    )
    
    print(f"👤 Ex-Propietario: {propietario_original.nombre_completo}")
    print(f"   - Tipo: {propietario_original.tipo_persona}")
    print(f"   - Activo: {propietario_original.activo}")
    print(f"   - Propiedades activas: {propiedades_prop.count()}")
    
    for prop in propiedades_prop:
        print(f"     • {prop.vivienda.numero_casa} ({prop.tipo_tenencia}) - {prop.porcentaje_propiedad}%")
    
    # Mostrar datos del nuevo propietario
    propiedades_nuevo = Propiedad.objects.filter(
        persona=inquilino_comprador,
        vivienda=vivienda,
        activo=True
    )
    
    print(f"\n🏠 Nuevo Propietario: {inquilino_comprador.nombre_completo}")
    print(f"   - Tipo: {inquilino_comprador.tipo_persona}")
    print(f"   - Activo: {inquilino_comprador.activo}")
    print(f"   - Propiedades activas: {propiedades_nuevo.count()}")
    
    for prop in propiedades_nuevo:
        print(f"     • {prop.vivienda.numero_casa} ({prop.tipo_tenencia}) - {prop.porcentaje_propiedad}%")

def main():
    print("=" * 70)
    print("🏡 PRUEBA DE TRANSFERENCIA DE PROPIEDAD")
    print("   Inquilino compra casa → Se convierte en propietario")
    print("=" * 70)
    
    # Obtener token
    token = obtener_token_admin()
    if not token:
        print("❌ No se pudo obtener token")
        return
    
    # Crear escenario de prueba
    vivienda, propietario_original, inquilino_comprador = crear_escenario_prueba()
    
    # Mostrar estado inicial
    mostrar_estado_antes(vivienda, propietario_original, inquilino_comprador)
    
    # Ejecutar transferencia
    input("\n⏸️ Presiona Enter para ejecutar la transferencia...")
    
    # Opción 1: Desactivar propietario anterior
    print("\n🔄 OPCIÓN 1: Desactivar propietario anterior")
    resultado = test_transferencia_propiedad(token, inquilino_comprador.id, 'desactivar')
    
    if resultado:
        # Mostrar estado final
        mostrar_estado_despues(vivienda, propietario_original, inquilino_comprador)
        
        print("\n" + "=" * 70)
        print("✅ PRUEBA COMPLETADA EXITOSAMENTE")
        print("   El inquilino ahora es propietario de la vivienda")
        print("   El propietario anterior fue desactivado")
        print("=" * 70)
    else:
        print("\n❌ La prueba falló")

if __name__ == "__main__":
    main()