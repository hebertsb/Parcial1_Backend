#!/usr/bin/env python
"""
🏗️ POBLADOR AUTOMÁTICO DE VIVIENDAS
Sistema de Reconocimiento Facial - Condominio

Este script permite crear automáticamente cualquier cantidad de viviendas:
✅ Especifica cuántas viviendas quieres
✅ Distribución automática por tipos (casas, departamentos, locales)
✅ Generación automática de números y datos
✅ Bloques y características aleatorias realistas

Ejecutar: python poblar_viviendas_automatico.py
"""

import os
import sys
import django
import random
from datetime import datetime

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

# Imports después de configurar Django
from core.models.propiedades_residentes import Vivienda
from faker import Faker

fake = Faker('es_ES')

class PobladorViviendas:
    """Clase para poblar viviendas automáticamente"""
    
    def __init__(self):
        self.bloques = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H']
        self.tipos_vivienda = {
            'casa': {
                'peso': 40,  # 40% casas
                'area_min': 80,
                'area_max': 200,
                'tarifa_min': 200,
                'tarifa_max': 500
            },
            'departamento': {
                'peso': 50,  # 50% departamentos  
                'area_min': 45,
                'area_max': 150,
                'tarifa_min': 150,
                'tarifa_max': 400
            },
            'local': {
                'peso': 10,  # 10% locales
                'area_min': 20,
                'area_max': 100,
                'tarifa_min': 100,
                'tarifa_max': 300
            }
        }
        self.estados = ['activa', 'inactiva', 'mantenimiento']
    
    def obtener_estadisticas_actuales(self):
        """Obtener estadísticas actuales de viviendas"""
        total_actual = Vivienda.objects.count()
        por_tipo = {}
        
        for tipo in ['casa', 'departamento', 'local']:
            count = Vivienda.objects.filter(tipo_vivienda=tipo).count()
            por_tipo[tipo] = count
        
        return total_actual, por_tipo
    
    def generar_numero_casa_unico(self, tipo, contador):
        """Generar número de casa único según el tipo"""
        numero_base = Vivienda.objects.count() + contador + 1
        
        if tipo == 'casa':
            formatos = [
                f"CASA-{numero_base:03d}",
                f"C{numero_base:03d}",
                f"{numero_base:02d}A",
                f"{numero_base:02d}B",
                f"VILLA-{numero_base:02d}"
            ]
        elif tipo == 'departamento':
            formatos = [
                f"DEPT-{numero_base:03d}",
                f"D{numero_base:03d}",
                f"{numero_base:03d}",
                f"APT-{numero_base:02d}",
                f"{random.choice(self.bloques)}{numero_base:02d}"
            ]
        else:  # local
            formatos = [
                f"LOCAL-{numero_base:02d}",
                f"L{numero_base:02d}",
                f"COM-{numero_base:02d}",
                f"LOC{numero_base:03d}"
            ]
        
        numero_propuesto = random.choice(formatos)
        
        # Verificar que sea único
        contador_verificacion = 0
        while Vivienda.objects.filter(numero_casa=numero_propuesto).exists():
            contador_verificacion += 1
            if tipo == 'casa':
                numero_propuesto = f"CASA-{numero_base + contador_verificacion:03d}"
            elif tipo == 'departamento':
                numero_propuesto = f"DEPT-{numero_base + contador_verificacion:03d}"
            else:
                numero_propuesto = f"LOCAL-{numero_base + contador_verificacion:02d}"
        
        return numero_propuesto
    
    def calcular_distribucion(self, total_viviendas):
        """Calcular cuántas viviendas de cada tipo crear"""
        distribucion = {}
        total_peso = sum(info['peso'] for info in self.tipos_vivienda.values())
        
        viviendas_asignadas = 0
        for tipo, info in self.tipos_vivienda.items():
            if tipo == 'local':  # Asignar el resto a locales
                distribucion[tipo] = total_viviendas - viviendas_asignadas
            else:
                cantidad = int((info['peso'] / total_peso) * total_viviendas)
                distribucion[tipo] = cantidad
                viviendas_asignadas += cantidad
        
        return distribucion
    
    def crear_vivienda(self, tipo, contador):
        """Crear una vivienda individual"""
        info_tipo = self.tipos_vivienda[tipo]
        
        # Generar datos aleatorios realistas
        area = round(random.uniform(info_tipo['area_min'], info_tipo['area_max']), 2)
        tarifa = round(random.uniform(info_tipo['tarifa_min'], info_tipo['tarifa_max']), 2)
        
        vivienda = Vivienda.objects.create(
            numero_casa=self.generar_numero_casa_unico(tipo, contador),
            tipo_vivienda=tipo,
            metros_cuadrados=area,
            tarifa_base_expensas=tarifa,
            bloque=random.choice(self.bloques) if random.random() > 0.3 else None,
            estado=random.choice(self.estados),
            tipo_cobranza=random.choice(['por_casa', 'por_metro_cuadrado'])
        )
        
        return vivienda
    
    def generar_descripcion(self, tipo, area):
        """Generar descripción realista para la vivienda"""
        descripciones = {
            'casa': [
                f"Casa de {area}m² con jardín privado",
                f"Vivienda unifamiliar de {area}m² con patio",
                f"Casa moderna de {area}m² con garaje",
                f"Residencia de {area}m² en zona tranquila"
            ],
            'departamento': [
                f"Departamento de {area}m² con balcón",
                f"Moderno apartamento de {area}m² con vista",
                f"Cómodo departamento de {area}m² bien ubicado",
                f"Departamento familiar de {area}m² con amenidades"
            ],
            'local': [
                f"Local comercial de {area}m² para negocio",
                f"Espacio comercial de {area}m² en planta baja",
                f"Local de {area}m² ideal para oficina",
                f"Amplio local de {area}m² con vitrina"
            ]
        }
        
        return random.choice(descripciones[tipo])
    
    def poblar_viviendas(self, cantidad_total):
        """Poblar viviendas automáticamente"""
        print(f"🏗️ Iniciando creación de {cantidad_total} viviendas...")
        
        # Mostrar estadísticas actuales
        total_actual, por_tipo_actual = self.obtener_estadisticas_actuales()
        print(f"📊 Viviendas actuales: {total_actual}")
        
        # Calcular distribución
        distribucion = self.calcular_distribucion(cantidad_total)
        print(f"📋 Distribución planificada:")
        for tipo, cantidad in distribucion.items():
            porcentaje = (cantidad / cantidad_total) * 100
            print(f"   🏠 {tipo.title()}: {cantidad} ({porcentaje:.1f}%)")
        
        print("\n🚀 Creando viviendas...")
        
        viviendas_creadas = []
        contador_global = 0
        
        for tipo, cantidad in distribucion.items():
            print(f"\n📦 Creando {cantidad} {tipo}s...")
            
            for i in range(cantidad):
                try:
                    vivienda = self.crear_vivienda(tipo, contador_global)
                    viviendas_creadas.append(vivienda)
                    contador_global += 1
                    
                    # Mostrar progreso cada 10 viviendas
                    if (i + 1) % 10 == 0:
                        print(f"   ✅ {i + 1}/{cantidad} {tipo}s creadas...")
                        
                except Exception as e:
                    print(f"   ❌ Error creando {tipo} {i+1}: {e}")
        
        return viviendas_creadas
    
    def mostrar_resumen_final(self, viviendas_creadas):
        """Mostrar resumen de viviendas creadas"""
        print("\n" + "="*80)
        print("✅ CREACIÓN COMPLETADA")
        print("="*80)
        
        total_nuevo, por_tipo_nuevo = self.obtener_estadisticas_actuales()
        
        print(f"📊 ESTADÍSTICAS FINALES:")
        print(f"   🏠 Total de viviendas: {total_nuevo}")
        print(f"   ➕ Viviendas creadas: {len(viviendas_creadas)}")
        
        print(f"\n📋 POR TIPO:")
        for tipo in ['casa', 'departamento', 'local']:
            count = por_tipo_nuevo[tipo]
            porcentaje = (count / total_nuevo) * 100 if total_nuevo > 0 else 0
            print(f"   🏠 {tipo.title()}: {count} ({porcentaje:.1f}%)")
        
        print(f"\n🎯 EJEMPLOS DE VIVIENDAS CREADAS:")
        for i, vivienda in enumerate(viviendas_creadas[:5]):
            tipo_display = {'casa': 'Casa', 'departamento': 'Departamento', 'local': 'Local'}[vivienda.tipo_vivienda]
            print(f"   {i+1}. {vivienda.numero_casa} - {tipo_display} - {vivienda.metros_cuadrados}m² - ${vivienda.tarifa_base_expensas}")
        
        if len(viviendas_creadas) > 5:
            print(f"   ... y {len(viviendas_creadas) - 5} viviendas más")
        
        print(f"\n🌐 Sistema disponible en: http://127.0.0.1:8000/")
        print(f"📚 Ver viviendas: http://127.0.0.1:8000/api/viviendas/")

def solicitar_cantidad():
    """Solicitar al usuario cuántas viviendas quiere crear"""
    print("🏗️ POBLADOR AUTOMÁTICO DE VIVIENDAS")
    print("="*60)
    
    while True:
        try:
            cantidad = input("\n¿Cuántas viviendas quieres crear? (ejemplo: 100): ")
            cantidad = int(cantidad)
            
            if cantidad <= 0:
                print("❌ La cantidad debe ser mayor a 0")
                continue
            
            if cantidad > 1000:
                confirmacion = input(f"⚠️  {cantidad} viviendas son muchas. ¿Continuar? (s/n): ")
                if confirmacion.lower() not in ['s', 'si', 'sí', 'yes', 'y']:
                    continue
            
            return cantidad
            
        except ValueError:
            print("❌ Por favor ingresa un número válido")
        except KeyboardInterrupt:
            print("\n👋 Cancelado por el usuario")
            sys.exit(0)

def main():
    """Función principal"""
    try:
        # Solicitar cantidad
        cantidad = solicitar_cantidad()
        
        print(f"\n🚀 Iniciando creación de {cantidad} viviendas...")
        
        # Crear poblador y ejecutar
        poblador = PobladorViviendas()
        viviendas_creadas = poblador.poblar_viviendas(cantidad)
        
        # Mostrar resumen
        poblador.mostrar_resumen_final(viviendas_creadas)
        
        print("\n" + "="*80)
        print("🎉 ¡PROCESO COMPLETADO EXITOSAMENTE!")
        print("="*80)
        
    except Exception as e:
        print(f"\n❌ Error durante la creación: {e}")
        raise

if __name__ == "__main__":
    main()