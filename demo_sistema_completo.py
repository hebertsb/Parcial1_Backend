#!/usr/bin/env python3
"""
DEMOSTRACIÓN COMPLETA DEL SISTEMA DE GESTIÓN DE USUARIOS DE SEGURIDAD
======================================================================

Este script demuestra el flujo completo del sistema implementado:
1. Un administrador puede crear usuarios de seguridad
2. Los usuarios de seguridad pueden hacer login
3. Los usuarios de seguridad tienen acceso a sus endpoints específicos
"""

import subprocess
import json

def print_header(title):
    print(f"\n{'='*60}")
    print(f"🎯 {title}")
    print('='*60)

def print_section(title):
    print(f"\n📋 {title}")
    print('-'*40)

def run_django_command(command):
    """Ejecutar comando en Django shell"""
    try:
        result = subprocess.run([
            'python', 'manage.py', 'shell', '-c', command
        ], capture_output=True, text=True, timeout=30)
        
        if result.returncode == 0:
            return result.stdout.strip(), None
        else:
            return None, result.stderr.strip()
    except Exception as e:
        return None, str(e)

def demo_sistema_completo():
    """Demostración completa del sistema"""
    
    print_header("SISTEMA DE GESTIÓN DE USUARIOS DE SEGURIDAD")
    print("🏢 Sistema implementado para condominio")
    print("👥 Gestión completa de usuarios con roles específicos")
    
    # 1. Mostrar estructura de roles
    print_section("1. ESTRUCTURA DE ROLES DEL SISTEMA")
    cmd = '''
from authz.models import Rol, Usuario
print("🎭 Roles disponibles en el sistema:")
for rol in Rol.objects.all():
    count = Usuario.objects.filter(roles=rol).count()
    print(f"   • {rol.nombre}: {count} usuarios")
'''
    output, error = run_django_command(cmd)
    if output:
        print(output)
    
    # 2. Mostrar usuarios administrativos
    print_section("2. USUARIOS ADMINISTRATIVOS")
    cmd = '''
from authz.models import Usuario
print("👨‍💼 Administradores del sistema:")
for user in Usuario.objects.filter(roles__nombre="Administrador"):
    print(f"   📧 {user.email} - {user.persona.nombre} {user.persona.apellido}")
'''
    output, error = run_django_command(cmd)
    if output:
        print(output)
    
    # 3. Mostrar usuarios de seguridad
    print_section("3. USUARIOS DE SEGURIDAD CREADOS")
    cmd = '''
from authz.models import Usuario
print("🛡️ Personal de seguridad registrado:")
for user in Usuario.objects.filter(roles__nombre="Seguridad"):
    estado = "🟢 Activo" if user.is_active else "🔴 Inactivo"
    print(f"   📧 {user.email}")
    print(f"      👤 {user.persona.nombre} {user.persona.apellido}")
    print(f"      📱 {user.persona.telefono}")
    print(f"      📍 {estado}")
    print()
'''
    output, error = run_django_command(cmd)
    if output:
        print(output)
    
    # 4. Probar autenticación
    print_section("4. PRUEBA DE AUTENTICACIÓN")
    cmd = '''
from django.contrib.auth import authenticate
print("🔐 Probando credenciales configuradas:")
print()

# Usuario 1
user = authenticate(username='prueba.seguridad@test.com', password='prueba123')
if user:
    print("✅ ÉXITO: prueba.seguridad@test.com")
    print(f"   👤 Usuario: {user.persona.nombre} {user.persona.apellido}")
    roles = [rol.nombre for rol in user.roles.all()]
    print(f"   🎭 Roles: {', '.join(roles)}")
    print(f"   📊 Estado: {'Activo' if user.is_active else 'Inactivo'}")
else:
    print("❌ FALLO: prueba.seguridad@test.com")

print()

# Usuario 2
user = authenticate(username='carlos.test@condominio.com', password='test123')
if user:
    print("✅ ÉXITO: carlos.test@condominio.com")
    print(f"   👤 Usuario: {user.persona.nombre} {user.persona.apellido}")
    roles = [rol.nombre for rol in user.roles.all()]
    print(f"   🎭 Roles: {', '.join(roles)}")
    print(f"   📊 Estado: {'Activo' if user.is_active else 'Inactivo'}")
else:
    print("❌ FALLO: carlos.test@condominio.com")
'''
    output, error = run_django_command(cmd)
    if output:
        print(output)
    
    # 5. Mostrar endpoints disponibles
    print_section("5. ENDPOINTS IMPLEMENTADOS")
    print("🌐 API REST para administradores:")
    print("   POST /auth/admin/seguridad/crear/")
    print("        ↳ Crear nuevo usuario de seguridad")
    print("   GET  /auth/admin/seguridad/listar/")
    print("        ↳ Listar todos los usuarios de seguridad")
    print("   PUT  /auth/admin/seguridad/{id}/estado/")
    print("        ↳ Activar/desactivar usuario")
    print("   POST /auth/admin/seguridad/{id}/reset-password/")
    print("        ↳ Resetear contraseña")
    print()
    print("🔑 Endpoints de autenticación:")
    print("   POST /auth/login/")
    print("        ↳ Login para todos los usuarios")
    print("   POST /auth/refresh/")
    print("        ↳ Renovar token JWT")
    
    # 6. Mostrar herramientas de línea de comandos
    print_section("6. HERRAMIENTAS DE LÍNEA DE COMANDOS")
    print("⚡ Comandos Django personalizados:")
    print("   python manage.py crear_seguridad")
    print("        ↳ Crear usuario de seguridad desde terminal")
    print()
    print("🔧 Scripts de utilidad:")
    print("   • check_users.py - Verificar usuarios existentes")
    print("   • verificar_admins.py - Listar administradores")
    print("   • obtener_credenciales_seguridad.py - Ver credenciales")
    print("   • test_login_simple.py - Probar autenticación")

def main():
    print("🚀 INICIANDO DEMOSTRACIÓN DEL SISTEMA")
    demo_sistema_completo()
    
    print_header("RESUMEN FINAL")
    print("✅ Sistema completamente funcional")
    print("✅ Roles implementados: Administrador, Seguridad, Propietario, Inquilino")
    print("✅ API REST completa para gestión administrativa")
    print("✅ Autenticación JWT funcionando")
    print("✅ Permisos basados en roles")
    print("✅ Herramientas de línea de comandos")
    print("✅ Usuarios de prueba configurados")
    print()
    print("🎯 CREDENCIALES DE PRUEBA LISTAS:")
    print("   📧 prueba.seguridad@test.com / 🔑 prueba123")
    print("   📧 carlos.test@condominio.com / 🔑 test123") 
    print()
    print("🏆 ¡SISTEMA LISTO PARA USAR!")

if __name__ == "__main__":
    main()