#!/usr/bin/env python
import django
import os
import sys

# Configurar Django
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from core.models import Vivienda

print("=== CREAR VIVIENDA DE PRUEBA ===")

# Crear vivienda A-101 si no existe
try:
    vivienda, created = Vivienda.objects.get_or_create(
        numero_casa='A-101',
        defaults={
            'bloque': 'A',
            'tipo_vivienda': 'departamento',
            'metros_cuadrados': 85.5,
            'tarifa_base_expensas': 150.00,
            'tipo_cobranza': 'por_casa',
            'estado': 'activa'
        }
    )
    
    if created:
        print(f"✅ Vivienda creada: {vivienda.numero_casa}")
    else:
        print(f"ℹ️ Vivienda ya existe: {vivienda.numero_casa}")
        
    print(f"🏠 Detalles:")
    print(f"   Número: {vivienda.numero_casa}")
    print(f"   Bloque: {vivienda.bloque}")
    print(f"   Tipo: {vivienda.tipo_vivienda}")
    print(f"   Área: {vivienda.metros_cuadrados} m²")
    print(f"   Estado: {vivienda.estado}")
    print(f"   Tarifa base: ${vivienda.tarifa_base_expensas}")
    
except Exception as e:
    print(f"❌ Error creando vivienda: {e}")