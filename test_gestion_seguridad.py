#!/usr/bin/env python
"""
Script de prueba para gestión de usuarios de seguridad
"""

import os
import sys
import django
from django.conf import settings

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from authz.models import Usuario, Persona, Rol
from django.db import transaction

def test_crear_usuario_seguridad():
    """Prueba crear un usuario de seguridad"""
    print("🧪 PRUEBA: Crear usuario de seguridad")
    
    try:
        with transaction.atomic():
            # Datos de prueba
            email_test = "seguridad.test@condominio.com"
            
            # Limpiar datos de prueba si existen
            Usuario.objects.filter(email=email_test).delete()
            Persona.objects.filter(email=email_test).delete()
            
            # Crear usuario de seguridad
            persona = Persona.objects.create(
                nombre="Carlos",
                apellido="Seguridad",
                documento_identidad="SEG001",
                email=email_test,
                telefono="+591 70123456",
                tipo_persona='seguridad',
                activo=True
            )
            
            usuario = Usuario.objects.create_user(
                email=email_test,
                password="seg2024",
                persona=persona,
                estado='ACTIVO'
            )
            
            # Obtener rol de seguridad
            rol_seguridad, _ = Rol.objects.get_or_create(
                nombre='Seguridad',
                defaults={'descripcion': 'Personal de seguridad del condominio'}
            )
            
            usuario.roles.add(rol_seguridad)
            
            print(f"✅ Usuario creado: {usuario.email}")
            print(f"✅ Persona asociada: {persona.nombre_completo}")
            print(f"✅ Documento: {persona.documento_identidad}")
            print(f"✅ Roles: {[rol.nombre for rol in usuario.roles.all()]}")
            print(f"✅ Estado: {usuario.estado}")
            
            return usuario
            
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        return None

def test_verificar_permisos_seguridad():
    """Prueba verificar permisos de usuario de seguridad"""
    print("\n🧪 PRUEBA: Verificar permisos de seguridad")
    
    try:
        # Obtener usuario de seguridad de prueba
        usuario = Usuario.objects.filter(
            email="seguridad.test@condominio.com"
        ).first()
        
        if not usuario:
            print("❌ No se encontró usuario de prueba")
            return False
            
        # Verificar rol
        tiene_rol_seguridad = usuario.roles.filter(nombre='Seguridad').exists()
        print(f"✅ Tiene rol Seguridad: {tiene_rol_seguridad}")
        
        # Verificar estado activo
        esta_activo = usuario.estado == 'ACTIVO'
        print(f"✅ Estado ACTIVO: {esta_activo}")
        
        # Verificar autenticación
        esta_autenticado = usuario.is_authenticated
        print(f"✅ Autenticado: {esta_autenticado}")
        
        return tiene_rol_seguridad and esta_activo and esta_autenticado
        
    except Exception as e:
        print(f"❌ Error verificando permisos: {str(e)}")
        return False

def test_listar_usuarios_seguridad():
    """Prueba listar todos los usuarios de seguridad"""
    print("\n🧪 PRUEBA: Listar usuarios de seguridad")
    
    try:
        usuarios_seguridad = Usuario.objects.filter(
            roles__nombre='Seguridad'
        ).select_related('persona')
        
        print(f"📊 Total usuarios de seguridad: {usuarios_seguridad.count()}")
        
        for usuario in usuarios_seguridad:
            print(f"  👤 {usuario.persona.nombre_completo if usuario.persona else 'Sin persona'}")
            print(f"     📧 {usuario.email}")
            print(f"     📄 {usuario.persona.documento_identidad if usuario.persona else 'Sin documento'}")
            print(f"     📱 {usuario.persona.telefono if usuario.persona else 'Sin teléfono'}")
            print(f"     🔘 Estado: {usuario.estado}")
            print(f"     📅 Creado: {usuario.date_joined}")
            print()
            
        return True
        
    except Exception as e:
        print(f"❌ Error listando usuarios: {str(e)}")
        return False

def test_actualizar_estado_seguridad():
    """Prueba actualizar estado de usuario de seguridad"""
    print("\n🧪 PRUEBA: Actualizar estado de seguridad")
    
    try:
        usuario = Usuario.objects.filter(
            email="seguridad.test@condominio.com"
        ).first()
        
        if not usuario:
            print("❌ No se encontró usuario de prueba")
            return False
            
        estado_original = usuario.estado
        print(f"🔘 Estado original: {estado_original}")
        
        # Cambiar a SUSPENDIDO
        usuario.estado = 'SUSPENDIDO'
        usuario.save()
        
        print(f"🔘 Estado actualizado: {usuario.estado}")
        
        # Volver al estado original
        usuario.estado = estado_original
        usuario.save()
        
        print(f"🔘 Estado restaurado: {usuario.estado}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error actualizando estado: {str(e)}")
        return False

def test_cleanup():
    """Limpiar datos de prueba"""
    print("\n🧹 LIMPIEZA: Eliminando datos de prueba")
    
    try:
        # Eliminar usuario de prueba
        usuario_eliminado = Usuario.objects.filter(
            email="seguridad.test@condominio.com"
        ).delete()
        
        persona_eliminada = Persona.objects.filter(
            email="seguridad.test@condominio.com"
        ).delete()
        
        print(f"✅ Usuarios eliminados: {usuario_eliminado[0] if usuario_eliminado[0] else 0}")
        print(f"✅ Personas eliminadas: {persona_eliminada[0] if persona_eliminada[0] else 0}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error en limpieza: {str(e)}")
        return False

def main():
    """Ejecutar todas las pruebas"""
    print("🔧 INICIANDO PRUEBAS DE GESTIÓN DE SEGURIDAD")
    print("=" * 50)
    
    # Ejecutar pruebas
    pruebas = [
        test_crear_usuario_seguridad,
        test_verificar_permisos_seguridad,
        test_listar_usuarios_seguridad,
        test_actualizar_estado_seguridad,
        test_cleanup
    ]
    
    resultados = []
    for prueba in pruebas:
        resultado = prueba()
        resultados.append(resultado is not False)
    
    # Mostrar resumen
    print("\n" + "=" * 50)
    print("📊 RESUMEN DE PRUEBAS")
    exitosas = sum(resultados)
    total = len(resultados)
    
    print(f"✅ Pruebas exitosas: {exitosas}/{total}")
    
    if exitosas == total:
        print("🎉 ¡Todas las pruebas pasaron correctamente!")
        print("\n💡 PRÓXIMOS PASOS:")
        print("1. Probar endpoints desde el frontend o Postman")
        print("2. Crear usuarios de seguridad reales")
        print("3. Configurar panel de seguridad")
    else:
        print("❌ Algunas pruebas fallaron. Revisar errores arriba.")
    
    return exitosas == total

if __name__ == "__main__":
    main()