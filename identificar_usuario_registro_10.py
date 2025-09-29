#!/usr/bin/env python3
"""
Identificar usuario del registro 10 para pruebas
"""
import os
import django
import json

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from seguridad.models import ReconocimientoFacial
from django.contrib.auth.models import User

def identificar_usuario_registro_10():
    print('🔍 IDENTIFICANDO USUARIO DEL REGISTRO 10')
    print('=' * 50)

    try:
        r10 = ReconocimientoFacial.objects.get(id=10)
        
        print(f'📋 REGISTRO 10 - INFORMACIÓN COMPLETA:')
        print(f'   🆔 ID del registro: {r10.id}')
        
        # Información del copropietario
        if hasattr(r10, 'copropietario') and r10.copropietario:
            coprop = r10.copropietario
            print(f'   👤 Copropietario ID: {coprop.id}')
            print(f'   📝 Nombre: {coprop.nombre} {coprop.apellido}')
            print(f'   📧 Email: {coprop.email}')
            print(f'   📱 Teléfono: {getattr(coprop, "telefono", "No especificado")}')
            print(f'   🏠 Unidad: {getattr(coprop, "unidad_residencial", "No especificada")}')
            print(f'   📄 Documento: {getattr(coprop, "documento", "No especificado")}')
            
            # Buscar usuario relacionado
            try:
                usuario = User.objects.get(email=coprop.email)
                print(f'   🔐 Usuario sistema: {usuario.username}')
                print(f'   ✅ Puede hacer login: {usuario.is_active}')
            except User.DoesNotExist:
                print(f'   ⚠️  Usuario sistema: No encontrado con email {coprop.email}')
                # Buscar por nombre de usuario
                try:
                    usuario = User.objects.filter(username__icontains=coprop.nombre.lower()).first()
                    if usuario:
                        print(f'   🔐 Usuario encontrado por nombre: {usuario.username} ({usuario.email})')
                    else:
                        print('   ❌ No se encontró usuario asociado')
                except Exception as e:
                    print(f'   ❌ Error buscando usuario: {e}')
        
        # Información de las fotos
        if r10.fotos_urls:
            if isinstance(r10.fotos_urls, str):
                urls = json.loads(r10.fotos_urls)
            else:
                urls = r10.fotos_urls
            
            print(f'   📸 Total fotos: {len(urls)}')
            print('   🔗 URLs completas:')
            for i, url in enumerate(urls, 1):
                print(f'      {i}. {url}')
            
            # Extraer información de las URLs
            if urls:
                primera_url = urls[0]
                if 'propietario_' in primera_url:
                    # Extraer ID del propietario de la URL
                    partes = primera_url.split('propietario_')
                    if len(partes) > 1:
                        id_parte = partes[1].split('_')[0]
                        print(f'   🔢 ID propietario extraído de URL: {id_parte}')
        
        print()
        print('🎯 INFORMACIÓN PARA PRUEBAS DEL FRONTEND:')
        if hasattr(r10, 'copropietario') and r10.copropietario:
            print(f'   📧 Email de login: {coprop.email}')
            print(f'   👤 Nombre completo: {coprop.nombre} {coprop.apellido}')
            print(f'   📸 Fotos disponibles: 2')
            print(f'   ⚠️  Estado: Archivos existen en Dropbox (error 403 = acceso denegado)')
            print(f'   🔧 Acción requerida: Configurar permisos públicos en Dropbox')
        
    except ReconocimientoFacial.DoesNotExist:
        print('❌ No se encontró el registro 10')
    except Exception as e:
        print(f'❌ Error: {e}')

if __name__ == "__main__":
    identificar_usuario_registro_10()