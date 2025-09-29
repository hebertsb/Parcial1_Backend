#!/usr/bin/env python3
"""
Script para investigar el problema del usuario ID 8 no apareciendo en usuarios-reconocimiento
"""

import os
import sys
import django

# Setup Django
sys.path.append('.')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from authz.models import Usuario
from seguridad.models import Copropietarios, ReconocimientoFacial

def investigar_usuario_8():
    print('🔍 INVESTIGACIÓN CRÍTICA - USUARIO ID 8')
    print('=' * 60)
    
    # 1. Verificar usuario
    print('1️⃣ VERIFICANDO USUARIO ID 8:')
    usuario = Usuario.objects.filter(id=8).first()
    if usuario:
        print(f'   ✅ Usuario encontrado: {usuario.email}')
        if usuario.persona:
            print(f'   Nombre: {usuario.persona.nombre} {usuario.persona.apellido}')
        else:
            print('   ⚠️ Sin persona asociada')
    else:
        print('   ❌ Usuario ID 8 NO encontrado')
        return
    
    # 2. Verificar copropietario
    print(f'\n2️⃣ VERIFICANDO COPROPIETARIOS para email: {usuario.email}')
    copropietarios = Copropietarios.objects.filter(email=usuario.email)
    print(f'   Total copropietarios encontrados: {copropietarios.count()}')
    
    for copro in copropietarios:
        print(f'   📋 Copropietario ID: {copro.id}')
        try:
            nombres = getattr(copro, 'nombres', getattr(copro, 'nombre', ''))
            apellidos = getattr(copro, 'apellidos', getattr(copro, 'apellido', ''))
            print(f'      Nombre: {nombres} {apellidos}')
        except:
            print(f'      Nombre: Error obteniendo nombre')
        print(f'      Email: {copro.email}')
        print(f'      Usuario asociado: {copro.usuario_id}')
        print(f'      Activo: {copro.activo}')
    
    # 3. Verificar fotos de reconocimiento
    print(f'\n3️⃣ VERIFICANDO FOTOS DE RECONOCIMIENTO:')
    total_fotos_global = 0
    
    for copro in copropietarios:
        fotos = ReconocimientoFacial.objects.filter(copropietario=copro)
        print(f'   📷 Copropietario ID {copro.id}: {fotos.count()} fotos')
        total_fotos_global += fotos.count()
        
        for foto in fotos[:3]:  # Mostrar solo las primeras 3
            print(f'      - Foto ID: {foto.id}')
            print(f'        Archivo: {foto.imagen_facial}')
            print(f'        Fecha: {foto.fecha_registro}')
    
    print(f'\n   🎯 TOTAL FOTOS PARA USUARIO ID 8: {total_fotos_global}')
    
    # 4. Verificar la consulta del endpoint
    print(f'\n4️⃣ SIMULANDO CONSULTA DEL ENDPOINT:')
    print('   Query: Copropietarios con ReconocimientoFacial...')
    
    # Simular la consulta que hace el endpoint
    copropietarios_con_fotos = Copropietarios.objects.filter(
        reconocimientofacial__isnull=False
    ).distinct()
    
    print(f'   Total copropietarios con fotos: {copropietarios_con_fotos.count()}')
    for copro in copropietarios_con_fotos:
        try:
            nombres = getattr(copro, 'nombres', getattr(copro, 'nombre', ''))
            apellidos = getattr(copro, 'apellidos', getattr(copro, 'apellido', ''))
            print(f'      - ID: {copro.id}, Email: {copro.email}, Nombre: {nombres} {apellidos}')
        except:
            print(f'      - ID: {copro.id}, Email: {copro.email}, Nombre: Error obteniendo nombre')
        if copro.usuario_id:
            print(f'        Usuario ID: {copro.usuario_id}')
        else:
            print(f'        ⚠️ Sin usuario asociado')
    
    # 5. Verificar si usuario ID 8 está en la consulta
    copro_usuario_8 = copropietarios_con_fotos.filter(usuario_id=8).first()
    if copro_usuario_8:
        print(f'\n   ✅ Usuario ID 8 SÍ aparece en la consulta con fotos')
        print(f'      Copropietario ID: {copro_usuario_8.id}')
    else:
        print(f'\n   ❌ Usuario ID 8 NO aparece en la consulta con fotos')
        print(f'   🔍 POSIBLES CAUSAS:')
        print(f'      1. No tiene copropietario asociado')
        print(f'      2. El copropietario no tiene fotos')
        print(f'      3. La relación usuario-copropietario está rota')

if __name__ == "__main__":
    investigar_usuario_8()