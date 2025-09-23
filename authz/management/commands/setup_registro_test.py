"""
Comando para crear datos de prueba para el sistema de registro de propietarios
"""
from django.core.management.base import BaseCommand
from django.db import transaction
from core.models.propiedades_residentes import Vivienda, Propiedad
from authz.models import SolicitudRegistroPropietario, FamiliarPropietario, Persona
from datetime import date
import random

class Command(BaseCommand):
    help = 'Crea datos de prueba para el sistema de registro de propietarios'

    def add_arguments(self, parser):
        parser.add_argument(
            '--num-viviendas',
            type=int,
            default=10,
            help='Número de viviendas a crear'
        )
        parser.add_argument(
            '--num-solicitudes',
            type=int,
            default=5,
            help='Número de solicitudes de prueba a crear'
        )

    @transaction.atomic
    def handle(self, *args, **options):
        self.stdout.write('Creando datos de prueba para registro de propietarios...')
        
        # Crear viviendas de prueba
        self.crear_viviendas(options['num_viviendas'])
        
        # Crear solicitudes de prueba
        self.crear_solicitudes(options['num_solicitudes'])
        
        self.stdout.write(
            self.style.SUCCESS(
                f'✓ Datos de prueba creados exitosamente:\n'
                f'  - {options["num_viviendas"]} viviendas\n'
                f'  - {options["num_solicitudes"]} solicitudes'
            )
        )

    def crear_viviendas(self, num_viviendas):
        """Crea viviendas de prueba"""
        bloques = ['A', 'B', 'C', 'D']
        tipos = [('casa', 'Casa'), ('departamento', 'Departamento'), ('local', 'Local')]
        
        for i in range(1, num_viviendas + 1):
            tipo_choice = random.choice(tipos)
            vivienda, created = Vivienda.objects.get_or_create(
                numero_casa=f"V{i:03d}",
                defaults={
                    'bloque': random.choice(bloques),
                    'tipo_vivienda': tipo_choice[0],  # Usar el valor, no la tupla
                    'metros_cuadrados': random.randint(80, 200),
                    'tarifa_base_expensas': random.randint(100, 500),
                    'tipo_cobranza': random.choice(['por_casa', 'por_metro_cuadrado']),
                    'estado': 'activa'
                }
            )
            
            if created:
                self.stdout.write(f'  Vivienda creada: {vivienda.numero_casa} - {vivienda.tipo_vivienda}')

    def crear_solicitudes(self, num_solicitudes):
        """Crea solicitudes de prueba"""
        viviendas_disponibles = list(
            Vivienda.objects.filter(estado='activa')
            .exclude(id__in=Propiedad.objects.values_list('vivienda_id', flat=True))
            [:num_solicitudes]
        )
        
        if len(viviendas_disponibles) < num_solicitudes:
            self.stdout.write(
                self.style.WARNING(
                    f'Solo hay {len(viviendas_disponibles)} viviendas disponibles. '
                    f'Creando {len(viviendas_disponibles)} solicitudes.'
                )
            )
        
        nombres = ['Carlos', 'María', 'Juan', 'Ana', 'Luis', 'Carmen', 'Pedro', 'Laura']
        apellidos = ['García', 'Rodríguez', 'López', 'Martínez', 'González', 'Pérez', 'Sánchez', 'Ramírez']
        
        for i, vivienda in enumerate(viviendas_disponibles, 1):
            nombre = random.choice(nombres)
            apellido = random.choice(apellidos)
            
            solicitud = SolicitudRegistroPropietario.objects.create(
                nombres=f"{nombre} Segundo",
                apellidos=f"{apellido} Segundo",
                documento_identidad=f"12345{i:03d}",
                fecha_nacimiento="1990-01-01",  # Fecha por defecto
                email=f"{nombre.lower()}.{apellido.lower()}{i}@test.com",
                telefono=f"987654{i:03d}",
                numero_casa=vivienda.numero_casa,
                comentarios_admin=f"Solicitud de prueba para {vivienda.numero_casa}",
                estado='PENDIENTE'
            )
            
            # Agregar algunos familiares
            if random.choice([True, False]):  # 50% probabilidad
                # Crear persona para el familiar
                persona_familiar = Persona.objects.create(
                    nombre=f"Familiar{i}",
                    apellido=apellido,
                    documento_identidad=f"98765{i:03d}",
                    telefono=f"555123{i:03d}",
                    email=f"familiar{i}.{apellido.lower()}@test.com",
                    fecha_nacimiento=date(1995, 1, 1),
                    genero='M' if i % 2 == 0 else 'F'
                )
                
                # Crear el familiar si la solicitud fue aprobada y tiene usuario
                if solicitud.usuario_creado:
                    FamiliarPropietario.objects.create(
                        propietario=solicitud.usuario_creado,
                        persona=persona_familiar,
                        parentesco=random.choice(['conyugue', 'hijo', 'padre']),
                        autorizado_acceso=True,
                        puede_autorizar_visitas=False
                    )
            
            self.stdout.write(f'  Solicitud creada: {solicitud.nombres} {solicitud.apellidos} - {vivienda.numero_casa}')
        
        self.stdout.write(f'  Total solicitudes creadas: {len(viviendas_disponibles)}')