#!/usr/bin/env python
"""
🏗️ POBLADOR RÁPIDO DE VIVIENDAS
Sistema de Reconocimiento Facial - Condominio

Uso rápido desde línea de comandos:
python poblar_viviendas_rapido.py 100                    # Crear 100 viviendas
python poblar_viviendas_rapido.py 50 --casas 30          # 50 total, 30 casas específicamente
python poblar_viviendas_rapido.py 200 --departamentos 120 --locales 20  # Distribución específica
"""

import os
import sys
import django
import random
import argparse
from datetime import datetime

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

# Imports después de configurar Django
from core.models.propiedades_residentes import Vivienda

class PobladorRapido:
    """Poblador rápido de viviendas"""
    
    def __init__(self):
        self.bloques = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J']
        self.estados = ['activa', 'inactiva', 'mantenimiento']
    
    def crear_lote_viviendas(self, cantidad, tipo='auto', prefijo=None):
        """Crear un lote de viviendas rápidamente"""
        viviendas_creadas = []
        base_numero = Vivienda.objects.count()
        
        print(f"🏗️ Creando {cantidad} viviendas tipo '{tipo}'...")
        
        for i in range(cantidad):
            try:
                # Determinar tipo si es automático
                if tipo == 'auto':
                    tipo_actual = random.choices(
                        ['casa', 'departamento', 'local'],
                        weights=[40, 50, 10]  # 40% casas, 50% deptos, 10% locales
                    )[0]
                else:
                    tipo_actual = tipo
                
                # Generar número único
                numero = self.generar_numero_rapido(tipo_actual, base_numero + i + 1, prefijo)
                
                # Generar datos según tipo
                if tipo_actual == 'casa':
                    area = round(random.uniform(80, 200), 2)
                    tarifa = round(random.uniform(200, 500), 2)
                elif tipo_actual == 'departamento':
                    area = round(random.uniform(45, 150), 2)
                    tarifa = round(random.uniform(150, 400), 2)
                else:  # local
                    area = round(random.uniform(20, 100), 2)
                    tarifa = round(random.uniform(100, 300), 2)
                
                # Crear vivienda
                vivienda = Vivienda.objects.create(
                    numero_casa=numero,
                    tipo_vivienda=tipo_actual,
                    metros_cuadrados=area,
                    tarifa_base_expensas=tarifa,
                    bloque=random.choice(self.bloques) if random.random() > 0.2 else None,
                    estado=random.choice(self.estados),
                    tipo_cobranza=random.choice(['por_casa', 'por_metro_cuadrado'])
                )
                
                viviendas_creadas.append(vivienda)
                
                # Progreso cada 25 viviendas
                if (i + 1) % 25 == 0:
                    print(f"   ✅ {i + 1}/{cantidad} viviendas creadas...")
                    
            except Exception as e:
                print(f"   ❌ Error en vivienda {i+1}: {e}")
        
        return viviendas_creadas
    
    def generar_numero_rapido(self, tipo, numero_base, prefijo=None):
        """Generar número de vivienda rápidamente"""
        if prefijo:
            base = f"{prefijo}-{numero_base:03d}"
        else:
            if tipo == 'casa':
                base = f"CASA-{numero_base:03d}"
            elif tipo == 'departamento':
                base = f"DEPT-{numero_base:03d}"
            else:
                base = f"LOCAL-{numero_base:03d}"
        
        # Verificar unicidad rápida
        contador = 0
        numero_final = base
        while Vivienda.objects.filter(numero_casa=numero_final).exists():
            contador += 1
            numero_final = f"{base}-{contador}"
        
        return numero_final

def poblar_rapido(total, casas=None, departamentos=None, locales=None, prefijo=None):
    """Función principal de poblado rápido"""
    poblador = PobladorRapido()
    viviendas_creadas = []
    
    print(f"🚀 POBLADO RÁPIDO DE {total} VIVIENDAS")
    print("="*60)
    print(f"📅 Inicio: {datetime.now().strftime('%H:%M:%S')}")
    
    # Si se especifican cantidades exactas
    if casas or departamentos or locales:
        total_especificado = (casas or 0) + (departamentos or 0) + (locales or 0)
        
        if total_especificado > total:
            print(f"⚠️  Cantidades específicas ({total_especificado}) exceden el total ({total})")
            print("Usando distribución automática...")
            casas = departamentos = locales = None
        else:
            # Crear cantidades específicas
            if casas:
                viviendas_creadas.extend(poblador.crear_lote_viviendas(casas, 'casa', prefijo))
            if departamentos:
                viviendas_creadas.extend(poblador.crear_lote_viviendas(departamentos, 'departamento', prefijo))
            if locales:
                viviendas_creadas.extend(poblador.crear_lote_viviendas(locales, 'local', prefijo))
            
            # Crear el resto automáticamente
            resto = total - total_especificado
            if resto > 0:
                viviendas_creadas.extend(poblador.crear_lote_viviendas(resto, 'auto', prefijo))
    
    # Si no se especifican cantidades, crear todo automáticamente
    if not (casas or departamentos or locales):
        viviendas_creadas = poblador.crear_lote_viviendas(total, 'auto', prefijo)
    
    # Mostrar resumen
    print("\n" + "="*60)
    print("✅ POBLADO COMPLETADO")
    print("="*60)
    print(f"📊 Viviendas creadas: {len(viviendas_creadas)}")
    print(f"🏠 Total en sistema: {Vivienda.objects.count()}")
    
    # Estadísticas por tipo
    tipos_creados = {}
    for vivienda in viviendas_creadas:
        tipo = vivienda.tipo_vivienda
        tipos_creados[tipo] = tipos_creados.get(tipo, 0) + 1
    
    print(f"\n📋 Distribución creada:")
    for tipo, cantidad in tipos_creados.items():
        porcentaje = (cantidad / len(viviendas_creadas)) * 100
        print(f"   🏠 {tipo.title()}: {cantidad} ({porcentaje:.1f}%)")
    
    print(f"\n📅 Completado: {datetime.now().strftime('%H:%M:%S')}")
    print(f"🌐 Ver resultado: http://127.0.0.1:8000/api/viviendas/")
    
    return viviendas_creadas

def main():
    """Función principal con argumentos de línea de comandos"""
    parser = argparse.ArgumentParser(
        description='🏗️ Poblador rápido de viviendas para el sistema de condominio',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Ejemplos de uso:
  python poblar_viviendas_rapido.py 100
  python poblar_viviendas_rapido.py 50 --casas 20 --departamentos 25 --locales 5
  python poblar_viviendas_rapido.py 200 --prefijo "TORRE1"
        """
    )
    
    parser.add_argument('total', type=int, help='Número total de viviendas a crear')
    parser.add_argument('--casas', type=int, help='Número específico de casas')
    parser.add_argument('--departamentos', type=int, help='Número específico de departamentos')
    parser.add_argument('--locales', type=int, help='Número específico de locales')
    parser.add_argument('--prefijo', type=str, help='Prefijo para los números de vivienda')
    
    args = parser.parse_args()
    
    # Validaciones
    if args.total <= 0:
        print("❌ El total debe ser mayor a 0")
        sys.exit(1)
    
    if args.total > 2000:
        respuesta = input(f"⚠️  {args.total} viviendas son muchas. ¿Continuar? (s/n): ")
        if respuesta.lower() not in ['s', 'si', 'sí', 'yes', 'y']:
            print("👋 Cancelado")
            sys.exit(0)
    
    try:
        viviendas_creadas = poblar_rapido(
            args.total,
            args.casas,
            args.departamentos,
            args.locales,
            args.prefijo
        )
        
        print(f"\n🎉 ¡{len(viviendas_creadas)} viviendas creadas exitosamente!")
        
    except Exception as e:
        print(f"\n❌ Error durante el poblado: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()