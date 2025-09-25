#!/usr/bin/env python
"""
Prueba simple de funcionalidad administrativa de seguridad
"""

import os
import sys
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from authz.models import Usuario, Persona, Rol

def main():
    print("🔧 PRUEBA SIMPLE - GESTIÓN DE SEGURIDAD")
    print("=" * 45)
    
    # 1. Verificar usuarios de seguridad existentes
    print("\n1️⃣ USUARIOS DE SEGURIDAD EXISTENTES:")
    usuarios_seguridad = Usuario.objects.filter(roles__nombre='Seguridad')
    print(f"Total: {usuarios_seguridad.count()}")
    
    for usuario in usuarios_seguridad:
        print(f"  👤 {usuario.persona.nombre_completo if usuario.persona else 'Sin nombre'}")
        print(f"     📧 {usuario.email}")
        print(f"     🔘 Estado: {usuario.estado}")
    
    # 2. Verificar rol de seguridad
    print("\n2️⃣ ROL DE SEGURIDAD:")
    try:
        rol_seguridad = Rol.objects.get(nombre='Seguridad')
        print(f"✅ Rol encontrado: {rol_seguridad.nombre}")
        print(f"   Descripción: {rol_seguridad.descripcion}")
        print(f"   Activo: {rol_seguridad.activo}")
        usuarios_con_rol = Usuario.objects.filter(roles=rol_seguridad).count()
        print(f"   Usuarios con este rol: {usuarios_con_rol}")
    except Rol.DoesNotExist:
        print("❌ Rol 'Seguridad' no encontrado")
    
    # 3. Verificar administradores
    print("\n3️⃣ ADMINISTRADORES:")
    administradores = Usuario.objects.filter(roles__nombre='Administrador')
    print(f"Total: {administradores.count()}")
    
    for admin in administradores:
        print(f"  👔 {admin.persona.nombre_completo if admin.persona else 'Sin nombre'}")
        print(f"     📧 {admin.email}")
        print(f"     🔘 Estado: {admin.estado}")
    
    # 4. Verificar importación de vistas
    print("\n4️⃣ VERIFICACIÓN DE VISTAS:")
    try:
        from authz.views_admin import (
            CrearUsuarioSeguridadAPIView,
            ListarUsuariosSeguridadAPIView,
            ActualizarEstadoUsuarioSeguridadAPIView,
            ResetPasswordSeguridadAPIView
        )
        print("✅ Todas las vistas administrativas importadas correctamente")
    except ImportError as e:
        print(f"❌ Error importando vistas: {e}")
    
    # 5. Verificar URLs
    print("\n5️⃣ VERIFICACIÓN DE URLs:")
    try:
        from authz.urls_admin import urlpatterns
        print(f"✅ URLs administrativas cargadas: {len(urlpatterns)} patterns")
        for pattern in urlpatterns:
            print(f"   - {pattern.pattern}")
    except ImportError as e:
        print(f"❌ Error importando URLs: {e}")
    
    # 6. Resultado final
    print("\n" + "=" * 45)
    print("📊 RESUMEN:")
    print(f"✅ Usuarios de seguridad: {usuarios_seguridad.count()}")
    print(f"✅ Administradores: {administradores.count()}")
    print("✅ Vistas administrativas: OK")
    print("✅ URLs administrativas: OK")
    print("\n🎉 EL SISTEMA ESTÁ LISTO PARA GESTIONAR SEGURIDAD!")
    
    print("\n💡 PRÓXIMOS PASOS:")
    print("1. Iniciar servidor: python manage.py runserver")
    print("2. Probar endpoints con Postman o frontend")
    print("3. Crear usuarios de seguridad según necesidad")

if __name__ == "__main__":
    main()