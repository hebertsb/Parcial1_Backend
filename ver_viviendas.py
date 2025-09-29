#!/usr/bin/env python
"""
Script para verificar el estado de las viviendas
"""

import os
import sys
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from core.models import Vivienda, Propiedad
from seguridad.models import Copropietarios
from authz.models import SolicitudRegistroPropietario

def ver_estado_viviendas():
    print('🏠 ESTADO DE VIVIENDAS EN EL CONDOMINIO')
    print('=' * 50)
    
    # Obtener todas las viviendas
    viviendas = Vivienda.objects.all().order_by('tipo_vivienda', 'bloque', 'numero_casa')
    
    # Contar totales usando el modelo Propiedad
    total_viviendas = viviendas.count()
    viviendas_ocupadas = Vivienda.objects.filter(propiedad__activo=True).distinct().count()
    viviendas_disponibles = total_viviendas - viviendas_ocupadas
    
    print(f'📊 RESUMEN GENERAL:')
    print(f'   Total Viviendas: {total_viviendas}')
    print(f'   🔴 Ocupadas: {viviendas_ocupadas}')
    print(f'   🟢 Disponibles: {viviendas_disponibles}')
    print()
    
    # Mostrar solicitudes pendientes
    solicitudes_pendientes = SolicitudRegistroPropietario.objects.filter(estado='PENDIENTE').count()
    print(f'📝 Solicitudes PENDIENTES: {solicitudes_pendientes}')
    print()
    
    # Agrupar por tipo
    tipos = {}
    for vivienda in viviendas:
        tipo = vivienda.tipo_vivienda
        if tipo not in tipos:
            tipos[tipo] = {'total': 0, 'ocupadas': 0, 'disponibles': 0, 'lista_disponibles': [], 'lista_ocupadas': []}
        
        tipos[tipo]['total'] += 1
        
        # Verificar si está ocupada (tiene propiedad activa)
        tiene_propietario = vivienda.propiedad_set.filter(activo=True).exists()
        
        if tiene_propietario:
            tipos[tipo]['ocupadas'] += 1
            tipos[tipo]['lista_ocupadas'].append(vivienda)
        else:
            tipos[tipo]['disponibles'] += 1
            tipos[tipo]['lista_disponibles'].append(vivienda)
    
    # Mostrar por tipo
    for tipo, datos in tipos.items():
        print(f'🏗️  {tipo.upper()}:')
        print(f'   Total: {datos["total"]} | Ocupadas: {datos["ocupadas"]} | Disponibles: {datos["disponibles"]}')
        
        print('   🟢 DISPONIBLES:')
        if datos['lista_disponibles']:
            for v in datos['lista_disponibles']:
                bloque_info = f' - Bloque {v.bloque}' if v.bloque else ''
                print(f'      • {v.numero_casa}{bloque_info} ({v.metros_cuadrados}m²)')
        else:
            print('      Ninguna disponible')
        
        print('   🔴 OCUPADAS:')
        if datos['lista_ocupadas']:
            for v in datos['lista_ocupadas']:
                bloque_info = f' - Bloque {v.bloque}' if v.bloque else ''
                # Buscar el propietario activo
                propiedad_activa = v.propiedad_set.filter(activo=True).first()
                propietario_info = f' ({propiedad_activa.persona.nombre} {propiedad_activa.persona.apellido})' if propiedad_activa else ''
                print(f'      • {v.numero_casa}{bloque_info} ({v.metros_cuadrados}m²){propietario_info}')
        else:
            print('      Ninguna ocupada')
        
        print()

def ver_resumen_simple():
    """Versión simple solo con números"""
    viviendas = Vivienda.objects.all()
    total = viviendas.count()
    ocupadas = Vivienda.objects.filter(propiedad__activo=True).distinct().count()
    disponibles = total - ocupadas
    
    print(f'📊 RESUMEN VIVIENDAS:')
    print(f'   Total: {total}')
    print(f'   🔴 Ocupadas: {ocupadas}') 
    print(f'   🟢 Disponibles: {disponibles}')
    
    # Solicitudes pendientes
    solicitudes = SolicitudRegistroPropietario.objects.filter(estado='PENDIENTE').count()
    print(f'   📝 Solicitudes PENDIENTES: {solicitudes}')
    
    # Por tipo
    tipos_count = {}
    for v in viviendas:
        tipo = v.tipo_vivienda
        if tipo not in tipos_count:
            tipos_count[tipo] = {'total': 0, 'ocupadas': 0}
        tipos_count[tipo]['total'] += 1
        if v.propiedad_set.filter(activo=True).exists():
            tipos_count[tipo]['ocupadas'] += 1
    
    print('\n🏗️  POR TIPO:')
    for tipo, counts in tipos_count.items():
        disponibles_tipo = counts['total'] - counts['ocupadas']
        print(f'   {tipo}: {counts["total"]} total | {counts["ocupadas"]} ocupadas | {disponibles_tipo} disponibles')

if __name__ == '__main__':
    if len(sys.argv) > 1 and sys.argv[1] == '--simple':
        ver_resumen_simple()
    else:
        ver_estado_viviendas()