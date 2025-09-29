#!/usr/bin/env python3
"""
Script para crear el copropietario faltante para el usuario ID 8
"""

import os
import sys
import django

# Setup Django
sys.path.append('.')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from authz.models import Usuario
from seguridad.models import Copropietarios

def crear_copropietario_usuario_8():
    print('🔧 SOLUCIONANDO PROBLEMA CRÍTICO - USUARIO ID 8')
    print('=' * 60)
    
    # Obtener usuario ID 8
    usuario = Usuario.objects.filter(id=8).first()
    if not usuario:
        print('❌ Usuario ID 8 no encontrado')
        return
    
    print(f'✅ Usuario encontrado: {usuario.email}')
    print(f'   Nombre: {usuario.persona.nombre} {usuario.persona.apellido}')
    
    # Verificar si ya existe copropietario
    copropietario_existente = Copropietarios.objects.filter(email=usuario.email).first()
    if copropietario_existente:
        print(f'✅ Copropietario ya existe con ID: {copropietario_existente.id}')
        
        # Verificar si está asociado al usuario
        if copropietario_existente.usuario_sistema_id != usuario.id:
            print(f'🔧 Asociando copropietario al usuario ID 8...')
            copropietario_existente.usuario_sistema_id = usuario.id
            copropietario_existente.save()
            print(f'✅ Copropietario asociado correctamente')
        
        return copropietario_existente
    
    # Crear nuevo copropietario
    print('🔧 Creando nuevo copropietario para usuario ID 8...')
    
    copropietario = Copropietarios.objects.create(
        nombres=usuario.persona.nombre,
        apellidos=usuario.persona.apellido,
        email=usuario.email,
        telefono=usuario.persona.telefono if usuario.persona else '',
        numero_documento='DOC_' + str(usuario.id).zfill(6),  # Documento único
        tipo_documento='CI',
        unidad_residencial='V' + str(usuario.id).zfill(3),  # Unidad única
        tipo_residente='Propietario',
        activo=True,
        usuario_sistema=usuario
    )
    
    print(f'✅ Copropietario creado exitosamente:')
    print(f'   ID: {copropietario.id}')
    print(f'   Nombre: {copropietario.nombres} {copropietario.apellidos}')
    print(f'   Email: {copropietario.email}')
    print(f'   Unidad: {copropietario.unidad_residencial}')
    print(f'   Usuario asociado: {copropietario.usuario_sistema_id}')
    
    return copropietario

def verificar_solucion():
    print(f'\n🧪 VERIFICANDO SOLUCIÓN:')
    print('=' * 30)
    
    # Verificar copropietario
    copropietario = Copropietarios.objects.filter(email='tito@gmail.com').first()
    if copropietario:
        print(f'✅ Copropietario encontrado: ID {copropietario.id}')
        print(f'   Usuario asociado: {copropietario.usuario_sistema_id}')
        
        # Simular consulta del endpoint
        from seguridad.models import ReconocimientoFacial
        
        copropietarios_con_fotos = Copropietarios.objects.filter(
            reconocimiento_facial__isnull=False
        ).distinct()
        
        usuario_8_en_consulta = copropietarios_con_fotos.filter(usuario_sistema_id=8).first()
        if usuario_8_en_consulta:
            print(f'✅ Usuario ID 8 ahora aparecerá en el endpoint')
        else:
            print(f'⚠️ Usuario ID 8 aún no aparece (necesita fotos de reconocimiento)')
            
            # Verificar si tiene fotos
            fotos = ReconocimientoFacial.objects.filter(copropietario=copropietario)
            print(f'   Fotos actuales: {fotos.count()}')
    else:
        print(f'❌ Copropietario aún no existe')

if __name__ == "__main__":
    copropietario = crear_copropietario_usuario_8()
    verificar_solucion()