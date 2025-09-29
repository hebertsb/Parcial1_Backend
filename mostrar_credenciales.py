#!/usr/bin/env python
"""
Script simplificado para mostrar credenciales de prueba
"""
import os
import sys
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from authz.models import Usuario, Persona, Rol
from seguridad.models import Copropietarios, ReconocimientoFacial
import json

def main():
    print("=" * 80)
    print("🔑 CREDENCIALES DE ACCESO PARA PRUEBAS")
    print("=" * 80)
    print()
    
    # 1. Mostrar usuarios existentes
    print("👤 USUARIOS EXISTENTES:")
    print("-" * 50)
    
    usuarios = Usuario.objects.filter(is_active=True)
    
    if not usuarios.exists():
        print("❌ No se encontraron usuarios activos")
    else:
        for usuario in usuarios:
            print(f"📧 Email: {usuario.email}")
            print(f"   👤 Nombre: {usuario.nombres} {usuario.apellidos}")
            
            roles = [rol.nombre for rol in usuario.roles.all()]
            print(f"   🏷️ Roles: {', '.join(roles) if roles else 'Sin roles'}")
            
            # Verificar si es copropietario
            try:
                copropietario = Copropietarios.objects.get(usuario_sistema=usuario)
                print(f"   🏠 Unidad: {copropietario.unidad_residencial}")
                print(f"   📋 Documento: {copropietario.numero_documento}")
                
                # Verificar fotos
                reconocimiento = ReconocimientoFacial.objects.filter(copropietario=copropietario).first()
                if reconocimiento and reconocimiento.fotos_urls:
                    try:
                        fotos_list = json.loads(reconocimiento.fotos_urls)
                        if isinstance(fotos_list, list):
                            print(f"   📸 Fotos: {len(fotos_list)}")
                    except:
                        print(f"   📸 Fotos: 0")
                else:
                    print(f"   📸 Fotos: 0")
                    
            except Copropietarios.DoesNotExist:
                print(f"   ℹ️ No es copropietario")
            
            print()
    
    print("=" * 80)
    print("🚀 CREDENCIALES LISTAS PARA USAR")
    print("=" * 80)
    
    print("🏠 PARA PROPIETARIOS:")
    propietarios_usuarios = Usuario.objects.filter(roles__nombre='Propietario', is_active=True)
    
    if propietarios_usuarios.exists():
        for usuario in propietarios_usuarios:
            print(f"   📧 Email: {usuario.email}")
            print(f"   🔑 Password sugerida: 123456 (resetear si es necesario)")
            print()
    else:
        print("   ❌ No hay usuarios propietarios configurados")
        print("   💡 Crear uno con el comando que aparece abajo")
    
    print("👮 PARA SEGURIDAD:")
    seguridad_usuarios = Usuario.objects.filter(roles__nombre__in=['Seguridad', 'security'], is_active=True)
    
    if seguridad_usuarios.exists():
        for usuario in seguridad_usuarios:
            print(f"   📧 Email: {usuario.email}")
            print(f"   🔑 Password sugerida: seguridad123 (resetear si es necesario)")
            print()
    else:
        print("   ❌ No hay usuarios de seguridad configurados")
        print("   💡 Crear uno con el comando que aparece abajo")
    
    print("=" * 80)
    print("🔧 COMANDOS PARA CREAR USUARIOS DE PRUEBA")
    print("=" * 80)
    
    print("Para crear usuario PROPIETARIO de prueba:")
    print("python -c \"")
    print("import os, django; os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings'); django.setup()")
    print("from authz.models import Usuario, Persona, Rol")
    print("from seguridad.models import Copropietarios")
    print()
    print("# Crear persona")
    print("persona = Persona.objects.create(nombre='Juan', apellido='Propietario', telefono='70123456')")
    print()
    print("# Crear usuario")
    print("usuario = Usuario.objects.create(email='propietario@test.com', persona=persona, is_active=True)")
    print("usuario.set_password('123456')")
    print("usuario.save()")
    print()
    print("# Asignar rol")
    print("rol, _ = Rol.objects.get_or_create(nombre='Propietario')")
    print("usuario.roles.add(rol)")
    print()
    print("# Crear copropietario")
    print("Copropietarios.objects.create(")
    print("    nombres='Juan', apellidos='Propietario',")
    print("    numero_documento='12345678', tipo_documento='CI',")
    print("    unidad_residencial='A-101', tipo_residente='Propietario',")
    print("    email='propietario@test.com', telefono='70123456',")
    print("    usuario_sistema=usuario, activo=True")
    print(")")
    print("print('✅ Usuario propietario creado: propietario@test.com / 123456')")
    print("\"")
    print()
    
    print("Para crear usuario SEGURIDAD de prueba:")
    print("python -c \"")
    print("import os, django; os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings'); django.setup()")
    print("from authz.models import Usuario, Persona, Rol")
    print()
    print("# Crear persona")
    print("persona = Persona.objects.create(nombre='Carlos', apellido='Seguridad', telefono='70987654')")
    print()
    print("# Crear usuario")
    print("usuario = Usuario.objects.create(email='seguridad@test.com', persona=persona, is_active=True)")
    print("usuario.set_password('seguridad123')")
    print("usuario.save()")
    print()
    print("# Asignar rol")
    print("rol, _ = Rol.objects.get_or_create(nombre='Seguridad')")
    print("usuario.roles.add(rol)")
    print("print('✅ Usuario seguridad creado: seguridad@test.com / seguridad123')")
    print("\"")
    print()
    
    print("Para RESETEAR contraseña de usuario existente:")
    print("python -c \"")
    print("import os, django; os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings'); django.setup()")
    print("from authz.models import Usuario")
    print("usuario = Usuario.objects.get(email='EMAIL_AQUI')")
    print("usuario.set_password('NUEVA_CONTRASEÑA')")
    print("usuario.save()")
    print("print('✅ Contraseña actualizada')")
    print("\"")
    
    print()
    print("=" * 80)
    print("📋 ENDPOINTS PARA PROBAR")
    print("=" * 80)
    print("🔐 Login:")
    print("POST http://localhost:8000/api/authz/auth/login/")
    print("Body: { \"username\": \"email@test.com\", \"password\": \"123456\" }")
    print()
    print("🏠 Panel Propietario - Mis fotos:")
    print("GET http://localhost:8000/api/authz/propietarios/mis-fotos/")
    print("Header: Authorization: Bearer <token>")
    print()
    print("📸 Subir foto:")
    print("POST http://localhost:8000/api/authz/propietarios/subir-foto/")
    print("Header: Authorization: Bearer <token>")
    print("Body: FormData con campo 'foto'")
    print()
    print("👮 Panel Seguridad - Ver usuarios:")
    print("GET http://localhost:8000/api/seguridad/usuarios-reconocimiento/")
    print("Header: Authorization: Bearer <token>")
    print()

if __name__ == '__main__':
    main()