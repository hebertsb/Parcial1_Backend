"""
Comando para crear viviendas de prueba para el sistema
"""
from django.core.management.base import BaseCommand
from core.models import Vivienda
from decimal import Decimal
import random

class Command(BaseCommand):
    help = 'Crea viviendas de prueba para el sistema'

    def add_arguments(self, parser):
        parser.add_argument(
            '--cantidad',
            type=int,
            default=20,
            help='Cantidad de viviendas a crear (default: 20)'
        )
        parser.add_argument(
            '--limpiar',
            action='store_true',
            help='Eliminar todas las viviendas existentes antes de crear nuevas'
        )

    def handle(self, **options):
        cantidad = options['cantidad']
        limpiar = options['limpiar']
        
        if limpiar:
            self.stdout.write("🗑️ Eliminando viviendas existentes...")
            count_eliminadas = Vivienda.objects.count()
            Vivienda.objects.all().delete()
            self.stdout.write(
                self.style.WARNING(f"❌ Eliminadas {count_eliminadas} viviendas existentes")
            )
        
        self.stdout.write(f"🏠 Creando {cantidad} viviendas de prueba...")
        
        # Definir tipos de vivienda y bloques
        tipos_vivienda = ['casa', 'departamento']
        bloques = ['A', 'B', 'C', 'D', 'E']
        tipos_cobranza = ['por_casa', 'por_metro_cuadrado']
        
        viviendas_creadas = 0
        
        for i in range(1, cantidad + 1):
            # Generar número de casa único
            bloque = random.choice(bloques)
            numero = f"{i:03d}{bloque}"  # 001A, 002B, etc.
            
            # Verificar que no exista
            if Vivienda.objects.filter(numero_casa=numero).exists():
                continue
            
            tipo_vivienda = random.choice(tipos_vivienda)
            metros_cuadrados = Decimal(str(random.randint(45, 150)))  # Entre 45 y 150 m²
            
            # Tarifa base según tipo y tamaño
            if tipo_vivienda == 'casa':
                tarifa_base = Decimal(str(random.randint(800, 1500)))  # Bs. 800-1500
            else:
                tarifa_base = Decimal(str(random.randint(400, 1000)))   # Bs. 400-1000
            
            try:
                vivienda = Vivienda.objects.create(
                    numero_casa=numero,
                    bloque=bloque,
                    tipo_vivienda=tipo_vivienda,
                    metros_cuadrados=metros_cuadrados,
                    tarifa_base_expensas=tarifa_base,
                    tipo_cobranza=random.choice(tipos_cobranza),
                    estado='activa'
                )
                
                viviendas_creadas += 1
                
                # Mostrar progreso cada 5 viviendas
                if viviendas_creadas % 5 == 0:
                    self.stdout.write(f"✅ Creadas {viviendas_creadas} viviendas...")
                
            except Exception as e:
                self.stdout.write(
                    self.style.ERROR(f"❌ Error creando vivienda {numero}: {e}")
                )
        
        self.stdout.write(
            self.style.SUCCESS(f"🎉 ¡Creadas {viviendas_creadas} viviendas exitosamente!")
        )
        
        # Mostrar resumen
        self.mostrar_resumen()

    def mostrar_resumen(self):
        """Muestra un resumen de las viviendas creadas"""
        self.stdout.write("\n📊 RESUMEN DE VIVIENDAS:")
        self.stdout.write("=" * 50)
        
        total = Vivienda.objects.count()
        casas = Vivienda.objects.filter(tipo_vivienda='casa').count()
        departamentos = Vivienda.objects.filter(tipo_vivienda='departamento').count()
        
        self.stdout.write(f"🏠 Total viviendas: {total}")
        self.stdout.write(f"🏘️ Casas: {casas}")
        self.stdout.write(f"🏢 Departamentos: {departamentos}")
        
        # Mostrar por bloque
        self.stdout.write("\n📍 Por bloque:")
        for bloque in ['A', 'B', 'C', 'D', 'E']:
            count = Vivienda.objects.filter(bloque=bloque).count()
            if count > 0:
                self.stdout.write(f"   Bloque {bloque}: {count} viviendas")
        
        # Mostrar algunas viviendas disponibles
        self.stdout.write("\n🆓 Viviendas disponibles para registro:")
        viviendas_disponibles = Vivienda.objects.all()[:10]
        
        for vivienda in viviendas_disponibles:
            self.stdout.write(
                f"   {vivienda.numero_casa} - {vivienda.tipo_vivienda.title()} "
                f"({vivienda.metros_cuadrados}m²) - Bs.{vivienda.tarifa_base_expensas}"
            )
        
        if total > 10:
            self.stdout.write(f"   ... y {total - 10} más")
        
        self.stdout.write("\n✅ Listo para probar el frontend!")