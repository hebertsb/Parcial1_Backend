#!/usr/bin/env python
"""
Script para validar y corregir roles de usuarios
Ejecutar con: python manage.py shell < validar_roles_usuarios.py
"""

from authz.models import Usuario, Rol

def validar_y_corregir_roles():
    """Valida que todos los usuarios tengan al menos un rol asignado"""
    print("🔍 VALIDANDO ROLES DE USUARIOS...")
    print("=" * 50)
    
    # Obtener o crear roles base
    roles_base = {}
    roles_nombres = ['Administrador', 'Seguridad', 'Propietario', 'Inquilino']
    
    for nombre in roles_nombres:
        rol, created = Rol.objects.get_or_create(
            nombre=nombre,
            defaults={
                'descripcion': f'Rol de {nombre.lower()} del sistema',
                'activo': True
            }
        )
        roles_base[nombre] = rol
        if created:
            print(f"✅ Rol '{nombre}' creado")
    
    # Revisar todos los usuarios
    usuarios_sin_roles = []
    usuarios_con_roles = []
    
    for usuario in Usuario.objects.all():
        roles_usuario = list(usuario.roles.values_list('nombre', flat=True))
        
        if not roles_usuario:
            usuarios_sin_roles.append(usuario)
            print(f"⚠️  Usuario SIN ROLES: {usuario.email}")
        else:
            usuarios_con_roles.append((usuario, roles_usuario))
            print(f"✅ Usuario CON ROLES: {usuario.email} -> {roles_usuario}")
    
    print("\n" + "=" * 50)
    print(f"📊 RESUMEN:")
    print(f"   • Usuarios con roles: {len(usuarios_con_roles)}")
    print(f"   • Usuarios sin roles: {len(usuarios_sin_roles)}")
    
    # Corregir usuarios sin roles
    if usuarios_sin_roles:
        print(f"\n🔧 CORRIGIENDO {len(usuarios_sin_roles)} USUARIOS SIN ROLES...")
        
        for usuario in usuarios_sin_roles:
            # Determinar rol por defecto
            if usuario.is_superuser or usuario.is_staff:
                rol_defecto = roles_base['Administrador']
                print(f"   👑 {usuario.email} -> Administrador (superuser/staff)")
            else:
                rol_defecto = roles_base['Inquilino']
                print(f"   🏘️  {usuario.email} -> Inquilino (usuario regular)")
            
            usuario.roles.add(rol_defecto)
        
        print("✅ CORRECCIÓN COMPLETADA")
    else:
        print("\n✅ TODOS LOS USUARIOS TIENEN ROLES ASIGNADOS")

    print("\n" + "=" * 50)
    print("🎯 ESTADO FINAL:")
    
    for usuario in Usuario.objects.all():
        roles = [r.nombre for r in usuario.roles.all()]
        tipo = "👑 ADMIN" if (usuario.is_superuser or usuario.is_staff) else "👤 USER"
        print(f"   {tipo} {usuario.email}: {roles}")

if __name__ == "__main__":
    validar_y_corregir_roles()