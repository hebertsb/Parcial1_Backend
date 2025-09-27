#!/usr/bin/env python3
"""
Script para probar DIRECTAMENTE el UsuarioUpdateSerializer
"""

import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from authz.models import Usuario, Rol
from authz.serializers import UsuarioUpdateSerializer

def test_serializer_directo():
    print("🧪 PRUEBA DIRECTA DEL SERIALIZER")
    print("=" * 40)
    
    # Obtener usuario de prueba
    try:
        usuario = Usuario.objects.get(email="usuario_prueba@test.com")
        print(f"✅ Usuario encontrado: {usuario.email}")
        print(f"   Roles actuales: {[r.nombre for r in usuario.roles.all()]}")
    except Usuario.DoesNotExist:
        print("❌ Usuario de prueba no encontrado")
        return
    
    # Obtener rol propietario
    try:
        propietario_rol = Rol.objects.get(nombre="Propietario")
        print(f"✅ Rol Propietario encontrado: ID {propietario_rol.id}")
    except Rol.DoesNotExist:
        print("❌ Rol Propietario no encontrado")
        return
    
    # Crear instancia del serializer DIRECTAMENTE
    print(f"\n🔧 Creando UsuarioUpdateSerializer...")
    try:
        serializer = UsuarioUpdateSerializer(instance=usuario)
        print(f"✅ Serializer creado exitosamente")
        print(f"   Campos disponibles: {list(serializer.fields.keys())}")
        
        # Verificar campo roles
        roles_field = serializer.fields.get('roles')
        print(f"   Campo roles: {roles_field}")
        print(f"   Tipo de campo roles: {type(roles_field)}")
        
    except Exception as e:
        print(f"❌ Error creando serializer: {e}")
        import traceback
        traceback.print_exc()
        return
    
    # Probar actualización DIRECTA
    print(f"\n🔄 Probando actualización directa...")
    data = {'roles': [propietario_rol.id]}
    print(f"   Datos: {data}")
    
    try:
        serializer = UsuarioUpdateSerializer(instance=usuario, data=data, partial=True)
        print(f"✅ Serializer con datos creado")
        
        if serializer.is_valid():
            print(f"✅ Datos válidos")
            print(f"   Validated data: {serializer.validated_data}")
            
            # Guardar
            updated_usuario = serializer.save()
            print(f"✅ Usuario actualizado")
            
            # Verificar resultado
            updated_usuario.refresh_from_db()
            roles_finales = [r.nombre for r in updated_usuario.roles.all()]
            print(f"   Roles finales: {roles_finales}")
            
            if "Propietario" in roles_finales:
                print("🎉 ¡ÉXITO! El serializer funciona correctamente")
            else:
                print("❌ FALLO: Los roles no se actualizaron")
                
        else:
            print(f"❌ Datos inválidos: {serializer.errors}")
            
    except Exception as e:
        print(f"❌ Error en actualización: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_serializer_directo()