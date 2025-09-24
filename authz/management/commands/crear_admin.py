from django.core.management.base import BaseCommand
from authz.models import Usuario, Rol, Persona
from rest_framework_simplejwt.tokens import RefreshToken


class Command(BaseCommand):
    help = (
        "Crea un usuario admin y le asigna rol Administrador. "
        "Uso: python manage.py crear_admin --email admin@example.com --password secret --nombres Admin --apellidos User"
    )

    def add_arguments(self, parser):
        parser.add_argument('--email', required=True, help='Email del admin')
        parser.add_argument('--password', required=True, help='Password')
        parser.add_argument('--nombres', required=True, help='Nombres')
        parser.add_argument('--apellidos', required=True, help='Apellidos')

    def handle(self, *args, **options):
        email = options['email']
        password = options['password']
        nombres = options['nombres']
        apellidos = options['apellidos']

        # Crear roles base si no existen (idempotente)
        admin_role, _ = Rol.objects.get_or_create(nombre='Administrador')
        Rol.objects.get_or_create(nombre='Seguridad')
        Rol.objects.get_or_create(nombre='Propietario')
        Rol.objects.get_or_create(nombre='Inquilino')
        # Nota: En este proyecto no se usa rol 'CLIENTE'

        # Crear/actualizar usuario admin y asegurar Persona asociada
        user = Usuario.objects.filter(email=email).first()
        if not user:
            # Crear Persona asociada
            persona = Persona.objects.create(
                nombre=nombres,
                apellido=apellidos,
                documento_identidad=f'ADM-{email}',
                telefono='',
                email=email,
                tipo_persona='administrador'
            )
            user = Usuario.objects.create_user(
                email=email,
                password=password,
                persona=persona,
                is_staff=True,
                is_superuser=True,
                estado='ACTIVO',
            )
        else:
            if not user.persona:
                user.persona = Persona.objects.create(
                    nombre=nombres,
                    apellido=apellidos,
                    documento_identidad=f'ADM-{email}',
                    telefono='',
                    email=email,
                    tipo_persona='administrador'
                )
            else:
                user.persona.nombre = nombres
                user.persona.apellido = apellidos
                user.persona.email = email
                user.persona.tipo_persona = user.persona.tipo_persona or 'administrador'
                user.persona.save()

            user.is_staff = True
            user.is_superuser = True
            user.estado = 'ACTIVO'
            user.set_password(password)
            user.save()

        # Asignar rol Administrador (evitar duplicados)
        if not user.roles.filter(id=admin_role.id).exists():
            user.roles.add(admin_role)

        # Generar token JWT
        refresh = RefreshToken.for_user(user)
        access = str(refresh.access_token)

        self.stdout.write(self.style.SUCCESS(f'Usuario admin creado/actualizado: {email}'))
        self.stdout.write(self.style.SUCCESS(f'Access token: {access}'))
