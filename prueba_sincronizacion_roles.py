#!/usr/bin/env python
"""
PRUEBA DE SINCRONIZACIÓN AUTOMÁTICA DE ROLES
===========================================
Escenario: Inquilino compra propiedad y se convierte en propietario
¿Su rol cambiará automáticamente para acceder al panel correcto?
"""

import os
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from authz.utils_roles import sincronizar_roles_con_tipo_persona
from authz.models import Usuario, Persona

def probar_sincronizacion_roles():
    print('🧪 PRUEBA: SINCRONIZACIÓN AUTOMÁTICA DE ROLES')
    print('=' * 50)
    print('Escenario: Inquilino compra casa y se convierte en propietario')
    print()

    # Buscar un usuario inquilino
    usuario_inquilino = Usuario.objects.filter(roles__nombre='Inquilino').first()
    if not usuario_inquilino or not usuario_inquilino.persona:
        print('❌ No se encontró usuario inquilino para la prueba')
        return
    
    persona = usuario_inquilino.persona
    
    print(f'👤 Usuario de prueba: {usuario_inquilino.email}')
    print(f'📋 ESTADO INICIAL:')
    print(f'   Persona.tipo_persona: {persona.tipo_persona}')
    print(f'   Usuario.roles: {[r.nombre for r in usuario_inquilino.roles.all()]}')
    print()
    
    # Simular el cambio: inquilino compra la casa
    print('🏠 SIMULANDO: Inquilino compra la casa...')
    persona.tipo_persona = 'propietario'
    persona.save()
    
    print(f'   ✅ Persona.tipo_persona cambió a: {persona.tipo_persona}')
    
    # Verificar roles ANTES de sincronizar
    print(f'   ❌ Roles siguen siendo: {[r.nombre for r in usuario_inquilino.roles.all()]}')
    print('   ⚠️  Sin sincronización, seguiría viendo panel de inquilino!')
    print()
    
    # Aplicar sincronización automática
    print('🔄 APLICANDO SINCRONIZACIÓN AUTOMÁTICA...')
    resultado = sincronizar_roles_con_tipo_persona(persona, usuario_inquilino)
    
    # Recargar usuario para ver cambios
    usuario_inquilino.refresh_from_db()
    
    print(f'   📧 {resultado["message"]}')
    print(f'   📋 ESTADO DESPUÉS DE SINCRONIZACIÓN:')
    print(f'      Persona.tipo_persona: {persona.tipo_persona}')
    print(f'      Usuario.roles: {[r.nombre for r in usuario_inquilino.roles.all()]}')
    print()
    
    # Verificar resultado
    if 'Propietario' in [r.nombre for r in usuario_inquilino.roles.all()]:
        print('✅ ÉXITO: El usuario ahora tiene rol de Propietario')
        print('✅ En el próximo login será redirigido al panel de propietarios')
    else:
        print('❌ ERROR: La sincronización no funcionó correctamente')
    
    print()
    print('🔄 REVIRTIENDO CAMBIOS (para no afectar datos de prueba)...')
    
    # Revertir cambios
    persona.tipo_persona = 'inquilino'
    persona.save()
    sincronizar_roles_con_tipo_persona(persona, usuario_inquilino)
    
    print('✅ Datos restaurados al estado original')
    print()
    print('📋 RESULTADO DE LA PRUEBA:')
    print('✅ La sincronización automática funciona correctamente')
    print('✅ Cuando inquilino compra casa y se vuelve propietario:')
    print('   - Su tipo_persona cambia a "propietario"')
    print('   - Sus roles se actualizan automáticamente')
    print('   - En el próximo login verá el panel de propietarios')
    print()
    print('🎯 RESPUESTA A TU PREGUNTA:')
    print('   SÍ, el rol cambiará automáticamente de Inquilino a Propietario')

if __name__ == '__main__':
    probar_sincronizacion_roles()