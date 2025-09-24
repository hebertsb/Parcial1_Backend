from django.core.management.base import BaseCommand
from authz.models import Usuario, Rol, Persona
from rest_framework_simplejwt.tokens import RefreshToken
from datetime import date


class Command(BaseCommand):
    help = 'Crea usuarios y roles del sistema de reconocimiento facial integrado con Persona'

    def handle(self, *args, **options):
        self.stdout.write('🚀 Creando roles, personas y usuarios del sistema facial...')

        # Crear roles del sistema facial
        roles_nombres = ['Administrador', 'Seguridad', 'Propietario', 'Inquilino']

        created_roles = []
        for rol_nombre in roles_nombres:
            rol, created = Rol.objects.get_or_create(
                nombre=rol_nombre,
                defaults={
                    'descripcion': f'Rol de {rol_nombre} del sistema',
                    'activo': True
                }
            )
            if created:
                self.stdout.write(f'✅ Rol creado: {rol.nombre}')
                created_roles.append(rol)
            else:
                self.stdout.write(f'ℹ️  Rol existente: {rol.nombre}')

        # Datos de personas y usuarios del sistema
        usuarios_data = [
            {
                'email': 'admin@facial.com',
                'persona_data': {
                    'nombre': 'Sistema',
                    'apellido': 'Administrador',
                    'documento_identidad': 'ADM001',
                    'telefono': '+591-70000001',
                    'email': 'admin@facial.com',
                    'fecha_nacimiento': date(1980, 1, 1),
                    'tipo_persona': 'administrador'
                },
                'password': 'admin123',
                'rol': 'Administrador',
                'is_staff': True,
                'is_superuser': True
            },
            {
                'email': 'seguridad@facial.com',
                'persona_data': {
                    'nombre': 'Juan Carlos',
                    'apellido': 'Seguridad',
                    'documento_identidad': 'SEG001',
                    'telefono': '+591-70000002',
                    'email': 'seguridad@facial.com',
                    'fecha_nacimiento': date(1985, 5, 15),
                    'tipo_persona': 'seguridad'
                },
                'password': 'seguridad123',
                'rol': 'Seguridad',
                'is_staff': False,
                'is_superuser': False
            },
            {
                'email': 'maria.gonzalez@facial.com',
                'persona_data': {
                    'nombre': 'María Elena',
                    'apellido': 'González López',
                    'documento_identidad': '12345678',
                    'telefono': '+591-70000003',
                    'email': 'maria.gonzalez@facial.com',
                    'fecha_nacimiento': date(1990, 3, 20),
                    'tipo_persona': 'propietario'
                },
                'password': 'propietario123',
                'rol': 'Propietario',
                'is_staff': False,
                'is_superuser': False
            },
            {
                'email': 'carlos.rodriguez@facial.com',
                'persona_data': {
                    'nombre': 'Carlos Alberto',
                    'apellido': 'Rodríguez Pérez',
                    'documento_identidad': '87654321',
                    'telefono': '+591-70000004',
                    'email': 'carlos.rodriguez@facial.com',
                    'fecha_nacimiento': date(1988, 8, 10),
                    'tipo_persona': 'inquilino'
                },
                'password': 'inquilino123',
                'rol': 'Inquilino',
                'is_staff': False,
                'is_superuser': False
            }
        ]

        created_users = []
        for user_data in usuarios_data:
            # Obtener el rol
            try:
                rol = Rol.objects.get(nombre=user_data['rol'])
            except Rol.DoesNotExist:
                self.stdout.write(f'❌ Error: Rol {user_data["rol"]} no encontrado')
                continue

            # Crear o actualizar persona
            persona_data = user_data['persona_data']
            persona, persona_created = Persona.objects.get_or_create(
                documento_identidad=persona_data['documento_identidad'],
                defaults=persona_data
            )
            
            if persona_created:
                self.stdout.write(f'✅ Persona creada: {persona.nombre_completo}')
            else:
                # Actualizar datos de persona existente
                for key, value in persona_data.items():
                    setattr(persona, key, value)
                persona.save()
                self.stdout.write(f'🔄 Persona actualizada: {persona.nombre_completo}')

            # Crear o actualizar usuario
            user, created = Usuario.objects.get_or_create(
                email=user_data['email'],
                defaults={
                    'persona': persona,
                    'is_staff': user_data.get('is_staff', False),
                    'is_superuser': user_data.get('is_superuser', False),
                    'estado': 'ACTIVO'
                }
            )

            # Establecer contraseña
            user.set_password(user_data['password'])
            
            # Actualizar campos si el usuario ya existía
            if not created:
                user.persona = persona
                user.is_staff = user_data.get('is_staff', False)
                user.is_superuser = user_data.get('is_superuser', False)
                user.estado = 'ACTIVO'
            
            user.save()

            # Asignar rol
            user.roles.clear()  # Limpiar roles anteriores
            user.roles.add(rol)

            if created:
                self.stdout.write(f'✅ Usuario creado: {user.email} ({rol.nombre})')
                created_users.append(user)
            else:
                self.stdout.write(f'🔄 Usuario actualizado: {user.email} ({rol.nombre})')

        # Mostrar resumen
        self.stdout.write('\n📊 RESUMEN:')
        self.stdout.write(f'- Roles totales: {Rol.objects.count()}')
        self.stdout.write(f'- Personas totales: {Persona.objects.count()}')
        self.stdout.write(f'- Usuarios totales: {Usuario.objects.count()}')
        
        self.stdout.write('\n🔑 CREDENCIALES DE ACCESO:')
        for user_data in usuarios_data:
            rol_nombre = user_data['rol']
            self.stdout.write(f'👤 {rol_nombre}: {user_data["email"]} / {user_data["password"]}')

        self.stdout.write('\n🌐 ENDPOINTS DE PRUEBA:')
        self.stdout.write('📍 Login: POST /api/auth/login/')
        self.stdout.write('📍 Admin Panel: /admin/')
        self.stdout.write('📍 API Docs: /api/docs/')
        
        # Generar token de ejemplo para el admin
        try:
            admin_user = Usuario.objects.get(email='admin@facial.com')
            refresh = RefreshToken.for_user(admin_user)
            access_token = str(refresh.access_token)
            self.stdout.write(f'\n🔐 Token de ejemplo (Admin): {access_token[:50]}...')
        except Usuario.DoesNotExist:
            pass

        self.stdout.write('\n✅ Sistema de usuarios y personas configurado correctamente!')