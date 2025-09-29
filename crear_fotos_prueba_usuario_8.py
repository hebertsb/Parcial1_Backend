#!/usr/bin/env python3
"""
Script para crear fotos de reconocimiento de prueba para el usuario ID 8
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

def crear_fotos_prueba_usuario_8():
    print('🔧 CREANDO FOTOS DE PRUEBA PARA USUARIO ID 8')
    print('=' * 60)
    
    # Obtener usuario y copropietario
    usuario = Usuario.objects.filter(id=8).first()
    copropietario = Copropietarios.objects.filter(usuario_sistema_id=8).first()
    
    if not usuario:
        print('❌ Usuario ID 8 no encontrado')
        return
        
    if not copropietario:
        print('❌ Copropietario para usuario ID 8 no encontrado')
        return
    
    print(f'✅ Usuario: {usuario.email}')
    print(f'✅ Copropietario: {copropietario.nombres} {copropietario.apellidos} (ID: {copropietario.id})')
    
    # Verificar fotos existentes
    fotos_existentes = ReconocimientoFacial.objects.filter(copropietario=copropietario)
    print(f'📷 Fotos existentes: {fotos_existentes.count()}')
    
    if fotos_existentes.count() >= 5:
        print('✅ Ya tiene suficientes fotos, no necesita crear más')
        return
    
    # Crear 5 fotos de prueba
    print(f'\n🔧 Creando 5 fotos de reconocimiento de prueba...')
    
    urls_fotos_ejemplo = [
        f"https://dropbox.com/s/test1/foto_reconocimiento_usuario8_1.jpg",
        f"https://dropbox.com/s/test2/foto_reconocimiento_usuario8_2.jpg", 
        f"https://dropbox.com/s/test3/foto_reconocimiento_usuario8_3.jpg",
        f"https://dropbox.com/s/test4/foto_reconocimiento_usuario8_4.jpg",
        f"https://dropbox.com/s/test5/foto_reconocimiento_usuario8_5.jpg"
    ]
    
    # Eliminar fotos existentes si las hay
    if fotos_existentes.exists():
        fotos_existentes.delete()
        print('🗑️ Eliminadas fotos existentes')
    
    # Crear UNA entrada de reconocimiento facial con múltiples URLs
    import json
    
    foto = ReconocimientoFacial.objects.create(
        copropietario=copropietario,
        proveedor_ia='Local',
        vector_facial=json.dumps(urls_fotos_ejemplo),  # Todas las URLs en el vector
        imagen_referencia_url=urls_fotos_ejemplo[0],  # Primera foto como referencia
        activo=True
    )
    
    print(f'   ✅ Reconocimiento creado: ID {foto.id}')
    print(f'   📷 Total URLs en vector_facial: {len(urls_fotos_ejemplo)}')
    fotos_creadas = [foto]
    
    print(f'\n🎯 RESULTADO:')
    print(f'   Registro de reconocimiento creado: {len(fotos_creadas)}')
    print(f'   URLs de fotos en vector: {len(urls_fotos_ejemplo)}')
    print(f'   Copropietario ID: {copropietario.id}')
    print(f'   Usuario ID: {usuario.id}')
    
    return fotos_creadas

def verificar_endpoint_usuarios_reconocimiento():
    print(f'\n🧪 VERIFICANDO ENDPOINT usuarios-reconocimiento:')
    print('=' * 50)
    
    # Simular la consulta del endpoint
    copropietarios_con_fotos = Copropietarios.objects.filter(
        reconocimiento_facial__isnull=False
    ).distinct()
    
    print(f'Total copropietarios con fotos: {copropietarios_con_fotos.count()}')
    
    for copro in copropietarios_con_fotos:
        usuario_id = copro.usuario_sistema_id if copro.usuario_sistema_id else "Sin usuario"
        fotos_count = ReconocimientoFacial.objects.filter(copropietario=copro).count()
        print(f'  - Copropietario ID {copro.id}: {copro.nombres} {copro.apellidos}')
        print(f'    Usuario ID: {usuario_id}, Email: {copro.email}')
        print(f'    Fotos: {fotos_count}')
    
    # Verificar específicamente usuario ID 8
    usuario_8_copro = copropietarios_con_fotos.filter(usuario_sistema_id=8).first()
    if usuario_8_copro:
        print(f'\n✅ ¡Usuario ID 8 ahora aparece en el endpoint!')
        print(f'   Copropietario ID: {usuario_8_copro.id}')
        fotos = ReconocimientoFacial.objects.filter(copropietario=usuario_8_copro)
        print(f'   Total fotos: {fotos.count()}')
    else:
        print(f'\n❌ Usuario ID 8 aún no aparece en el endpoint')

if __name__ == "__main__":
    fotos = crear_fotos_prueba_usuario_8()
    verificar_endpoint_usuarios_reconocimiento()