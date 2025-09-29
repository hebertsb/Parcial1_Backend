#!/usr/bin/env python
"""
Script para obtener credenciales de propietarios para pruebas
"""
import os
import sys
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from authz.models import Usuario, Persona
from seguridad.models import Copropietarios, ReconocimientoFacial
from django.contrib.auth.hashers import make_password
import json

def main():
    print("=" * 80)
    print("🏠 CREDENCIALES DE PROPIETARIOS PARA PRUEBAS")
    print("=" * 80)
    
    # Obtener todos los propietarios
    propietarios = Copropietarios.objects.filter(activo=True).order_by('unidad_residencial')
    
    if not propietarios.exists():
        print("❌ No se encontraron propietarios activos")
        return
    
    print(f"📊 Total de propietarios encontrados: {propietarios.count()}")
    print()
    
    credenciales = []
    
    for prop in propietarios:
        print(f"🏡 PROPIETARIO: {prop.nombres} {prop.apellidos}")
        print(f"   📋 Documento: {prop.numero_documento}")
        print(f"   🏠 Unidad: {prop.unidad_residencial}")
        print(f"   📧 Email: {prop.email or 'No registrado'}")
        print(f"   📱 Teléfono: {prop.telefono or 'No registrado'}")
        
        # Buscar usuario del sistema
        usuario_sistema = prop.usuario_sistema
        
        if usuario_sistema:
            print(f"   👤 Usuario Sistema: {usuario_sistema.username}")
            print(f"   🔑 Email Sistema: {usuario_sistema.email}")
            print(f"   ✅ Estado: {'Activo' if usuario_sistema.is_active else 'Inactivo'}")
            
            # Verificar si tiene reconocimiento facial
            reconocimiento = ReconocimientoFacial.objects.filter(copropietario=prop).first()
            if reconocimiento:
                fotos_count = 0
                if reconocimiento.fotos_urls:
                    try:
                        fotos_list = json.loads(reconocimiento.fotos_urls)
                        if isinstance(fotos_list, list):
                            fotos_count = len(fotos_list)
                    except:
                        pass
                print(f"   📸 Fotos reconocimiento: {fotos_count}")
            else:
                print(f"   📸 Fotos reconocimiento: 0")
            
            # Credenciales sugeridas
            credenciales.append({
                'username': usuario_sistema.username,
                'email': usuario_sistema.email,
                'nombre_completo': f"{prop.nombres} {prop.apellidos}",
                'documento': prop.numero_documento,
                'unidad': prop.unidad_residencial,
                'password_sugerida': f"{prop.numero_documento}123"  # Patrón común
            })
            
        else:
            print(f"   ❌ No tiene usuario del sistema")
            
        print(f"   🔗 ID Copropietario: {prop.id}")
        print("-" * 60)
    
    print("\n" + "=" * 80)
    print("🔑 CREDENCIALES PARA PRUEBAS")
    print("=" * 80)
    
    if credenciales:
        print("📝 Para hacer login, usa estas credenciales:")
        print()
        
        for i, cred in enumerate(credenciales, 1):
            print(f"{i}. {cred['nombre_completo']} ({cred['unidad']})")
            print(f"   Username: {cred['username']}")
            print(f"   Email: {cred['email']}")
            print(f"   Password sugerida: {cred['password_sugerida']}")
            print(f"   Documento: {cred['documento']}")
            print()
    
    print("=" * 80)
    print("🔧 COMANDOS ADICIONALES")
    print("=" * 80)
    
    print("Para crear/resetear contraseña de un usuario específico:")
    print("python manage.py shell")
    print(">>> from authz.models import Usuario")
    print(">>> user = Usuario.objects.get(username='NOMBRE_USUARIO')")
    print(">>> user.set_password('NUEVA_CONTRASEÑA')")
    print(">>> user.save()")
    print()
    
    print("Para crear un usuario de prueba:")
    print("python crear_usuario_prueba.py")
    print()
    
    # Verificar usuarios de seguridad
    print("=" * 80)
    print("👮 USUARIOS DE SEGURIDAD")
    print("=" * 80)
    
    usuarios_seguridad = Usuario.objects.filter(roles__nombre__icontains='Seguridad')
    
    if usuarios_seguridad.exists():
        for user in usuarios_seguridad:
            print(f"👮 Usuario Seguridad: {user.username}")
            print(f"   📧 Email: {user.email}")
            print(f"   ✅ Activo: {user.is_active}")
            roles = [rol.nombre for rol in user.roles.all()]
            print(f"   🏷️ Roles: {', '.join(roles)}")
            print()
    else:
        print("❌ No se encontraron usuarios de seguridad")
        print("💡 Crear uno con: python crear_usuario_seguridad.py")
    
    print("=" * 80)
    print("✅ CONSULTA COMPLETADA")
    print("=" * 80)

if __name__ == '__main__':
    main()