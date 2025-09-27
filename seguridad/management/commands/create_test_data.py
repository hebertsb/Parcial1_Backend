"""
Management command para crear datos de prueba con el nuevo sistema authz
"""

from django.core.management.base import BaseCommand
from django.conf import settings
from seguridad.models import Copropietarios

try:
    from authz.models import Usuario, Rol
    User = Usuario  # Usar directamente el modelo Usuario de authz
except ImportError:
    Usuario = None
    Rol = None
    User = None


class Command(BaseCommand):
    help = 'Crea datos de prueba para el sistema de reconocimiento facial con authz'

    def handle(self, *args, **options):
        self.stdout.write('🏗️ Creando datos de prueba del sistema facial...')

        # Debug: Verificar usuarios existentes
        self.stdout.write('🔍 USUARIOS EXISTENTES EN DB:')
        if User is not None:
            for user in User.objects.all():
                self.stdout.write(f'  - {user.email} (ID: {user.id})')
        else:
            self.stdout.write('  (No hay modelo de usuario disponible)')

        # Verificar que el sistema authz esté disponible
        if User is None:
            self.stdout.write(
                self.style.ERROR('❌ Sistema de usuarios no disponible. Ejecuta primero: python manage.py crear_usuarios_facial')
            )
            return

        # Limpiar copropietarios existentes para evitar duplicados
        Copropietarios.objects.all().delete()
        self.stdout.write('🧹 Copropietarios anteriores eliminados')

        # Crear copropietarios y relacionarlos con usuarios del sistema
        copropietarios_data = [
            {
                'nombres': 'María Elena',
                'apellidos': 'González López',
                'numero_documento': '12345678',
                'tipo_documento': 'CC',
                'telefono': '+591-70000003',
                'email': 'maria.gonzalez@facial.com',
                'unidad_residencial': 'Apto 101',
                'tipo_residente': 'Propietario',
                'usuario_email': 'maria.gonzalez@facial.com'
            },
            {
                'nombres': 'Carlos Alberto',
                'apellidos': 'Rodríguez Pérez',
                'numero_documento': '87654321',
                'tipo_documento': 'CC',
                'telefono': '+591-70000004',
                'email': 'carlos.rodriguez@facial.com',
                'unidad_residencial': 'Apto 205',
                'tipo_residente': 'Inquilino',
                'usuario_email': 'carlos.rodriguez@facial.com'
            },
            {
                'nombres': 'Ana Sofía',
                'apellidos': 'Martínez Silva',
                'numero_documento': '11223344',
                'tipo_documento': 'CC',
                'telefono': '+591-71234567',
                'email': 'ana.martinez@residencial.com',
                'unidad_residencial': 'Casa 15',
                'tipo_residente': 'Propietario',
                'usuario_email': None  # Sin usuario del sistema
            },
            {
                'nombres': 'José Miguel',
                'apellidos': 'Hernández Torres',
                'numero_documento': '44332211',
                'tipo_documento': 'CC',
                'telefono': '+591-72345678',
                'email': 'jose.hernandez@residencial.com',
                'unidad_residencial': 'Apto 312',
                'tipo_residente': 'Inquilino',
                'usuario_email': None  # Sin usuario del sistema
            },
            {
                'nombres': 'Laura Patricia',
                'apellidos': 'Vásquez Morales',
                'numero_documento': '55667788',
                'tipo_documento': 'CC',
                'telefono': '+591-73456789',
                'email': 'laura.vasquez@residencial.com',
                'unidad_residencial': 'Apto 405',
                'tipo_residente': 'Familiar',
                'usuario_email': None
            }
        ]

        created_count = 0
        for coprop_data in copropietarios_data:
            # Por ahora, crear copropietarios sin vincular usuarios del sistema
            # hasta resolver el problema de integridad referencial
            usuario_sistema = None
            
            # Crear o actualizar copropietario
            copropietario, created = Copropietarios.objects.get_or_create(
                numero_documento=coprop_data['numero_documento'],
                defaults={
                    'nombres': coprop_data['nombres'],
                    'apellidos': coprop_data['apellidos'],
                    'tipo_documento': coprop_data['tipo_documento'],
                    'telefono': coprop_data['telefono'],
                    'email': coprop_data['email'],
                    'unidad_residencial': coprop_data['unidad_residencial'],
                    'tipo_residente': coprop_data['tipo_residente'],
                    'usuario_sistema': usuario_sistema
                }
            )

            if created:
                created_count += 1
                status_usuario = f" (👤 {usuario_sistema.email})" if usuario_sistema else " (Sin usuario sistema)"
                self.stdout.write(
                    f'✅ Copropietario creado: {copropietario.nombre_completo} - {copropietario.unidad_residencial}{status_usuario}'
                )
            else:
                # Actualizar usuario_sistema si cambió
                if copropietario.usuario_sistema != usuario_sistema:
                    copropietario.usuario_sistema = usuario_sistema
                    copropietario.save()
                    self.stdout.write(
                        f'🔄 Copropietario actualizado: {copropietario.nombre_completo}'
                    )

        self.stdout.write(
            self.style.SUCCESS(f'\n✅ Datos de prueba creados/actualizados exitosamente!')
        )
        
        self.stdout.write('\n📋 RESUMEN:')
        self.stdout.write(f'- Copropietarios totales: {Copropietarios.objects.count()}')
        self.stdout.write(f'- Con usuario sistema: {Copropietarios.objects.filter(usuario_sistema__isnull=False).count()}')
        self.stdout.write(f'- Sin usuario sistema: {Copropietarios.objects.filter(usuario_sistema__isnull=True).count()}')
        
        self.stdout.write('\n🏠 COPROPIETARIOS DISPONIBLES:')
        for coprop in Copropietarios.objects.all():
            usuario_info = f" (👤 {coprop.usuario_sistema.email})" if coprop.usuario_sistema else ""
            self.stdout.write(f'  - ID {coprop.id}: {coprop.nombre_completo} ({coprop.unidad_residencial}) - {coprop.tipo_residente}{usuario_info}')
        
        self.stdout.write('\n🔗 PRÓXIMOS PASOS:')
        self.stdout.write('1. 🖥️  Acceder al admin: http://127.0.0.1:8000/admin/')
        self.stdout.write('2. 📚 Ver API docs: http://127.0.0.1:8000/api/docs/')
        self.stdout.write('3. 🔐 Probar login: POST /api/auth/login/')
        self.stdout.write('4. 📸 Enrolar rostros: POST /api/faces/enroll/')
        
        self.stdout.write('\n🎯 ROLES DISPONIBLES:')
        if Rol:
            for rol in Rol.objects.all():
                # Si la relación usuarios no existe, solo muestra el nombre del rol
                self.stdout.write(f'  - {rol.nombre}')
        
        self.stdout.write('\n🚀 ¡Sistema listo para pruebas de reconocimiento facial!')
