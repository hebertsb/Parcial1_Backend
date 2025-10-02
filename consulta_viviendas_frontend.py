#!/usr/bin/env python
"""
🏠 CONSULTA DE VIVIENDAS DISPONIBLES PARA PRUEBAS FRONTEND
Sistema de Reconocimiento Facial - Condominio

Este script muestra:
✅ Viviendas disponibles para registro
✅ Viviendas ocupadas con detalles
✅ Tipos de vivienda disponibles
✅ Estadísticas completas para frontend

Ejecutar: python consulta_viviendas_frontend.py
"""

import os
import sys
import django
from datetime import datetime

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

# Imports después de configurar Django
from django.contrib.auth import get_user_model
from authz.models import Usuario, Persona, Rol
from core.models.propiedades_residentes import Vivienda, Propiedad
from seguridad.models import Copropietarios

User = get_user_model()

def mostrar_estadisticas_generales():
    """Mostrar estadísticas generales"""
    print("="*80)
    print("📊 ESTADÍSTICAS GENERALES DEL SISTEMA")
    print("="*80)
    
    total_viviendas = Vivienda.objects.count()
    viviendas_ocupadas = Propiedad.objects.filter(activo=True).values_list('vivienda_id', flat=True).distinct().count()
    viviendas_disponibles = total_viviendas - viviendas_ocupadas
    
    print(f"🏠 Total de viviendas: {total_viviendas}")
    print(f"🔴 Viviendas ocupadas: {viviendas_ocupadas}")
    print(f"🟢 Viviendas disponibles: {viviendas_disponibles}")
    print(f"📊 Porcentaje ocupación: {(viviendas_ocupadas/total_viviendas*100):.1f}%")
    print()

def mostrar_viviendas_por_tipo():
    """Mostrar viviendas agrupadas por tipo"""
    print("="*80)
    print("🏢 VIVIENDAS POR TIPO")
    print("="*80)
    
    tipos_vivienda = Vivienda.objects.values_list('tipo_vivienda', flat=True).distinct()
    
    for tipo in tipos_vivienda:
        total_tipo = Vivienda.objects.filter(tipo_vivienda=tipo).count()
        ocupadas_tipo = Vivienda.objects.filter(
            tipo_vivienda=tipo,
            pk__in=Propiedad.objects.filter(activo=True).values_list('vivienda_id', flat=True)
        ).count()
        disponibles_tipo = total_tipo - ocupadas_tipo
        
        tipo_display = {'casa': 'Casas', 'departamento': 'Departamentos', 'local': 'Locales'}.get(tipo, tipo.title())
        
        print(f"🏠 {tipo_display}:")
        print(f"   📊 Total: {total_tipo}")
        print(f"   🔴 Ocupadas: {ocupadas_tipo}")
        print(f"   🟢 Disponibles: {disponibles_tipo}")
        print()

def mostrar_viviendas_disponibles_detalle():
    """Mostrar detalles de viviendas disponibles"""
    print("="*80)
    print("🟢 VIVIENDAS DISPONIBLES PARA REGISTRO (FRONTEND)")
    print("="*80)
    
    viviendas_ocupadas_ids = Propiedad.objects.filter(activo=True).values_list('vivienda_id', flat=True)
    viviendas_disponibles = Vivienda.objects.exclude(pk__in=viviendas_ocupadas_ids).order_by('numero_casa')
    
    if not viviendas_disponibles.exists():
        print("❌ No hay viviendas disponibles para registro")
        return
    
    print(f"📋 Total disponibles: {viviendas_disponibles.count()}")
    print("-" * 80)
    
    for i, vivienda in enumerate(viviendas_disponibles, 1):
        tipo_display = {'casa': 'Casa', 'departamento': 'Departamento', 'local': 'Local'}.get(vivienda.tipo_vivienda, vivienda.tipo_vivienda)
        
        print(f"{i:2d}. 🏠 {vivienda.numero_casa}")
        print(f"    🏢 Tipo: {tipo_display}")
        print(f"    📐 Área: {vivienda.metros_cuadrados} m²")
        if vivienda.bloque:
            print(f"    🏗️ Bloque: {vivienda.bloque}")
        print(f"    💰 Tarifa base: ${vivienda.tarifa_base_expensas}")
        print(f"    ⚡ Estado: {vivienda.estado}")
        print(f"    📅 Creada: {vivienda.fecha_creacion.strftime('%d/%m/%Y')}")
        print()

def mostrar_viviendas_ocupadas_detalle():
    """Mostrar detalles de viviendas ocupadas"""
    print("="*80)
    print("🔴 VIVIENDAS OCUPADAS (REFERENCIAS)")
    print("="*80)
    
    viviendas_ocupadas_ids = Propiedad.objects.filter(activo=True).values_list('vivienda_id', flat=True).distinct()
    viviendas_ocupadas = Vivienda.objects.filter(pk__in=viviendas_ocupadas_ids).order_by('numero_casa')
    
    print(f"📋 Total ocupadas: {viviendas_ocupadas.count()}")
    print("-" * 80)
    
    for i, vivienda in enumerate(viviendas_ocupadas, 1):
        tipo_display = {'casa': 'Casa', 'departamento': 'Departamento', 'local': 'Local'}.get(vivienda.tipo_vivienda, vivienda.tipo_vivienda)
        
        print(f"{i:2d}. 🏠 {vivienda.numero_casa}")
        print(f"    🏢 Tipo: {tipo_display}")
        print(f"    📐 Área: {vivienda.metros_cuadrados} m²")
        if vivienda.bloque:
            print(f"    🏗️ Bloque: {vivienda.bloque}")
        
        # Mostrar quien vive ahí
        propiedades = Propiedad.objects.filter(vivienda=vivienda, activo=True)
        for propiedad in propiedades:
            tipo_residente = "👨‍💼 Propietario" if propiedad.tipo_tenencia == 'propietario' else "🏠 Inquilino"
            print(f"    {tipo_residente}: {propiedad.persona.nombre} {propiedad.persona.apellido}")
        print()

def generar_json_frontend():
    """Generar datos en formato JSON para frontend"""
    print("="*80)
    print("📱 DATOS PARA FRONTEND (JSON)")
    print("="*80)
    
    viviendas_ocupadas_ids = Propiedad.objects.filter(activo=True).values_list('vivienda_id', flat=True)
    viviendas_disponibles = Vivienda.objects.exclude(pk__in=viviendas_ocupadas_ids)
    
    print("// Viviendas disponibles para selector del frontend")
    print("const viviendasDisponibles = [")
    
    for vivienda in viviendas_disponibles:
        tipo_display = {'casa': 'Casa', 'departamento': 'Departamento', 'local': 'Local'}.get(vivienda.tipo_vivienda, vivienda.tipo_vivienda)
        
        print(f"  {{")
        print(f"    id: {vivienda.pk},")
        print(f"    numero_casa: '{vivienda.numero_casa}',")
        print(f"    tipo: '{tipo_display}',")
        print(f"    area: {vivienda.metros_cuadrados},")
        bloque_valor = 'null' if not vivienda.bloque else f"'{vivienda.bloque}'"
        print(f"    bloque: {bloque_valor},")
        print(f"    tarifa_base: {vivienda.tarifa_base_expensas}")
        print(f"  }},")
    
        print("];")
        print()
    
        print("// Tipos de vivienda disponibles")
        tipos_disponibles = viviendas_disponibles.values_list('tipo_vivienda', flat=True).distinct()
        print("const tiposViviendaDisponibles = [")
        for tipo in tipos_disponibles:
             tipo_display = {'casa': 'Casa', 'departamento': 'Departamento', 'local': 'Local'}.get(tipo, tipo)
        print(f"  {{ value: '{tipo}', label: '{tipo_display}' }},")
    print("];")
    print()

def mostrar_endpoints_frontend():
    """Mostrar endpoints útiles para frontend"""
    print("="*80)
    print("🌐 ENDPOINTS ÚTILES PARA FRONTEND")
    print("="*80)
    
    print("📡 CONSULTAS DE VIVIENDAS:")
    print("  GET http://127.0.0.1:8000/api/viviendas/ - Listar todas las viviendas")
    print("  GET http://127.0.0.1:8000/api/viviendas/disponibles/ - Solo disponibles")
    print("  GET http://127.0.0.1:8000/api/viviendas/{id}/ - Detalle de vivienda")
    print()
    
    print("👤 REGISTRO DE USUARIOS:")
    print("  POST http://127.0.0.1:8000/api/authz/registro/propietario/ - Registro propietario")
    print("  GET http://127.0.0.1:8000/api/authz/solicitudes/ - Consultar solicitudes")
    print("  GET http://127.0.0.1:8000/api/authz/panel/ - Panel propietario")
    print()
    
    print("🔐 AUTENTICACIÓN:")
    print("  POST http://127.0.0.1:8000/api/auth/login/ - Login usuario")
    print("  POST http://127.0.0.1:8000/api/auth/refresh/ - Refresh token")
    print()
    
    print("📚 DOCUMENTACIÓN:")
    print("  GET http://127.0.0.1:8000/api/docs/ - Swagger UI completo")
    print()

def mostrar_credenciales_prueba():
    """Mostrar credenciales para pruebas"""
    print("="*80)
    print("🔑 CREDENCIALES PARA PRUEBAS FRONTEND")
    print("="*80)
    
    print("👔 ADMINISTRADOR (para aprobar solicitudes):")
    print("  📧 Email: admin@condominio.com")
    print("  🔐 Password: temporal123")
    print()
    
    print("👨‍💼 PROPIETARIOS EXISTENTES (para comparar):")
    propietarios = Usuario.objects.filter(roles__nombre='Propietario')[:3]
    for prop in propietarios:
        print(f"  📧 {prop.email} / temporal123")
    print()
    
    print("📱 DATOS PARA FORMULARIO DE REGISTRO:")
    print("  🆔 Documento: 12345678 (disponible)")
    print("  📧 Email: nuevo_usuario@test.com")
    print("  🔐 Password: temporal123")
    print("  🏠 Viviendas disponibles: Ver lista arriba")
    print()

def main():
    """Función principal"""
    print("\n🚀 CONSULTA DE VIVIENDAS PARA FRONTEND")
    print(f"📅 Fecha: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}")
    
    try:
        mostrar_estadisticas_generales()
        mostrar_viviendas_por_tipo()
        mostrar_viviendas_disponibles_detalle()
        mostrar_viviendas_ocupadas_detalle()
        generar_json_frontend()
        mostrar_endpoints_frontend()
        mostrar_credenciales_prueba()
        
        print("="*80)
        print("✅ CONSULTA COMPLETADA")
        print("="*80)
        print("💡 Usa las viviendas disponibles para probar registro de nuevos usuarios")
        print("🌐 Sistema funcionando en: http://127.0.0.1:8000/")
        print("📚 Documentación: http://127.0.0.1:8000/api/docs/")
        print("="*80)
        
    except Exception as e:
        print(f"❌ Error en consulta: {e}")
        raise

if __name__ == "__main__":
    main()