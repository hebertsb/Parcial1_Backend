#!/usr/bin/env python
"""
Verificar usuarios con rol Propietario vs Copropietarios
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from authz.models import Usuario, Rol
from seguridad.models import Copropietarios

def verificar_propietarios_vs_copropietarios():
    print("🏠 ANÁLISIS: PROPIETARIOS vs COPROPIETARIOS")
    print("=" * 60)
    
    # 1. Usuarios con rol Propietario
    try:
        rol_propietario = Rol.objects.get(nombre='Propietario')
        propietarios = Usuario.objects.filter(roles=rol_propietario)
        
        print(f"👥 USUARIOS CON ROL 'PROPIETARIO': {propietarios.count()}")
        for prop in propietarios:
            persona_info = "Sin persona"
            if prop.persona:
                persona_info = f"{prop.persona.nombre} {prop.persona.apellido}"
            print(f"   ID: {prop.id}, Email: {prop.email}, Persona: {persona_info}")
            
    except Rol.DoesNotExist:
        print("❌ No existe el rol 'Propietario'")
        
        # Mostrar roles disponibles
        roles = Rol.objects.all()
        print("📋 Roles disponibles:")
        for rol in roles:
            print(f"   - {rol.nombre}")
    
    # 2. Tabla Copropietarios
    copropietarios = Copropietarios.objects.all()
    print(f"\n🏠 TABLA COPROPIETARIOS: {copropietarios.count()}")
    for cop in copropietarios:
        usuario_info = "Sin usuario"
        if cop.usuario_sistema:
            usuario_info = f"Usuario ID: {cop.usuario_sistema.id}"
        print(f"   ID: {cop.id}, Nombre: {cop.nombres} {cop.apellidos}, {usuario_info}")
    
    # 3. Usuarios que pueden usar reconocimiento facial
    print(f"\n🔍 USUARIOS QUE PUEDEN USAR RECONOCIMIENTO FACIAL:")
    
    usuarios_validos = []
    
    # Opción A: Usuarios con rol Propietario y persona asociada
    try:
        rol_propietario = Rol.objects.get(nombre='Propietario')
        propietarios_con_persona = Usuario.objects.filter(
            roles=rol_propietario,
            persona__isnull=False
        )
        
        for prop in propietarios_con_persona:
            usuarios_validos.append({
                'id': prop.id,
                'email': prop.email,
                'nombre': f"{prop.persona.nombre} {prop.persona.apellido}",
                'tipo': 'Propietario (authz)'
            })
    except:
        pass
    
    # Opción B: Usuarios asociados a Copropietarios
    copropietarios_con_usuario = Copropietarios.objects.filter(usuario_sistema__isnull=False)
    for cop in copropietarios_con_usuario:
        if cop.usuario_sistema:  # Verificación de seguridad adicional
            usuarios_validos.append({
                'id': cop.usuario_sistema.id,
                'email': cop.usuario_sistema.email,
                'nombre': f"{cop.nombres} {cop.apellidos}",
                'tipo': 'Copropietario (seguridad)'
            })
    
    if usuarios_validos:
        for usuario in usuarios_validos:
            print(f"   ✅ ID: {usuario['id']}, Email: {usuario['email']}")
            print(f"      Nombre: {usuario['nombre']}, Tipo: {usuario['tipo']}")
    else:
        print("   ❌ NO HAY USUARIOS VÁLIDOS")
        print("   💡 Necesitas crear asociaciones o usuarios con rol Propietario")

def mostrar_solucion():
    print(f"\n🛠️ SOLUCIÓN RECOMENDADA:")
    print("=" * 60)
    
    print("OPCIÓN 1: Usar sistema de Propietarios (authz)")
    print("  - Cambiar endpoint para buscar usuarios con rol 'Propietario'")
    print("  - Verificar que tengan persona asociada")
    print("  - Es el sistema 'oficial' del proyecto")
    print()
    
    print("OPCIÓN 2: Mantener sistema de Copropietarios (seguridad)")
    print("  - Asociar más usuarios a copropietarios existentes")
    print("  - Mantener el endpoint actual")
    print("  - Sistema más específico para seguridad")
    print()
    
    print("RECOMENDACIÓN: 🎯 OPCIÓN 1")
    print("  - Más consistente con el flujo de registro")
    print("  - Los admins aprueban solicitudes → se crean Propietarios")
    print("  - Endpoint debe buscar rol 'Propietario' no tabla Copropietarios")

if __name__ == "__main__":
    verificar_propietarios_vs_copropietarios()
    mostrar_solucion()