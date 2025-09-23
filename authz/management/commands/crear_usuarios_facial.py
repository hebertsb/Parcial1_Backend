from django.core.management.base import BaseCommand
from authz.models import Usuario, Rol
from rest_framework_simplejwt.tokens import RefreshToken


class Command(BaseCommand):
    help = 'Crea usuarios y roles del sistema de reconocimiento facial'

    def handle(self, *args, **options):
        self.stdout.write('🚀 Creando roles y usuarios del sistema facial...')

        # Crear roles del sistema facial
        roles_nombres = ['Administrador', 'Seguridad', 'Propietario', 'Inquilino']

        created_roles = []
        for rol_nombre in roles_nombres:
            rol, created = Rol.objects.get_or_create(nombre=rol_nombre)
            if created:
                self.stdout.write(f'✅ Rol creado: {rol.nombre}')
                created_roles.append(rol)
            else:
                self.stdout.write(f'ℹ️  Rol existente: {rol.nombre}')

        # Crear usuarios del sistema
        usuarios_data = [
            {
                'email': 'admin@facial.com',
                'nombres': 'Sistema',
                'apellidos': 'Administrador',
                'password': 'admin123',
                'telefono': '+591-70000001',
                'rol': 'Administrador',
                'is_staff': True,
                'is_superuser': True
            },
            {
                'email': 'seguridad@facial.com',
                'nombres': 'Juan Carlos',
                'apellidos': 'Seguridad',
                'password': 'seguridad123',
                'telefono': '+591-70000002',
                'rol': 'Seguridad',
                'is_staff': False,
                'is_superuser': False
            },
            {
                'email': 'maria.gonzalez@facial.com',
                'nombres': 'María Elena',
                'apellidos': 'González López',
                'password': 'propietario123',
                'telefono': '+591-70000003',
                'rol': 'Propietario',
                'documento_identidad': '12345678',
                'is_staff': False,
                'is_superuser': False
            },
            {
                'email': 'carlos.rodriguez@facial.com',
                'nombres': 'Carlos Alberto',
                'apellidos': 'Rodríguez Pérez',
                'password': 'inquilino123',
                'telefono': '+591-70000004',
                'rol': 'Inquilino',
                'documento_identidad': '87654321',
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

            # Crear o actualizar usuario
            user, created = Usuario.objects.get_or_create(
                email=user_data['email'],
                defaults={
                    'nombres': user_data['nombres'],
                    'apellidos': user_data['apellidos'],
                    'telefono': user_data.get('telefono'),
                    'documento_identidad': user_data.get('documento_identidad'),
                    'is_staff': user_data.get('is_staff', False),
                    'is_superuser': user_data.get('is_superuser', False),
                    'estado': 'ACTIVO'
                }
            )

            # Establecer contraseña
            user.set_password(user_data['password'])
            
            # Actualizar campos si el usuario ya existía
            if not created:
                user.nombres = user_data['nombres']
                user.apellidos = user_data['apellidos']
                user.telefono = user_data.get('telefono')
                user.documento_identidad = user_data.get('documento_identidad')
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

        self.stdout.write('\n✅ Sistema de usuarios configurado correctamente!')