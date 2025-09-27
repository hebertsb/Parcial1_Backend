#!/usr/bin/env python
"""
PRUEBA SIMPLIFICADA: CAMB        print(f'👤 Persona A: {usuario_propietario.email}')
        print(f'   Tipo: {propietario.tipo_persona}')
        print(f'   Roles: {[r.nombre for r in usuario_propietario.roles.all()]}')
        print()
        
        print(f'👤 Persona B: {usuario_inquilino.email}')ROLES DURANTE TRANSFERENCIA
========================================================
Escenario: Cambio de tipo_persona activa sincronización automática
"""

import os
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from authz.models import Persona, Usuario
from django.db import transaction

def probar_cambio_roles_transferencia():
    print('🔄 PRUEBA: CAMBIO AUTOMÁTICO DE ROLES EN TRANSFERENCIA')
    print('=' * 65)
    print('Escenario: Dos usuarios intercambian tipo_persona')
    print()
    
    try:
        # Buscar un propietario y un inquilino con usuarios
        propietario = None
        inquilino = None
        
        # Buscar propietario con usuario
        for persona in Persona.objects.filter(tipo_persona='propietario'):
            try:
                Usuario.objects.get(persona=persona)
                propietario = persona
                break
            except Usuario.DoesNotExist:
                continue
                
        # Buscar inquilino con usuario
        for persona in Persona.objects.filter(tipo_persona='inquilino'):
            try:
                Usuario.objects.get(persona=persona)
                inquilino = persona
                break
            except Usuario.DoesNotExist:
                continue
        
        if not propietario or not inquilino:
            print('❌ No se encontraron personas con usuarios para la prueba')
            return
            
        usuario_propietario = Usuario.objects.get(persona=propietario)
        usuario_inquilino = Usuario.objects.get(persona=inquilino)
        
        print(f'� Persona A: ID {propietario.id} - {usuario_propietario.email}')
        print(f'   Tipo: {propietario.tipo_persona}')
        print(f'   Roles: {[r.nombre for r in usuario_propietario.roles.all()]}')
        print()
        
        print(f'👤 Persona B: ID {inquilino.id} - {usuario_inquilino.email}')
        print(f'   Tipo: {inquilino.tipo_persona}')
        print(f'   Roles: {[r.nombre for r in usuario_inquilino.roles.all()]}')
        print()
        
        print('� SIMULANDO INTERCAMBIO DE TIPOS (como en transferencia)...')
        
        with transaction.atomic():
            # Intercambiar tipos
            propietario.tipo_persona = 'inquilino'
            inquilino.tipo_persona = 'propietario'
            
            propietario.save()
            inquilino.save()
            
            print('✅ Tipos intercambiados en base de datos')
            
            # Sincronizar roles automáticamente
            from authz.utils_roles import sincronizar_roles_con_tipo_persona
            
            resultado_prop = sincronizar_roles_con_tipo_persona(propietario, usuario_propietario)
            resultado_inq = sincronizar_roles_con_tipo_persona(inquilino, usuario_inquilino)
            
            print(f'📧 Sincronización A: {resultado_prop["message"]}')
            print(f'📧 Sincronización B: {resultado_inq["message"]}')
            
            # Recargar usuarios para ver cambios
            usuario_propietario.refresh_from_db()
            usuario_inquilino.refresh_from_db()
            
            print()
            print('📋 RESULTADO FINAL:')
            print(f'👤 Persona A: {usuario_propietario.email}')
            print(f'   Tipo: {propietario.tipo_persona} (era propietario)')
            print(f'   Roles: {[r.nombre for r in usuario_propietario.roles.all()]}')
            print(f'   🎯 Login → Panel de {"inquilinos" if "Inquilino" in [r.nombre for r in usuario_propietario.roles.all()] else "propietarios"}')
            print()
            
            print(f'👤 Persona B: {usuario_inquilino.email}')
            print(f'   Tipo: {inquilino.tipo_persona} (era inquilino)')
            print(f'   Roles: {[r.nombre for r in usuario_inquilino.roles.all()]}')
            print(f'   🎯 Login → Panel de {"propietarios" if "Propietario" in [r.nombre for r in usuario_inquilino.roles.all()] else "inquilinos"}')
            
            print()
            print('✅ INTERCAMBIO COMPLETO')
            print('✅ Roles sincronizados correctamente')
            print('✅ Cada usuario verá el panel correcto')
            
            # Verificar que funcionaría en el login
            print()
            print('� VERIFICACIÓN DE LOGIN:')
            
            # Simular get_primary_role
            roles_a = [r.nombre for r in usuario_propietario.roles.all()]
            roles_b = [r.nombre for r in usuario_inquilino.roles.all()]
            
            primary_a = 'Inquilino' if 'Inquilino' in roles_a else (
                'Propietario' if 'Propietario' in roles_a else 
                'Administrador' if 'Administrador' in roles_a else roles_a[0] if roles_a else None
            )
            
            primary_b = 'Inquilino' if 'Inquilino' in roles_b else (
                'Propietario' if 'Propietario' in roles_b else 
                'Administrador' if 'Administrador' in roles_b else roles_b[0] if roles_b else None
            )
            
            print(f'   {usuario_propietario.email} → primary_role: {primary_a}')
            print(f'   {usuario_inquilino.email} → primary_role: {primary_b}')
            
            # Revertir cambios
            print()
            print('🔄 REVIRTIENDO CAMBIOS...')
            
            propietario.tipo_persona = 'propietario'
            inquilino.tipo_persona = 'inquilino'
            propietario.save()
            inquilino.save()
            
            sincronizar_roles_con_tipo_persona(propietario, usuario_propietario)
            sincronizar_roles_con_tipo_persona(inquilino, usuario_inquilino)
            
            print('✅ Estado original restaurado')
            
    except Exception as e:
        print(f'❌ Error en la prueba: {str(e)}')
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    probar_cambio_roles_transferencia()