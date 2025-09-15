"""
Management command para crear datos de prueba
"""

from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from seguridad.models import Roles, Usuarios, Copropietarios


class Command(BaseCommand):
    help = 'Crea datos de prueba para el sistema de reconocimiento facial'

    def handle(self, *args, **options):
        self.stdout.write('Creando datos de prueba...')

        # Crear roles
        rol_admin, created = Roles.objects.get_or_create(
            nombre='Administrador',
            defaults={
                'descripcion': 'Administrador del sistema con acceso completo'
            }
        )
        if created:
            self.stdout.write(f'✓ Rol creado: {rol_admin.nombre}')

        rol_operador, created = Roles.objects.get_or_create(
            nombre='Operador',
            defaults={
                'descripcion': 'Operador de seguridad con acceso a reconocimiento facial'
            }
        )
        if created:
            self.stdout.write(f'✓ Rol creado: {rol_operador.nombre}')

        # Crear usuario operador
        user_operador, created = User.objects.get_or_create(
            username='operador',
            defaults={
                'email': 'operador@test.com',
                'first_name': 'Juan',
                'last_name': 'Seguridad'
            }
        )
        if created:
            user_operador.set_password('operador123')
            user_operador.save()
            self.stdout.write(f'✓ Usuario creado: {user_operador.username}')

        # Crear perfil de usuario operador
        usuario_operador, created = Usuarios.objects.get_or_create(
            user=user_operador,
            defaults={
                'rol': rol_operador,
                'telefono': '+573001234567'
            }
        )
        if created:
            self.stdout.write(f'✓ Perfil de usuario creado: {usuario_operador}')

        # Crear copropietarios de prueba
        copropietarios_data = [
            {
                'nombres': 'María Elena',
                'apellidos': 'González López',
                'numero_documento': '12345678',
                'tipo_documento': 'CC',
                'telefono': '+573009876543',
                'email': 'maria.gonzalez@email.com',
                'unidad_residencial': 'Apto 101'
            },
            {
                'nombres': 'Carlos Alberto',
                'apellidos': 'Rodríguez Pérez',
                'numero_documento': '87654321',
                'tipo_documento': 'CC',
                'telefono': '+573011234567',
                'email': 'carlos.rodriguez@email.com',
                'unidad_residencial': 'Apto 205'
            },
            {
                'nombres': 'Ana Sofía',
                'apellidos': 'Martínez Silva',
                'numero_documento': '11223344',
                'tipo_documento': 'CC',
                'telefono': '+573023456789',
                'email': 'ana.martinez@email.com',
                'unidad_residencial': 'Casa 15'
            },
            {
                'nombres': 'José Miguel',
                'apellidos': 'Hernández Torres',
                'numero_documento': '44332211',
                'tipo_documento': 'CC',
                'telefono': '+573034567890',
                'email': 'jose.hernandez@email.com',
                'unidad_residencial': 'Apto 312'
            }
        ]

        for coprop_data in copropietarios_data:
            copropietario, created = Copropietarios.objects.get_or_create(
                numero_documento=coprop_data['numero_documento'],
                defaults=coprop_data
            )
            if created:
                self.stdout.write(
                    f'✓ Copropietario creado: {copropietario.nombre_completo} - {copropietario.unidad_residencial}'
                )

        self.stdout.write(
            self.style.SUCCESS('✅ Datos de prueba creados exitosamente!')
        )
        
        self.stdout.write('\n📋 Resumen:')
        self.stdout.write(f'- Roles: {Roles.objects.count()}')
        self.stdout.write(f'- Usuarios: {Usuarios.objects.count()}')
        self.stdout.write(f'- Copropietarios: {Copropietarios.objects.count()}')
        
        self.stdout.write('\n🔑 Credenciales de prueba:')
        self.stdout.write('👤 Administrador: admin / admin')
        self.stdout.write('👤 Operador: operador / operador123')
        
        self.stdout.write('\n🏠 Copropietarios disponibles para enrolamiento:')
        for coprop in Copropietarios.objects.all():
            self.stdout.write(f'  - ID {coprop.id}: {coprop.nombre_completo} ({coprop.unidad_residencial})')
        
        self.stdout.write('\n🔗 URLs útiles:')
        self.stdout.write('  - Admin: http://127.0.0.1:8000/admin/')
        self.stdout.write('  - API Docs: http://127.0.0.1:8000/api/docs/')
        self.stdout.write('  - JWT Token: http://127.0.0.1:8000/api/auth/login/')
