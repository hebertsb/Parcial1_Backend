"""
Comando para aprobar solicitudes de registro desde la línea de comandos
"""
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction
from authz.models import SolicitudRegistroPropietario, Usuario

class Command(BaseCommand):
    help = 'Aprueba una solicitud de registro de propietario'

    def add_arguments(self, parser):
        parser.add_argument(
            'solicitud_id',
            type=int,
            help='ID de la solicitud a aprobar'
        )
        parser.add_argument(
            '--admin-user',
            type=str,
            help='Email del usuario administrador que aprueba'
        )
        parser.add_argument(
            '--observaciones',
            type=str,
            default='Aprobado por comando de administración',
            help='Observaciones de la aprobación'
        )

    @transaction.atomic
    def handle(self, *args, **options):
        solicitud_id = options['solicitud_id']
        admin_email = options['admin_user']
        observaciones = options['observaciones']
        
        try:
            # Buscar la solicitud
            solicitud = SolicitudRegistroPropietario.objects.get(id=solicitud_id)
        except SolicitudRegistroPropietario.DoesNotExist:
            raise CommandError(f'No existe una solicitud con ID {solicitud_id}')
        
        # Verificar estado
        if solicitud.estado != 'PENDIENTE':
            raise CommandError(
                f'La solicitud {solicitud_id} ya fue procesada. Estado actual: {solicitud.estado}'
            )
        
        # Buscar el administrador si se proporcionó
        admin_user = None
        if admin_email:
            try:
                admin_user = Usuario.objects.get(
                    email=admin_email,
                    roles__nombre__in=['Administrador', 'ADMIN']
                )
            except Usuario.DoesNotExist:
                self.stdout.write(
                    self.style.WARNING(
                        f'Usuario administrador "{admin_email}" no encontrado. '
                        'Procediendo sin asignar administrador.'
                    )
                )
        
        try:
            # Aprobar la solicitud usando el método correcto
            usuario_creado = solicitud.aprobar_solicitud(admin_user)
            
            # Agregar observaciones si se proporcionaron
            if observaciones:
                solicitud.observaciones = observaciones
                solicitud.save()
            
            self.stdout.write(
                self.style.SUCCESS(
                    f'✓ Solicitud {solicitud_id} aprobada exitosamente:\n'
                    f'  - Solicitante: {solicitud.nombres} {solicitud.apellidos}\n'
                    f'  - Vivienda: {solicitud.numero_casa}\n'
                    f'  - Usuario creado: {usuario_creado.email}\n'
                    f'  - Rol asignado: Propietario\n'
                    f'  - Estado: {solicitud.estado}'
                )
            )
                
        except Exception as e:
            raise CommandError(f'Error inesperado al aprobar solicitud: {str(e)}')
