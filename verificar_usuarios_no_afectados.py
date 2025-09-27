#!/usr/bin/env python
"""
VERIFICACIÓN: SOLO SE AFECTAN LOS USUARIOS INVOLUCRADOS EN LA TRANSFERENCIA
=========================================================================
Confirmar que otros usuarios mantienen sus roles normales
"""

import os
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from authz.models import Persona, Usuario
from authz.utils_roles import sincronizar_roles_con_tipo_persona
from django.db import transaction

def verificar_usuarios_no_afectados():
    print('🔍 VERIFICACIÓN: USUARIOS NO INVOLUCRADOS MANTIENEN SUS ROLES')
    print('=' * 70)
    print()
    
    # Obtener TODOS los usuarios antes de cualquier cambio
    todos_usuarios_antes = []
    for usuario in Usuario.objects.all():
        if usuario.persona:
            todos_usuarios_antes.append({
                'email': usuario.email,
                'tipo_persona': usuario.persona.tipo_persona,
                'roles': [r.nombre for r in usuario.roles.all()]
            })
    
    print(f'👥 ESTADO INICIAL - {len(todos_usuarios_antes)} usuarios en el sistema:')
    for i, user in enumerate(todos_usuarios_antes, 1):
        print(f'   {i}. {user["email"]}')
        print(f'      Tipo: {user["tipo_persona"]} | Roles: {user["roles"]}')
    print()
    
    # Encontrar dos usuarios específicos para el intercambio
    usuario_prop = Usuario.objects.filter(persona__tipo_persona='propietario').first()
    usuario_inq = Usuario.objects.filter(persona__tipo_persona='inquilino').first()
    
    if not usuario_prop or not usuario_inq:
        print('❌ No se encontraron usuarios para el intercambio')
        return
    
    print(f'🔄 INTERCAMBIO ESPECÍFICO ENTRE 2 USUARIOS:')
    print(f'   📧 {usuario_prop.email} (propietario → inquilino)')
    print(f'   📧 {usuario_inq.email} (inquilino → propietario)')
    print()
    
    with transaction.atomic():
        # Intercambiar SOLO estos dos usuarios
        usuario_prop.persona.tipo_persona = 'inquilino'
        usuario_inq.persona.tipo_persona = 'propietario'
        
        usuario_prop.persona.save()
        usuario_inq.persona.save()
        
        # Sincronizar SOLO estos dos usuarios
        sincronizar_roles_con_tipo_persona(usuario_prop.persona, usuario_prop)
        sincronizar_roles_con_tipo_persona(usuario_inq.persona, usuario_inq)
        
        print('✅ Intercambio realizado')
        print()
        
        # Verificar estado de TODOS los usuarios después
        print('📋 ESTADO DESPUÉS DEL INTERCAMBIO:')
        
        usuarios_cambiados = 0
        usuarios_sin_cambios = 0
        
        for usuario in Usuario.objects.all():
            if not usuario.persona:
                continue
                
            # Buscar estado anterior
            estado_anterior = next((u for u in todos_usuarios_antes if u['email'] == usuario.email), None)
            if not estado_anterior:
                continue
                
            estado_actual = {
                'email': usuario.email,
                'tipo_persona': usuario.persona.tipo_persona,
                'roles': [r.nombre for r in usuario.roles.all()]
            }
            
            # Verificar si hubo cambios
            if (estado_anterior['tipo_persona'] != estado_actual['tipo_persona'] or 
                estado_anterior['roles'] != estado_actual['roles']):
                usuarios_cambiados += 1
                print(f'   🔄 CAMBIÓ: {usuario.email}')
                print(f'      Antes: {estado_anterior["tipo_persona"]} | {estado_anterior["roles"]}')
                print(f'      Ahora: {estado_actual["tipo_persona"]} | {estado_actual["roles"]}')
            else:
                usuarios_sin_cambios += 1
                print(f'   ✅ SIN CAMBIO: {usuario.email} | {estado_actual["tipo_persona"]} | {estado_actual["roles"]}')
        
        print()
        print('📊 RESUMEN:')
        print(f'   🔄 Usuarios que CAMBIARON: {usuarios_cambiados}')
        print(f'   ✅ Usuarios SIN CAMBIOS: {usuarios_sin_cambios}')
        print()
        
        if usuarios_cambiados == 2:
            print('✅ VERIFICACIÓN EXITOSA:')
            print('   - Solo los 2 usuarios involucrados en la transferencia cambiaron')
            print('   - Todos los demás usuarios mantienen sus roles normales')
            print('   - El sistema funciona correctamente de forma SELECTIVA')
        else:
            print('❌ ERROR: Más usuarios de los esperados fueron afectados')
        
        print()
        print('🔄 REVIRTIENDO CAMBIOS...')
        
        # Revertir los cambios
        usuario_prop.persona.tipo_persona = 'propietario'
        usuario_inq.persona.tipo_persona = 'inquilino'
        usuario_prop.persona.save()
        usuario_inq.persona.save()
        
        sincronizar_roles_con_tipo_persona(usuario_prop.persona, usuario_prop)
        sincronizar_roles_con_tipo_persona(usuario_inq.persona, usuario_inq)
        
        print('✅ Estado original restaurado')

if __name__ == '__main__':
    verificar_usuarios_no_afectados()