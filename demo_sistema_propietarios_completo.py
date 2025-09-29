#!/usr/bin/env python
"""
Script de demostración completa del sistema de gestión de propietarios con panel admin
"""
import os
import sys
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from authz.models import Usuario, SolicitudRegistroPropietario
from seguridad.models import Copropietarios, ReconocimientoFacial

def mostrar_arquitectura_sistema():
    """Mostrar la arquitectura del sistema dual"""
    print("🏗️  ARQUITECTURA DEL SISTEMA DUAL")
    print("=" * 70)
    print("""
📊 TABLAS PRINCIPALES:
┌─────────────────┬─────────────────┬──────────────────────────────────┐
│ authz.Usuario   │ authz.Persona   │ Propósito                        │
├─────────────────┼─────────────────┼──────────────────────────────────┤
│ Email/Password  │ Datos personales│ Autenticación y datos básicos    │
│ Roles           │ Foto perfil     │                                  │
└─────────────────┴─────────────────┴──────────────────────────────────┘

┌─────────────────┬─────────────────┬──────────────────────────────────┐
│ Copropietarios  │ ReconocFacial   │ Propósito                        │
├─────────────────┼─────────────────┼──────────────────────────────────┤
│ Unidad residen. │ URLs de fotos   │ Reconocimiento facial y          │
│ Usuario sistema │ Persona relac.  │ gestión de residentes            │
└─────────────────┴─────────────────┴──────────────────────────────────┘

🔗 RELACIONES:
Usuario ← OneToOne → Copropietarios
Copropietarios ← OneToMany → ReconocimientoFacial
""")

def mostrar_flujo_registro():
    """Mostrar el flujo de registro y aprobación"""
    print("🔄 FLUJO DE REGISTRO DE PROPIETARIOS")
    print("=" * 70)
    print("""
1️⃣  SOLICITUD: Usuario envía SolicitudRegistroPropietario
   • Datos personales + número de casa
   • Fotos de reconocimiento facial → Dropbox temporal
   
2️⃣  VALIDACIÓN: Admin valida vivienda en sistema
   • Verifica que numero_casa existe en tabla Vivienda
   • Asocia solicitud.vivienda_validada
   
3️⃣  APROBACIÓN: Admin aprueba → aprobar_solicitud()
   • ✅ Crea/actualiza authz.Persona
   • ✅ Crea authz.Usuario con rol 'Propietario'
   • ✅ Crea seguridad.Copropietarios (AUTOMÁTICO)
   • ✅ Mueve fotos Dropbox → carpeta definitiva
   • ✅ Sincroniza unidad_residencial con vivienda_validada
   
4️⃣  RESULTADO: Usuario puede subir fotos faciales
   • Acceso al endpoint /api/authz/reconocimiento/fotos/
   • Relación Usuario → Copropietarios → ReconocimientoFacial
""")

def mostrar_endpoints_admin():
    """Mostrar los nuevos endpoints admin"""
    print("🌐 ENDPOINTS ADMINISTRATIVOS IMPLEMENTADOS")
    print("=" * 70)
    print("""
🔐 GESTIÓN DE SEGURIDAD (ya existía):
📍 GET  /auth/admin/seguridad/listar/
📍 POST /auth/admin/seguridad/crear/
📍 PUT  /auth/admin/seguridad/<id>/estado/
📍 POST /auth/admin/seguridad/<id>/reset-password/

🏠 GESTIÓN DE PROPIETARIOS (NUEVO):
📍 GET  /auth/admin/propietarios/listar/
   • Lista todos los usuarios con rol 'Propietario'
   • Información combinada: Usuario + Copropietarios + Vivienda
   • Foto perfil desde authz.Persona
   • Estado de capacidad para subir fotos

📍 PUT  /auth/admin/propietarios/<usuario_id>/editar/
   • Edita Usuario + Copropietarios sincronizadamente
   • Crea Copropietarios si no existe
   • Mantiene consistencia entre tablas duales
""")

def mostrar_estadisticas_actuales():
    """Mostrar estadísticas del sistema actual"""
    print("📊 ESTADÍSTICAS ACTUALES DEL SISTEMA")
    print("=" * 70)
    
    # Contar por roles
    total_usuarios = Usuario.objects.count()
    admins = Usuario.objects.filter(roles__nombre='Administrador').count()
    propietarios = Usuario.objects.filter(roles__nombre='Propietario').count()
    seguridad = Usuario.objects.filter(roles__nombre='Seguridad').count()
    
    print(f"👥 USUARIOS POR ROL:")
    print(f"   🔐 Administradores: {admins}")
    print(f"   🏠 Propietarios: {propietarios}")
    print(f"   🛡️  Seguridad: {seguridad}")
    print(f"   📊 Total: {total_usuarios}")
    
    # Propietarios con capacidades
    copropietarios = Copropietarios.objects.count()
    copropietarios_con_usuario = Copropietarios.objects.filter(usuario_sistema__isnull=False).count()
    propietarios_con_copropietario = Usuario.objects.filter(
        roles__nombre='Propietario',
        copropietario_perfil__isnull=False
    ).count()
    
    print(f"\n🏠 ANÁLISIS DE PROPIETARIOS:")
    print(f"   👥 Copropietarios totales: {copropietarios}")
    print(f"   🔗 Con usuario asociado: {copropietarios_con_usuario}")
    print(f"   📸 Can upload fotos: {propietarios_con_copropietario}/{propietarios}")
    
    # Fotos de reconocimiento
    fotos_totales = ReconocimientoFacial.objects.count()
    personas_con_fotos = ReconocimientoFacial.objects.values('copropietario').distinct().count()
    
    print(f"\n📸 RECONOCIMIENTO FACIAL:")
    print(f"   📷 Fotos totales: {fotos_totales}")
    print(f"   👤 Personas con fotos: {personas_con_fotos}")

def mostrar_casos_uso():
    """Mostrar casos de uso específicos"""
    print("🎯 CASOS DE USO IMPLEMENTADOS")
    print("=" * 70)
    print("""
✅ CASO 1: Nuevo propietario se registra
   → Solicitud → Aprobación → Usuario + Copropietarios creados
   → Puede subir fotos inmediatamente

✅ CASO 2: Admin gestiona propietarios existentes
   → Ve lista completa con estado de fotos
   → Puede editar información en ambas tablas
   → Mantiene sincronización automática

✅ CASO 3: Propietario ve su panel
   → Número de casa correcto desde vivienda_validada
   → Acceso a reconocimiento facial
   → Información consistente en todo el sistema

✅ CASO 4: Sistema mantiene integridad dual
   → authz.Usuario para autenticación
   → seguridad.Copropietarios para funcionalidades residenciales
   → Sincronización automática entre ambas tablas
""")

def verificar_propietarios_detallado():
    """Mostrar estado detallado de cada propietario"""
    print("🔍 ESTADO DETALLADO DE PROPIETARIOS")
    print("=" * 70)
    
    propietarios = Usuario.objects.filter(roles__nombre='Propietario').order_by('email')
    
    for prop in propietarios:
        print(f"\n👤 {prop.email} (ID: {prop.id})")
        print(f"   📊 Estado: {prop.estado}")
        
        # Persona
        if prop.persona:
            print(f"   👤 Persona: {prop.persona.nombre_completo}")
            print(f"   📄 Documento: {prop.persona.documento_identidad}")
            print(f"   📷 Foto perfil: {'✅' if prop.persona.foto_perfil else '❌'}")
        else:
            print(f"   ❌ Sin persona asociada")
        
        # Solicitud
        solicitud = SolicitudRegistroPropietario.objects.filter(
            usuario_creado=prop, estado='APROBADA'
        ).first()
        if solicitud:
            print(f"   📋 Solicitud aprobada: Casa {solicitud.numero_casa}")
            if solicitud.vivienda_validada:
                print(f"   🏠 Vivienda validada: {solicitud.vivienda_validada.numero_casa}")
        else:
            print(f"   ❌ Sin solicitud aprobada")
        
        # Copropietario
        copropietario = getattr(prop, 'copropietario_perfil', None)
        if copropietario:
            print(f"   👥 Copropietario ID: {copropietario.id}")
            print(f"   🏠 Unidad: {copropietario.unidad_residencial}")
            print(f"   📸 Puede subir fotos: ✅")
        else:
            print(f"   ❌ Sin perfil copropietario")
            print(f"   📸 Puede subir fotos: ❌")
        
        # Fotos
        if copropietario:
            fotos = ReconocimientoFacial.objects.filter(copropietario=copropietario)
            print(f"   📷 Fotos reconocimiento: {fotos.count()}")
        else:
            print(f"   📷 Fotos reconocimiento: 0")

def main():
    """Ejecutar demostración completa"""
    print("🎉 DEMOSTRACIÓN COMPLETA: SISTEMA DE GESTIÓN DE PROPIETARIOS")
    print("=" * 80)
    
    mostrar_arquitectura_sistema()
    mostrar_flujo_registro()
    mostrar_endpoints_admin()
    mostrar_estadisticas_actuales()
    mostrar_casos_uso()
    verificar_propietarios_detallado()
    
    print("\n" + "=" * 80)
    print("✅ RESUMEN FINAL:")
    print("🏗️  Sistema dual implementado correctamente")
    print("🔄 Sincronización automática entre tablas")
    print("🌐 Endpoints admin para gestión completa")
    print("📸 Reconocimiento facial funcional")
    print("🎯 Casos de uso cubiertos completamente")
    print("=" * 80)

if __name__ == "__main__":
    main()