#!/usr/bin/env python
"""
Script para sincronizar las unidades residenciales entre solicitudes y copropietarios
"""
import os
import sys
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from authz.models import Usuario, SolicitudRegistroPropietario
from seguridad.models import Copropietarios

def sincronizar_unidades_residenciales():
    """Sincronizar unidades residenciales entre solicitudes y copropietarios"""
    print("🔄 SINCRONIZANDO UNIDADES RESIDENCIALES")
    print("=" * 60)
    
    propietarios = Usuario.objects.filter(roles__nombre='Propietario')
    actualizados = 0
    
    for propietario in propietarios:
        print(f"\n👤 {propietario.email}:")
        
        # Buscar solicitud aprobada
        solicitud = SolicitudRegistroPropietario.objects.filter(
            usuario_creado=propietario,
            estado='APROBADA'
        ).first()
        
        # Buscar copropietario
        copropietario = getattr(propietario, 'copropietario_perfil', None)
        
        if solicitud and copropietario:
            # Determinar número correcto (preferir vivienda validada)
            numero_correcto = solicitud.numero_casa
            if solicitud.vivienda_validada:
                numero_correcto = solicitud.vivienda_validada.numero_casa
            
            print(f"   📋 Solicitud: {solicitud.numero_casa}")
            if solicitud.vivienda_validada:
                print(f"   🏠 Vivienda validada: {solicitud.vivienda_validada.numero_casa}")
            print(f"   👥 Copropietario actual: {copropietario.unidad_residencial}")
            
            if copropietario.unidad_residencial != numero_correcto:
                print(f"   🔄 Actualizando: {copropietario.unidad_residencial} → {numero_correcto}")
                copropietario.unidad_residencial = numero_correcto
                copropietario.save()
                actualizados += 1
                print(f"   ✅ Actualizado!")
            else:
                print(f"   ✅ Ya está sincronizado")
        
        elif solicitud and not copropietario:
            print(f"   ❌ Tiene solicitud pero no copropietario")
        elif copropietario and not solicitud:
            print(f"   ❌ Tiene copropietario pero no solicitud")
        else:
            print(f"   ❌ Sin solicitud ni copropietario")
    
    print(f"\n📊 RESUMEN:")
    print(f"   👥 Total propietarios: {propietarios.count()}")
    print(f"   🔄 Actualizados: {actualizados}")
    print(f"   ✅ Sincronización completada!")

def verificar_estado_final():
    """Verificar estado final después de la sincronización"""
    print("\n🔍 VERIFICACIÓN FINAL")
    print("=" * 60)
    
    propietarios = Usuario.objects.filter(roles__nombre='Propietario')
    
    with_both = 0
    with_solicitud_only = 0
    with_copropietario_only = 0
    with_neither = 0
    synchronized = 0
    
    for propietario in propietarios:
        solicitud = SolicitudRegistroPropietario.objects.filter(
            usuario_creado=propietario,
            estado='APROBADA'
        ).first()
        
        copropietario = getattr(propietario, 'copropietario_perfil', None)
        
        if solicitud and copropietario:
            with_both += 1
            numero_solicitud = solicitud.vivienda_validada.numero_casa if solicitud.vivienda_validada else solicitud.numero_casa
            if copropietario.unidad_residencial == numero_solicitud:
                synchronized += 1
        elif solicitud:
            with_solicitud_only += 1
        elif copropietario:
            with_copropietario_only += 1
        else:
            with_neither += 1
    
    print(f"📊 ESTADÍSTICAS:")
    print(f"   ✅ Con solicitud Y copropietario: {with_both}")
    print(f"   📋 Solo con solicitud: {with_solicitud_only}")
    print(f"   👥 Solo con copropietario: {with_copropietario_only}")
    print(f"   ❌ Sin ninguno: {with_neither}")
    print(f"   🎯 Sincronizados correctamente: {synchronized}/{with_both}")

def main():
    """Ejecutar sincronización"""
    sincronizar_unidades_residenciales()
    verificar_estado_final()

if __name__ == "__main__":
    main()