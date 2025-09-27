#!/usr/bin/env python
"""
APLICAR CAMBIO PERMANENTE: TRANSFERENCIA DE PROPIEDAD REAL
========================================================
Este script SÍ modifica la base de datos permanentemente
"""

import os
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from authz.models import Persona, Usuario
from authz.utils_roles import sincronizar_roles_con_tipo_persona

def aplicar_transferencia_permanente():
    print('🏠 APLICAR TRANSFERENCIA PERMANENTE EN BASE DE DATOS')
    print('=' * 60)
    print('⚠️  ESTE CAMBIO SÍ SE GUARDARÁ EN LA BASE DE DATOS')
    print()
    
    # Mostrar usuarios actuales
    maria = Usuario.objects.filter(email='maria.gonzalez@facial.com').first()
    carlos = Usuario.objects.filter(email='carlos.rodriguez@facial.com').first()
    
    if not maria or not carlos:
        print('❌ No se encontraron los usuarios específicos')
        return
    
    print('📋 ESTADO ACTUAL:')
    print(f'👤 {maria.email}:')
    print(f'   Tipo: {maria.persona.tipo_persona}')
    print(f'   Roles: {[r.nombre for r in maria.roles.all()]}')
    print()
    
    print(f'👤 {carlos.email}:')
    print(f'   Tipo: {carlos.persona.tipo_persona}')
    print(f'   Roles: {[r.nombre for r in carlos.roles.all()]}')
    print()
    
    # Preguntar confirmación
    respuesta = input('¿Quieres aplicar la transferencia PERMANENTE? (si/no): ').lower().strip()
    
    if respuesta in ['si', 'sí', 's', 'yes', 'y']:
        print()
        print('🔄 APLICANDO TRANSFERENCIA PERMANENTE...')
        
        # Cambiar tipos de persona PERMANENTEMENTE
        maria.persona.tipo_persona = 'inquilino'  # Era propietario
        carlos.persona.tipo_persona = 'propietario'  # Era inquilino
        
        maria.persona.save()
        carlos.persona.save()
        
        print('✅ Tipos de persona actualizados en base de datos')
        
        # Sincronizar roles PERMANENTEMENTE
        resultado_maria = sincronizar_roles_con_tipo_persona(maria.persona, maria)
        resultado_carlos = sincronizar_roles_con_tipo_persona(carlos.persona, carlos)
        
        print(f'📧 {maria.email}: {resultado_maria["message"]}')
        print(f'📧 {carlos.email}: {resultado_carlos["message"]}')
        
        # Recargar usuarios para mostrar cambios
        maria.refresh_from_db()
        carlos.refresh_from_db()
        
        print()
        print('📋 NUEVO ESTADO PERMANENTE:')
        print(f'👤 {maria.email}:')
        print(f'   Tipo: {maria.persona.tipo_persona}')
        print(f'   Roles: {[r.nombre for r in maria.roles.all()]}')
        print(f'   🔐 Login → Panel de {"inquilinos" if "Inquilino" in [r.nombre for r in maria.roles.all()] else "propietarios"}')
        print()
        
        print(f'👤 {carlos.email}:')
        print(f'   Tipo: {carlos.persona.tipo_persona}')
        print(f'   Roles: {[r.nombre for r in carlos.roles.all()]}')
        print(f'   🔐 Login → Panel de {"propietarios" if "Propietario" in [r.nombre for r in carlos.roles.all()] else "inquilinos"}')
        
        print()
        print('✅ TRANSFERENCIA APLICADA PERMANENTEMENTE')
        print('✅ Los cambios están guardados en la base de datos')
        print('✅ Los usuarios verán los nuevos paneles en el próximo login')
        
    else:
        print()
        print('❌ Transferencia cancelada - No se modificó la base de datos')

def mostrar_estado_actual():
    print('📋 ESTADO ACTUAL DE LA BASE DE DATOS:')
    print('=' * 45)
    
    maria = Usuario.objects.filter(email='maria.gonzalez@facial.com').first()
    carlos = Usuario.objects.filter(email='carlos.rodriguez@facial.com').first()
    
    if maria:
        print(f'👤 {maria.email}:')
        print(f'   Tipo: {maria.persona.tipo_persona}')
        print(f'   Roles: {[r.nombre for r in maria.roles.all()]}')
        
        # Simular primary_role
        roles = [r.nombre for r in maria.roles.all()]
        primary = 'Inquilino' if 'Inquilino' in roles else (
            'Propietario' if 'Propietario' in roles else 
            'Administrador' if 'Administrador' in roles else roles[0] if roles else None
        )
        print(f'   🔐 primary_role: {primary}')
        print()
    
    if carlos:
        print(f'👤 {carlos.email}:')
        print(f'   Tipo: {carlos.persona.tipo_persona}')
        print(f'   Roles: {[r.nombre for r in carlos.roles.all()]}')
        
        # Simular primary_role
        roles = [r.nombre for r in carlos.roles.all()]
        primary = 'Inquilino' if 'Inquilino' in roles else (
            'Propietario' if 'Propietario' in roles else 
            'Administrador' if 'Administrador' in roles else roles[0] if roles else None
        )
        print(f'   🔐 primary_role: {primary}')

if __name__ == '__main__':
    print('1️⃣  Ver estado actual')
    print('2️⃣  Aplicar transferencia permanente')
    print()
    
    opcion = input('Elige una opción (1 o 2): ').strip()
    
    if opcion == '1':
        mostrar_estado_actual()
    elif opcion == '2':
        aplicar_transferencia_permanente()
    else:
        print('❌ Opción inválida')