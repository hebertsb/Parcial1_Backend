"""
Comando para crear usuarios de seguridad desde la línea de comandos
"""

from django.core.management.base import BaseCommand
from django.db import transaction
from authz.models import Usuario, Rol, Persona
import secrets
import string


class Command(BaseCommand):
    help = (
        "Crea un usuario de seguridad. "
        "Uso: python manage.py crear_seguridad --email seguridad@condominio.com --nombres Juan --apellidos Pérez --documento 12345678"
    )

    def add_arguments(self, parser):
        parser.add_argument('--email', required=True, help='Email del usuario de seguridad')
        parser.add_argument('--nombres', required=True, help='Nombres')
        parser.add_argument('--apellidos', required=True, help='Apellidos')
        parser.add_argument('--documento', required=True, help='Documento de identidad')
        parser.add_argument('--telefono', default='', help='Teléfono (opcional)')
        parser.add_argument('--password', help='Password personalizado (opcional, se genera automáticamente)')

    def handle(self, *args, **options):
        email = options['email']
        nombres = options['nombres']
        apellidos = options['apellidos']
        documento = options['documento']
        telefono = options['telefono']
        password = options.get('password')

        try:
            with transaction.atomic():
                # Verificar que no exista usuario con el mismo email
                if Usuario.objects.filter(email=email).exists():
                    self.stdout.write(
                        self.style.ERROR(f'❌ Error: Ya existe un usuario con el email {email}')
                    )
                    return

                # Verificar que no exista persona con el mismo documento
                if Persona.objects.filter(documento_identidad=documento).exists():
                    self.stdout.write(
                        self.style.ERROR(f'❌ Error: Ya existe una persona con el documento {documento}')
                    )
                    return

                # Generar password temporal si no se proporciona
                if not password:
                    password = f'seg{documento[:4]}2024'

                # Crear o obtener rol de seguridad
                rol_seguridad, created = Rol.objects.get_or_create(
                    nombre='Seguridad',
                    defaults={
                        'descripcion': 'Personal de seguridad del condominio',
                        'activo': True
                    }
                )

                if created:
                    self.stdout.write(
                        self.style.SUCCESS(f'✅ Rol "Seguridad" creado')
                    )

                # Crear persona
                persona = Persona.objects.create(
                    nombre=nombres,
                    apellido=apellidos,
                    documento_identidad=documento,
                    email=email,
                    telefono=telefono,
                    tipo_persona='seguridad',
                    activo=True
                )

                # Crear usuario
                usuario = Usuario.objects.create_user(
                    email=email,
                    password=password,
                    persona=persona,
                    estado='ACTIVO'
                )

                # Asignar rol
                usuario.roles.add(rol_seguridad)

                self.stdout.write(
                    self.style.SUCCESS(f'✅ Usuario de seguridad creado exitosamente')
                )
                self.stdout.write(f'📧 Email: {email}')
                self.stdout.write(f'👤 Nombre: {nombres} {apellidos}')
                self.stdout.write(f'📄 Documento: {documento}')
                self.stdout.write(f'🔑 Password temporal: {password}')
                self.stdout.write(
                    self.style.WARNING(f'⚠️  IMPORTANTE: Entregue estas credenciales al usuario de seguridad')
                )
                self.stdout.write(
                    self.style.WARNING(f'⚠️  El usuario debe cambiar el password en su primer login')
                )

        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'❌ Error creando usuario de seguridad: {str(e)}')
            )