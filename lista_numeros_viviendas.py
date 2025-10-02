#!/usr/bin/env python
"""
📋 LISTA DE NÚMEROS DE VIVIENDAS PARA PRUEBAS
Sistema de Reconocimiento Facial - Condominio

Este script genera la lista completa de números de viviendas disponibles
para usar en formularios de registro del frontend.

Ejecutar: python lista_numeros_viviendas.py
"""

import os
import sys
import django
from datetime import datetime

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

# Imports después de configurar Django
from core.models.propiedades_residentes import Vivienda, Propiedad

def generar_lista_viviendas():
    """Generar lista completa de viviendas con sus números"""
    print("🏠 LISTA DE NÚMEROS DE VIVIENDAS PARA PRUEBAS FRONTEND")
    print("="*80)
    print(f"📅 Generado: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}")
    print()
    
    # Obtener todas las viviendas
    todas_viviendas = Vivienda.objects.all().order_by('numero_casa')
    viviendas_ocupadas_ids = Propiedad.objects.filter(activo=True).values_list('vivienda_id', flat=True)
    
    print(f"📊 RESUMEN GENERAL:")
    print(f"   🏠 Total viviendas: {todas_viviendas.count()}")
    print(f"   🔴 Ocupadas: {len(viviendas_ocupadas_ids)}")
    print(f"   🟢 Disponibles: {todas_viviendas.count() - len(viviendas_ocupadas_ids)}")
    print()
    
    # Separar por tipo y estado
    casas_disponibles = []
    casas_ocupadas = []
    deptos_disponibles = []
    deptos_ocupadas = []
    locales_disponibles = []
    locales_ocupadas = []
    
    for vivienda in todas_viviendas:
        ocupada = vivienda.id in viviendas_ocupadas_ids
        
        if vivienda.tipo_vivienda == 'casa':
            if ocupada:
                casas_ocupadas.append(vivienda)
            else:
                casas_disponibles.append(vivienda)
        elif vivienda.tipo_vivienda == 'departamento':
            if ocupada:
                deptos_ocupadas.append(vivienda)
            else:
                deptos_disponibles.append(vivienda)
        else:  # local
            if ocupada:
                locales_ocupadas.append(vivienda)
            else:
                locales_disponibles.append(vivienda)
    
    # CASAS
    print("🏠 CASAS")
    print("="*50)
    print(f"🟢 CASAS DISPONIBLES ({len(casas_disponibles)} unidades):")
    print("-" * 50)
    
    if casas_disponibles:
        numeros_casas = [v.numero_casa for v in casas_disponibles]
        # Mostrar en columnas de 5
        for i in range(0, len(numeros_casas), 5):
            fila = numeros_casas[i:i+5]
            linea = "   " + " | ".join(f"{num:12}" for num in fila)
            print(linea)
    else:
        print("   No hay casas disponibles")
    
    print(f"\n🔴 CASAS OCUPADAS ({len(casas_ocupadas)} unidades):")
    print("-" * 50)
    if casas_ocupadas:
        for casa in casas_ocupadas:
            propietario = Propiedad.objects.filter(vivienda=casa, activo=True).first()
            if propietario:
                print(f"   {casa.numero_casa:12} - {propietario.persona.nombre} {propietario.persona.apellido}")
    else:
        print("   No hay casas ocupadas")
    
    # DEPARTAMENTOS
    print(f"\n🏢 DEPARTAMENTOS")
    print("="*50)
    print(f"🟢 DEPARTAMENTOS DISPONIBLES ({len(deptos_disponibles)} unidades):")
    print("-" * 50)
    
    if deptos_disponibles:
        numeros_deptos = [v.numero_casa for v in deptos_disponibles]
        # Mostrar en columnas de 5
        for i in range(0, len(numeros_deptos), 5):
            fila = numeros_deptos[i:i+5]
            linea = "   " + " | ".join(f"{num:12}" for num in fila)
            print(linea)
    else:
        print("   No hay departamentos disponibles")
    
    print(f"\n🔴 DEPARTAMENTOS OCUPADOS ({len(deptos_ocupadas)} unidades):")
    print("-" * 50)
    if deptos_ocupadas:
        for depto in deptos_ocupadas:
            propietario = Propiedad.objects.filter(vivienda=depto, activo=True).first()
            if propietario:
                print(f"   {depto.numero_casa:12} - {propietario.persona.nombre} {propietario.persona.apellido}")
    else:
        print("   No hay departamentos ocupados")
    
    # LOCALES
    print(f"\n🏪 LOCALES COMERCIALES")
    print("="*50)
    print(f"🟢 LOCALES DISPONIBLES ({len(locales_disponibles)} unidades):")
    print("-" * 50)
    
    if locales_disponibles:
        numeros_locales = [v.numero_casa for v in locales_disponibles]
        # Mostrar en columnas de 5
        for i in range(0, len(numeros_locales), 5):
            fila = numeros_locales[i:i+5]
            linea = "   " + " | ".join(f"{num:12}" for num in fila)
            print(linea)
    else:
        print("   No hay locales disponibles")
    
    print(f"\n🔴 LOCALES OCUPADOS ({len(locales_ocupadas)} unidades):")
    print("-" * 50)
    if locales_ocupadas:
        for local in locales_ocupadas:
            propietario = Propiedad.objects.filter(vivienda=local, activo=True).first()
            if propietario:
                print(f"   {local.numero_casa:12} - {propietario.persona.nombre} {propietario.persona.apellido}")
    else:
        print("   No hay locales ocupados")
    
    return casas_disponibles, deptos_disponibles, locales_disponibles

def generar_lista_para_frontend():
    """Generar listas específicas para usar en el frontend"""
    print("\n" + "="*80)
    print("📱 LISTAS PARA FRONTEND - COPY/PASTE")
    print("="*80)
    
    casas_disponibles, deptos_disponibles, locales_disponibles = generar_lista_viviendas()
    
    # Array JavaScript para casas
    print("\n🏠 ARRAY JAVASCRIPT - CASAS DISPONIBLES:")
    print("const casasDisponibles = [")
    for casa in casas_disponibles[:20]:  # Primeras 20
        print(f'  "{casa.numero_casa}",')
    if len(casas_disponibles) > 20:
        print(f'  // ... y {len(casas_disponibles) - 20} casas más')
    print("];")
    
    # Array JavaScript para departamentos
    print("\n🏢 ARRAY JAVASCRIPT - DEPARTAMENTOS DISPONIBLES:")
    print("const departamentosDisponibles = [")
    for depto in deptos_disponibles[:20]:  # Primeros 20
        print(f'  "{depto.numero_casa}",')
    if len(deptos_disponibles) > 20:
        print(f'  // ... y {len(deptos_disponibles) - 20} departamentos más')
    print("];")
    
    # Array JavaScript para locales
    print("\n🏪 ARRAY JAVASCRIPT - LOCALES DISPONIBLES:")
    print("const localesDisponibles = [")
    for local in locales_disponibles:
        print(f'  "{local.numero_casa}",')
    print("];")
    
    # Lista combinada
    print("\n📋 ARRAY COMBINADO - TODAS LAS VIVIENDAS DISPONIBLES:")
    print("const todasViviendasDisponibles = [")
    
    # Combinar todas
    todas_disponibles = (
        [(v.numero_casa, 'Casa') for v in casas_disponibles] +
        [(v.numero_casa, 'Departamento') for v in deptos_disponibles] +
        [(v.numero_casa, 'Local') for v in locales_disponibles]
    )
    
    for numero, tipo in todas_disponibles[:30]:  # Primeras 30
        print(f'  {{ numero: "{numero}", tipo: "{tipo}" }},')
    
    if len(todas_disponibles) > 30:
        print(f'  // ... y {len(todas_disponibles) - 30} viviendas más')
    print("];")

def generar_archivo_txt():
    """Generar archivo TXT con todas las viviendas"""
    print("\n" + "="*80)
    print("💾 GENERANDO ARCHIVO TXT...")
    
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    nombre_archivo = f"NUMEROS_VIVIENDAS_{timestamp}.txt"
    
    todas_viviendas = Vivienda.objects.all().order_by('tipo_vivienda', 'numero_casa')
    viviendas_ocupadas_ids = Propiedad.objects.filter(activo=True).values_list('vivienda_id', flat=True)
    
    with open(nombre_archivo, 'w', encoding='utf-8') as f:
        f.write("NÚMEROS DE VIVIENDAS PARA PRUEBAS FRONTEND\n")
        f.write("="*60 + "\n")
        f.write(f"Generado: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}\n")
        f.write(f"Total viviendas: {todas_viviendas.count()}\n\n")
        
        # Por tipo
        for tipo in ['casa', 'departamento', 'local']:
            viviendas_tipo = todas_viviendas.filter(tipo_vivienda=tipo)
            disponibles = viviendas_tipo.exclude(id__in=viviendas_ocupadas_ids)
            ocupadas = viviendas_tipo.filter(id__in=viviendas_ocupadas_ids)
            
            tipo_display = {'casa': 'CASAS', 'departamento': 'DEPARTAMENTOS', 'local': 'LOCALES'}[tipo]
            
            f.write(f"{tipo_display}\n")
            f.write("-" * 40 + "\n")
            f.write(f"DISPONIBLES ({disponibles.count()}):\n")
            
            numeros = [v.numero_casa for v in disponibles]
            for i, numero in enumerate(numeros):
                f.write(f"{numero}")
                if (i + 1) % 5 == 0:
                    f.write("\n")
                else:
                    f.write(" | ")
            
            f.write(f"\n\nOCUPADAS ({ocupadas.count()}):\n")
            for vivienda in ocupadas:
                propietario = Propiedad.objects.filter(vivienda=vivienda, activo=True).first()
                if propietario:
                    f.write(f"{vivienda.numero_casa} - {propietario.persona.nombre} {propietario.persona.apellido}\n")
            f.write("\n" + "="*60 + "\n\n")
    
    print(f"✅ Archivo generado: {nombre_archivo}")
    return nombre_archivo

def main():
    """Función principal"""
    try:
        # Mostrar lista en pantalla
        casas_disp, deptos_disp, locales_disp = generar_lista_viviendas()
        
        # Generar código para frontend
        generar_lista_para_frontend()
        
        # Generar archivo TXT
        archivo = generar_archivo_txt()
        
        print("\n" + "="*80)
        print("✅ LISTA DE VIVIENDAS GENERADA")
        print("="*80)
        print(f"📄 Archivo creado: {archivo}")
        print(f"🟢 Viviendas disponibles totales: {len(casas_disp) + len(deptos_disp) + len(locales_disp)}")
        print(f"🌐 Ver en navegador: http://127.0.0.1:8000/api/viviendas/")
        print("="*80)
        
        # Top 10 para pruebas rápidas
        print("\n🎯 TOP 10 VIVIENDAS PARA PRUEBAS RÁPIDAS:")
        print("-" * 50)
        todas_disponibles = list(casas_disp) + list(deptos_disp) + list(locales_disp)
        for i, vivienda in enumerate(todas_disponibles[:10], 1):
            tipo_emoji = {'casa': '🏠', 'departamento': '🏢', 'local': '🏪'}[vivienda.tipo_vivienda]
            print(f"{i:2d}. {tipo_emoji} {vivienda.numero_casa} - {vivienda.tipo_vivienda.title()} - {vivienda.metros_cuadrados}m²")
        
    except Exception as e:
        print(f"❌ Error generando lista: {e}")
        raise

if __name__ == "__main__":
    main()