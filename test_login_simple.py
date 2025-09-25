#!/usr/bin/env python3
"""
Script simple para probar el login de usuarios de seguridad
"""
import subprocess
import time
import json

def test_with_manage_py():
    """Probar credenciales usando manage.py shell"""
    print("🔐 PROBANDO CREDENCIALES CON DJANGO SHELL")
    print("=" * 50)
    
    # Comandos Python para ejecutar en el shell de Django
    test_commands = '''
from django.contrib.auth import authenticate
from authz.models import Usuario

print("\\n📊 USUARIOS DISPONIBLES:")
for user in Usuario.objects.filter(roles__nombre="Seguridad"):
    print(f"   📧 {user.email} - Estado: {'Activo' if user.is_active else 'Inactivo'}")

print("\\n🧪 PROBANDO AUTENTICACIÓN:")

# Probar usuario de prueba
user1 = authenticate(username='prueba.seguridad@test.com', password='prueba123')
if user1:
    print("   ✅ prueba.seguridad@test.com con 'prueba123' - LOGIN EXITOSO")
    print(f"      Usuario: {user1.persona.nombre} {user1.persona.apellido}")
    roles = [rol.nombre for rol in user1.roles.all()]
    print(f"      Roles: {', '.join(roles)}")
else:
    print("   ❌ prueba.seguridad@test.com con 'prueba123' - FALLÓ")

# Probar usuario carlos
user2 = authenticate(username='carlos.test@condominio.com', password='test123')
if user2:
    print("   ✅ carlos.test@condominio.com con 'test123' - LOGIN EXITOSO")
    print(f"      Usuario: {user2.persona.nombre} {user2.persona.apellido}")
    roles = [rol.nombre for rol in user2.roles.all()]
    print(f"      Roles: {', '.join(roles)}")
else:
    print("   ❌ carlos.test@condominio.com con 'test123' - FALLÓ")

print("\\n✨ Prueba completada")
'''
    
    try:
        # Ejecutar el comando en Django shell
        result = subprocess.run([
            'python', 'manage.py', 'shell', '-c', test_commands
        ], capture_output=True, text=True, timeout=30)
        
        if result.returncode == 0:
            print(result.stdout)
            if result.stderr:
                print("⚠️  Advertencias:")
                print(result.stderr)
        else:
            print("❌ Error al ejecutar el test:")
            print(result.stderr)
            return False
            
    except subprocess.TimeoutExpired:
        print("❌ Timeout al ejecutar el test")
        return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False
    
    return True

if __name__ == "__main__":
    print("🚀 INICIANDO PRUEBA DE CREDENCIALES")
    print("Usando Django shell para probar autenticación...")
    print()
    
    success = test_with_manage_py()
    
    if success:
        print("\n🎉 RESUMEN:")
        print("   ✅ Script ejecutado correctamente")
        print("   📝 Las credenciales fueron probadas usando Django authenticate()")
        print("   🔑 Credenciales disponibles:")
        print("      - prueba.seguridad@test.com / prueba123")
        print("      - carlos.test@condominio.com / test123")
    else:
        print("\n❌ PROBLEMAS ENCONTRADOS")
        print("   Revisa la configuración de Django")