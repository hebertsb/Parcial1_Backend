#!/usr/bin/env python3
"""
VERI            print(f"   📄 Solicitud ID: {solicitud.id}")
            print(f"      Email: {solicitud.email}")
            print(f"      Estado: {solicitud.estado}")
            print(f"      Fecha: {solicitud.created_at}")CIÓN SISTEMA COMPLETO - FLUJO AUTOMÁTICO
================================================
Verifica que el sistema automático funciona correctamente:
1. Crear solicitud → 2. Aprobar → 3. Sistema automático crea todo
"""

import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

import requests
import json
from authz.models import Usuario, SolicitudRegistroPropietario
from seguridad.models import Copropietarios, ReconocimientoFacial

def main():
    print("🔍 VERIFICACIÓN DEL SISTEMA COMPLETO")
    print("=" * 50)
    
    # 1. Verificar flujo automático reciente
    print("\n1. 📋 VERIFICANDO ÚLTIMAS SOLICITUDES APROBADAS")
    
    solicitudes_aprobadas = SolicitudRegistroPropietario.objects.filter(
        estado='APROBADA'
    ).order_by('-created_at')[:3]
    
    if solicitudes_aprobadas.exists():
        print(f"   ✅ {solicitudes_aprobadas.count()} solicitudes aprobadas encontradas")
        
        for solicitud in solicitudes_aprobadas:
            print(f"\n   📄 Solicitud ID: {solicitud.id}")
            print(f"      Email: {solicitud.email}")
            print(f"      Estado: {solicitud.estado}")
            print(f"      Fecha: {solicitud.created_at}")
            
            # Verificar usuario creado
            try:
                usuario = Usuario.objects.get(email=solicitud.email)
                print(f"      ✅ Usuario creado: ID {usuario.id}")
                
                # Verificar copropietario
                try:
                    copropietario = Copropietarios.objects.get(usuario_sistema=usuario)
                    print(f"      ✅ Copropietario creado: ID {copropietario.id}")
                    
                    # Verificar reconocimiento facial
                    try:
                        reconocimiento = ReconocimientoFacial.objects.get(copropietario=copropietario)
                        print(f"      ✅ ReconocimientoFacial creado: ID {reconocimiento.id}")
                        
                        if reconocimiento.vector_facial:
                            fotos_count = len(reconocimiento.vector_facial.split(',')) if reconocimiento.vector_facial else 0
                            print(f"      📸 Fotos subidas: {fotos_count}")
                        else:
                            print(f"      📸 Sin fotos aún (normal para usuarios nuevos)")
                            
                    except ReconocimientoFacial.DoesNotExist:
                        print(f"      ❌ ReconocimientoFacial NO encontrado")
                        
                except Copropietarios.DoesNotExist:
                    print(f"      ❌ Copropietario NO encontrado")
                    
            except Usuario.DoesNotExist:
                print(f"      ❌ Usuario NO encontrado")
    else:
        print("   ⚠️  No hay solicitudes aprobadas en el sistema")
    
    # 2. Verificar endpoints funcionando
    print("\n\n2. 🔌 VERIFICANDO ENDPOINTS DE RECONOCIMIENTO")
    
    try:
        # Login como seguridad
        print("   🔐 Realizando login de seguridad...")
        login_response = requests.post('http://localhost:8000/api/authz/login/', {
            'email': 'seguridad@facial.com',
            'password': 'seguridad123'
        })
        
        if login_response.status_code == 200:
            token = login_response.json()['access']
            print("   ✅ Login exitoso")
            
            # Verificar endpoint de lista de reconocimientos
            headers = {'Authorization': f'Bearer {token}'}
            response = requests.get(
                'http://localhost:8000/api/authz/reconocimiento/',
                headers=headers
            )
            
            if response.status_code == 200:
                data = response.json()
                reconocimientos = data.get('data', [])
                print(f"   ✅ Endpoint lista reconocimientos: {len(reconocimientos)} registros")
                
                # Probar endpoint de fotos si hay reconocimientos
                if reconocimientos:
                    primer_reconocimiento = reconocimientos[0]
                    reconocimiento_id = primer_reconocimiento.get('id')
                    
                    foto_response = requests.get(
                        f'http://localhost:8000/api/authz/reconocimiento/fotos/{reconocimiento_id}/',
                        headers=headers
                    )
                    
                    if foto_response.status_code == 200:
                        foto_data = foto_response.json()
                        success = foto_data.get('success', False)
                        print(f"   ✅ Endpoint GET fotos funcional: Success={success}")
                    else:
                        print(f"   ⚠️  Endpoint GET fotos: Status {foto_response.status_code}")
                
            else:
                print(f"   ❌ Error en endpoint lista: Status {response.status_code}")
                
        else:
            print(f"   ❌ Error en login: Status {login_response.status_code}")
            
    except Exception as e:
        print(f"   ❌ Error en verificación de endpoints: {e}")
    
    # 3. Resumen del sistema
    print("\n\n3. 📊 RESUMEN DEL SISTEMA")
    print("   " + "="*40)
    
    total_solicitudes = SolicitudRegistroPropietario.objects.count()
    solicitudes_aprobadas_count = SolicitudRegistroPropietario.objects.filter(estado='APROBADA').count()
    total_usuarios = Usuario.objects.count()
    total_copropietarios = Copropietarios.objects.count()
    total_reconocimientos = ReconocimientoFacial.objects.count()
    
    print(f"   📋 Total solicitudes: {total_solicitudes}")
    print(f"   ✅ Solicitudes aprobadas: {solicitudes_aprobadas_count}")
    print(f"   👤 Total usuarios: {total_usuarios}")
    print(f"   🏠 Total copropietarios: {total_copropietarios}")
    print(f"   📸 Total reconocimientos: {total_reconocimientos}")
    
    # Verificar consistencia
    if solicitudes_aprobadas_count == total_copropietarios == total_reconocimientos:
        print("\n   🎉 SISTEMA COMPLETAMENTE FUNCIONAL")
        print("   ✅ Flujo automático trabajando correctamente")
        print("   ✅ Cada solicitud aprobada crea: Usuario + Copropietario + ReconocimientoFacial")
    else:
        print("\n   ⚠️  Posible inconsistencia detectada")
        print("   💡 Verificar flujo automático en aprobar_solicitud()")

if __name__ == "__main__":
    main()