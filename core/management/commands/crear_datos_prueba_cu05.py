# Script para crear datos de prueba - CU05
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from core.models.propiedades_residentes import Vivienda, Propiedad
from authz.models import Usuario, Rol, Persona
from decimal import Decimal
from datetime import date

User = get_user_model()

class Command(BaseCommand):
    help = 'Crear datos de prueba para CU05 - Gestionar Unidades Habitacionales'
    
    def handle(self, *args, **options):
        self.stdout.write('🏗️ Creando datos de prueba para CU05...')
        
        # 1. Crear usuario admin si no existe
        admin_user, created = Usuario.objects.get_or_create(
            email='admin@condominio.com',
            defaults={
                'is_staff': True,
                'is_superuser': True,
                'estado': 'ACTIVO'
            }
        )
        if created:
            # Crear persona para el admin
            admin_persona, _ = Persona.objects.get_or_create(
                documento_identidad='99999999',
                defaults={
                    'nombre': 'Administrador',
                    'apellido': 'Sistema',
                    'email': 'admin@condominio.com',
                    'tipo_persona': 'administrador'
                }
            )
            admin_user.persona = admin_persona
            admin_user.set_password('admin123')
            admin_user.save()
            self.stdout.write('✅ Usuario admin creado')
        else:
            self.stdout.write('ℹ️ Usuario admin ya existe')
        
        # 2. Crear personas de prueba
        personas_data = [
            {
                'nombre': 'Juan Carlos',
                'apellido': 'Pérez López',
                'documento_identidad': '12345678',
                'email': 'juan.perez@email.com',
                'fecha_nacimiento': date(1980, 5, 15),
                'tipo_persona': 'propietario'
            },
            {
                'nombre': 'María Elena',
                'apellido': 'García Rodríguez',
                'documento_identidad': '87654321',
                'email': 'maria.garcia@email.com',
                'fecha_nacimiento': date(1985, 8, 22),
                'tipo_persona': 'propietario'
            },
            {
                'nombre': 'Carlos Alberto',
                'apellido': 'Mendoza Silva',
                'documento_identidad': '11223344',
                'email': 'carlos.mendoza@email.com',
                'fecha_nacimiento': date(1975, 12, 10),
                'tipo_persona': 'inquilino'
            },
            {
                'nombre': 'Ana Sofía',
                'apellido': 'Vargas Torres',
                'documento_identidad': '44332211',
                'email': 'ana.vargas@email.com',
                'fecha_nacimiento': date(1990, 3, 8),
                'tipo_persona': 'inquilino'
            }
        ]
        
        personas_creadas = []
        for persona_data in personas_data:
            persona, created = Persona.objects.get_or_create(
                documento_identidad=persona_data['documento_identidad'],
                defaults=persona_data
            )
            personas_creadas.append(persona)
            if created:
                self.stdout.write(f'✅ Persona creada: {persona.nombre} {persona.apellido}')
            else:
                self.stdout.write(f'ℹ️ Persona ya existe: {persona.nombre} {persona.apellido}')
        
        # 3. Crear viviendas de prueba
        viviendas_data = [
            {
                'numero_casa': '101A',
                'bloque': 'A',
                'tipo_vivienda': 'departamento',
                'metros_cuadrados': Decimal('85.50'),
                'tarifa_base_expensas': Decimal('250.00'),
                'tipo_cobranza': 'por_casa',
                'estado': 'activa'
            },
            {
                'numero_casa': '102A',
                'bloque': 'A',
                'tipo_vivienda': 'departamento',
                'metros_cuadrados': Decimal('92.75'),
                'tarifa_base_expensas': Decimal('275.00'),
                'tipo_cobranza': 'por_casa',
                'estado': 'activa'
            },
            {
                'numero_casa': '201B',
                'bloque': 'B',
                'tipo_vivienda': 'casa',
                'metros_cuadrados': Decimal('120.00'),
                'tarifa_base_expensas': Decimal('350.00'),
                'tipo_cobranza': 'por_metro_cuadrado',
                'estado': 'activa'
            },
            {
                'numero_casa': '202B',
                'bloque': 'B',
                'tipo_vivienda': 'casa',
                'metros_cuadrados': Decimal('110.25'),
                'tarifa_base_expensas': Decimal('325.00'),
                'tipo_cobranza': 'por_metro_cuadrado',
                'estado': 'mantenimiento'
            },
            {
                'numero_casa': 'L01',
                'bloque': 'C',
                'tipo_vivienda': 'local',
                'metros_cuadrados': Decimal('45.00'),
                'tarifa_base_expensas': Decimal('150.00'),
                'tipo_cobranza': 'por_casa',
                'estado': 'activa'
            }
        ]
        
        viviendas_creadas = []
        for vivienda_data in viviendas_data:
            vivienda, created = Vivienda.objects.get_or_create(
                numero_casa=vivienda_data['numero_casa'],
                defaults=vivienda_data
            )
            viviendas_creadas.append(vivienda)
            if created:
                self.stdout.write(f'✅ Vivienda creada: {vivienda.numero_casa} - {vivienda.tipo_vivienda}')
            else:
                self.stdout.write(f'ℹ️ Vivienda ya existe: {vivienda.numero_casa}')
        
        # 4. Crear asignaciones de propiedades
        asignaciones = [
            {
                'vivienda': viviendas_creadas[0],  # 101A
                'persona': personas_creadas[0],   # Juan Carlos
                'tipo_tenencia': 'propietario',
                'porcentaje_propiedad': Decimal('100.00'),
                'fecha_inicio_tenencia': date(2024, 1, 1)
            },
            {
                'vivienda': viviendas_creadas[1],  # 102A
                'persona': personas_creadas[1],   # María Elena
                'tipo_tenencia': 'propietario',
                'porcentaje_propiedad': Decimal('100.00'),
                'fecha_inicio_tenencia': date(2024, 2, 15)
            },
            {
                'vivienda': viviendas_creadas[2],  # 201B
                'persona': personas_creadas[2],   # Carlos Alberto
                'tipo_tenencia': 'inquilino',
                'porcentaje_propiedad': Decimal('100.00'),
                'fecha_inicio_tenencia': date(2024, 6, 1)
            },
            {
                'vivienda': viviendas_creadas[4],  # L01
                'persona': personas_creadas[3],   # Ana Sofía
                'tipo_tenencia': 'inquilino',
                'porcentaje_propiedad': Decimal('100.00'),
                'fecha_inicio_tenencia': date(2024, 8, 15)
            }
        ]
        
        for asignacion_data in asignaciones:
            propiedad, created = Propiedad.objects.get_or_create(
                vivienda=asignacion_data['vivienda'],
                persona=asignacion_data['persona'],
                tipo_tenencia=asignacion_data['tipo_tenencia'],
                defaults={
                    'porcentaje_propiedad': asignacion_data['porcentaje_propiedad'],
                    'fecha_inicio_tenencia': asignacion_data['fecha_inicio_tenencia'],
                    'activo': True
                }
            )
            if created:
                self.stdout.write(
                    f'✅ Asignación creada: {propiedad.persona.nombre} → '
                    f'{propiedad.vivienda.numero_casa} como {propiedad.tipo_tenencia}'
                )
            else:
                self.stdout.write(
                    f'ℹ️ Asignación ya existe: {propiedad.persona.nombre} → '
                    f'{propiedad.vivienda.numero_casa}'
                )
        
        self.stdout.write('\n🎉 ¡Datos de prueba creados exitosamente!')
        self.stdout.write('\n📊 RESUMEN:')
        self.stdout.write(f'   👤 Personas: {len(personas_creadas)}')
        self.stdout.write(f'   🏠 Viviendas: {len(viviendas_creadas)}')
        self.stdout.write(f'   📋 Asignaciones: {len(asignaciones)}')
        self.stdout.write('\n🔐 CREDENCIALES DE PRUEBA:')
        self.stdout.write('   📧 Email: admin@condominio.com')
        self.stdout.write('   🔑 Password: admin123')
        self.stdout.write('\n🚀 ¡Listo para probar en Postman!')