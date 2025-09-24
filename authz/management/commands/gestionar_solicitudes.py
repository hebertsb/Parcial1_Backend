"""
Comando para gestionar solicitudes de propietarios desde consola
"""
from typing import cast
from django.core.management.base import BaseCommand
from django.utils import timezone
from authz.models import SolicitudRegistroPropietario, Usuario
from authz.email_service import EmailService

class Command(BaseCommand):
    help = 'Gestiona solicitudes de registro de propietarios'

    def add_arguments(self, parser):
        parser.add_argument(
            '--accion',
            type=str,
            default='listar',
            choices=['listar', 'aprobar', 'rechazar', 'detalle'],
            help='Acción a realizar'
        )
        parser.add_argument(
            '--solicitud-id',
            type=int,
            help='ID de la solicitud para aprobar/rechazar/detalle'
        )
        parser.add_argument(
            '--motivo',
            type=str,
            default='',
            help='Motivo del rechazo'
        )
        parser.add_argument(
            '--observaciones',
            type=str,
            default='',
            help='Observaciones para la aprobación'
        )

    def handle(self, *args, **options):
        accion = options['accion']
        
        if accion == 'listar':
            self.listar_solicitudes()
        elif accion == 'detalle':
            if not options['solicitud_id']:
                self.stdout.write(self.style.ERROR('Debe especificar --solicitud-id'))
                return
            self.mostrar_detalle(options['solicitud_id'])
        elif accion == 'aprobar':
            if not options['solicitud_id']:
                self.stdout.write(self.style.ERROR('Debe especificar --solicitud-id'))
                return
            self.aprobar_solicitud(options['solicitud_id'], options['observaciones'])
        elif accion == 'rechazar':
            if not options['solicitud_id']:
                self.stdout.write(self.style.ERROR('Debe especificar --solicitud-id'))
                return
            if not options['motivo']:
                self.stdout.write(self.style.ERROR('Debe especificar --motivo para rechazar'))
                return
            self.rechazar_solicitud(options['solicitud_id'], options['motivo'])

    def listar_solicitudes(self):
        self.stdout.write(self.style.SUCCESS('📋 SOLICITUDES DE REGISTRO DE PROPIETARIOS'))
        self.stdout.write('=' * 70)
        
        # Solicitudes pendientes
        pendientes = SolicitudRegistroPropietario.objects.filter(estado='PENDIENTE').order_by('-created_at')
        
        if pendientes.count() == 0:
            self.stdout.write(self.style.WARNING('✅ No hay solicitudes pendientes de revisión'))
        else:
            self.stdout.write(self.style.WARNING(f'⏳ PENDIENTES ({pendientes.count()}):'))
            for sol in pendientes:
                solicitud = cast(SolicitudRegistroPropietario, sol)
                self.stdout.write(f'  🆔 ID: {solicitud.pk}')
                self.stdout.write(f'  👤 {solicitud.nombres} {solicitud.apellidos}')
                self.stdout.write(f'  📧 {solicitud.email}')
                self.stdout.write(f'  🏠 {solicitud.numero_casa}')
                self.stdout.write(f'  📅 {solicitud.created_at.strftime("%d/%m/%Y %H:%M")}')
                self.stdout.write(f'  🎫 Token: {solicitud.token_seguimiento}')
                self.stdout.write('  ' + '-' * 50)
        
        # Resumen por estado
        self.stdout.write('\n📊 RESUMEN POR ESTADO:')
        for estado, descripcion in SolicitudRegistroPropietario.ESTADO_CHOICES:
            count = SolicitudRegistroPropietario.objects.filter(estado=estado).count()
            if count > 0:
                emoji = {'PENDIENTE': '⏳', 'APROBADA': '✅', 'RECHAZADA': '❌'}.get(estado, '📋')
                self.stdout.write(f'  {emoji} {descripcion}: {count}')

    def mostrar_detalle(self, solicitud_id):
        try:
            solicitud = cast(SolicitudRegistroPropietario, SolicitudRegistroPropietario.objects.get(id=solicitud_id))
            
            self.stdout.write(self.style.SUCCESS(f'📄 DETALLE DE SOLICITUD #{solicitud_id}'))
            self.stdout.write('=' * 50)
            
            self.stdout.write(f'👤 Nombre: {solicitud.nombres} {solicitud.apellidos}')
            self.stdout.write(f'📄 Documento: {solicitud.documento_identidad}')
            self.stdout.write(f'📧 Email: {solicitud.email}')
            self.stdout.write(f'📱 Teléfono: {solicitud.telefono}')
            self.stdout.write(f'🎂 Fecha Nacimiento: {solicitud.fecha_nacimiento}')
            self.stdout.write(f'🏠 Vivienda: {solicitud.numero_casa}')
            estado_display = dict(SolicitudRegistroPropietario.ESTADO_CHOICES).get(solicitud.estado, solicitud.estado)
            self.stdout.write(f'📊 Estado: {estado_display}')
            self.stdout.write(f'🎫 Token: {solicitud.token_seguimiento}')
            self.stdout.write(f'📅 Creada: {solicitud.created_at.strftime("%d/%m/%Y %H:%M")}')
            
            if solicitud.vivienda_validada:
                self.stdout.write(f'✅ Vivienda validada: {solicitud.vivienda_validada}')
            else:
                self.stdout.write('❌ Vivienda no validada')
            
            if solicitud.estado == 'APROBADA':
                self.stdout.write(f'✅ Aprobada: {solicitud.fecha_aprobacion}')
                if solicitud.usuario_creado:
                    self.stdout.write(f'👤 Usuario creado: {solicitud.usuario_creado.email}')
                    
            elif solicitud.estado == 'RECHAZADA':
                self.stdout.write(f'❌ Rechazada: {solicitud.fecha_rechazo}')
                if solicitud.motivo_rechazo:
                    self.stdout.write(f'📝 Motivo: {solicitud.motivo_rechazo}')
                    
        except SolicitudRegistroPropietario.DoesNotExist:
            self.stdout.write(self.style.ERROR(f'❌ No existe solicitud con ID {solicitud_id}'))

    def aprobar_solicitud(self, solicitud_id, observaciones):
        try:
            solicitud = SolicitudRegistroPropietario.objects.get(id=solicitud_id)
            
            if solicitud.estado != 'PENDIENTE':
                self.stdout.write(self.style.ERROR(f'❌ La solicitud ya fue procesada. Estado: {solicitud.estado}'))
                return
            
            # Obtener un admin para realizar la aprobación
            admin = Usuario.objects.filter(roles__nombre='Administrador').first()
            if not admin:
                self.stdout.write(self.style.ERROR('❌ No hay administradores en el sistema'))
                return
            
            self.stdout.write(f'🔄 Aprobando solicitud de {solicitud.nombres} {solicitud.apellidos}...')
            
            # Aprobar solicitud
            usuario_creado = solicitud.aprobar_solicitud(admin)
            
            # Agregar observaciones si se proporcionaron
            if observaciones:
                solicitud.comentarios_admin = observaciones
                solicitud.save()
            
            self.stdout.write(self.style.SUCCESS(f'✅ Solicitud aprobada exitosamente!'))
            self.stdout.write(f'👤 Usuario creado: {usuario_creado.email}')
            self.stdout.write(f'🔑 Contraseña temporal: temporal123')
            self.stdout.write(f'📧 Email de notificación enviado a: {solicitud.email}')
            
        except SolicitudRegistroPropietario.DoesNotExist:
            self.stdout.write(self.style.ERROR(f'❌ No existe solicitud con ID {solicitud_id}'))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'❌ Error aprobando solicitud: {e}'))

    def rechazar_solicitud(self, solicitud_id, motivo):
        try:
            solicitud = SolicitudRegistroPropietario.objects.get(id=solicitud_id)
            
            if solicitud.estado != 'PENDIENTE':
                self.stdout.write(self.style.ERROR(f'❌ La solicitud ya fue procesada. Estado: {solicitud.estado}'))
                return
            
            self.stdout.write(f'🔄 Rechazando solicitud de {solicitud.nombres} {solicitud.apellidos}...')
            
            # Rechazar solicitud
            solicitud.estado = 'RECHAZADA'
            solicitud.motivo_rechazo = motivo
            solicitud.fecha_rechazo = timezone.now()
            solicitud.save()
            
            # Enviar notificación de rechazo
            EmailService.enviar_solicitud_rechazada(solicitud)
            
            self.stdout.write(self.style.SUCCESS(f'✅ Solicitud rechazada exitosamente!'))
            self.stdout.write(f'📝 Motivo: {motivo}')
            self.stdout.write(f'📧 Email de notificación enviado a: {solicitud.email}')
            
        except SolicitudRegistroPropietario.DoesNotExist:
            self.stdout.write(self.style.ERROR(f'❌ No existe solicitud con ID {solicitud_id}'))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'❌ Error rechazando solicitud: {e}'))