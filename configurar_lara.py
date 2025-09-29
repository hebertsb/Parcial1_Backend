#!/usr/bin/env python3
"""
CONFIGURAR CREDENCIALES CORRECTAS PARA LARA
===========================================
"""

import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from authz.models import Usuario

def main():
    print("🔧 CONFIGURANDO CREDENCIALES PARA LARA")
    print("=" * 40)
    
    try:
        # Buscar usuario lara
        lara_user = Usuario.objects.get(email='lara@gmail.com')
        print(f"✅ Usuario encontrado: {lara_user.email}")
        print(f"   ID: {lara_user.id}")
        print(f"   Nombre: {lara_user.first_name} {lara_user.last_name}")
        
        # Establecer contraseña conocida
        lara_user.set_password('lara123')
        lara_user.save()
        print("✅ Contraseña establecida: lara123")
        
        # Verificar que la contraseña funciona
        if lara_user.check_password('lara123'):
            print("✅ Verificación de contraseña exitosa")
        else:
            print("❌ Error en verificación de contraseña")
            
        print("\n🎯 CREDENCIALES PARA EL FRONTEND:")
        print(f"   Email: {lara_user.email}")
        print(f"   Password: lara123")
        print(f"   User ID: {lara_user.id}")
        
    except Usuario.DoesNotExist:
        print("❌ Usuario lara@gmail.com no encontrado")
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    main()