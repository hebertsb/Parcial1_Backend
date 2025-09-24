"""
Comando para probar el sistema de emails
"""
from django.core.management.base import BaseCommand
from django.utils import timezone
from authz.models import SolicitudRegistroPropietario, Usuario
from authz.email_service import EmailService
import uuid

class Command(BaseCommand):
    help = 'Prueba el sistema de emails del condominio'

    def add_arguments(self, parser):
        parser.add_argument(
            '--test-type',
            type=str,
            default='all',
            choices=['all', 'config', 'nueva-solicitud', 'confirmacion', 'aprobacion', 'rechazo'],
            help='Tipo de prueba a ejecutar'
        )
        parser.add_argument(
            '--email',
            type=str,
            default='test@example.com',
            help='Email de prueba para los templates'
        )

    def handle(self, *args, **options):
        test_type = options['test_type']
        test_email = options['email']
        
        self.stdout.write(self.style.SUCCESS('🧪 Iniciando pruebas del sistema de emails...'))
        
        if test_type in ['all', 'config']:
            self.test_email_configuration()
        
        if test_type in ['all', 'nueva-solicitud']:
            self.test_nueva_solicitud_admin()
        
        if test_type in ['all', 'confirmacion']:
            self.test_confirmacion_solicitud(test_email)
        
        if test_type in ['all', 'aprobacion']:
            self.test_solicitud_aprobada(test_email)
        
        if test_type in ['all', 'rechazo']:
            self.test_solicitud_rechazada(test_email)
        
        self.stdout.write(self.style.SUCCESS('✅ Pruebas completadas!'))

    def test_email_configuration(self):
        self.stdout.write('📧 Probando configuración de email...')
        
        try:
            results = EmailService.test_email_configuration()
            
            if results['configuration_ok']:
                self.stdout.write(self.style.SUCCESS('  ✅ Configuración de email OK'))
            else:
                self.stdout.write(self.style.ERROR('  ❌ Configuración de email con problemas'))
            
            if results['send_test_ok']:
                self.stdout.write(self.style.SUCCESS('  ✅ Envío de email de prueba OK'))
            else:
                self.stdout.write(self.style.WARNING('  ⚠️  Envío de email de prueba falló'))
                
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'  ❌ Error en configuración: {e}'))

    def test_nueva_solicitud_admin(self):
        self.stdout.write('📬 Probando notificación a administradores...')
        
        try:
            # Crear solicitud de prueba
            solicitud = self.create_test_solicitud()
            
            # Enviar notificación
            success = EmailService.enviar_nueva_solicitud_admin(solicitud, familiares_count=2)
            
            if success:
                self.stdout.write(self.style.SUCCESS('  ✅ Notificación a administradores enviada'))
            else:
                self.stdout.write(self.style.ERROR('  ❌ Error enviando notificación a administradores'))
                
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'  ❌ Error: {e}'))

    def test_confirmacion_solicitud(self, test_email):
        self.stdout.write('📩 Probando confirmación de solicitud...')
        
        try:
            # Crear solicitud de prueba
            solicitud = self.create_test_solicitud(email=test_email)
            
            # Enviar confirmación
            success = EmailService.enviar_confirmacion_solicitud(solicitud, familiares_count=1)
            
            if success:
                self.stdout.write(self.style.SUCCESS('  ✅ Confirmación de solicitud enviada'))
            else:
                self.stdout.write(self.style.ERROR('  ❌ Error enviando confirmación'))
                
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'  ❌ Error: {e}'))

    def test_solicitud_aprobada(self, test_email):
        self.stdout.write('🎉 Probando notificación de aprobación...')
        
        try:
            # Crear solicitud y usuario de prueba
            solicitud = self.create_test_solicitud(email=test_email, estado='APROBADA')
            usuario = self.create_test_usuario(email=test_email)
            
            # Enviar notificación de aprobación
            success = EmailService.enviar_solicitud_aprobada(solicitud, usuario)
            
            if success:
                self.stdout.write(self.style.SUCCESS('  ✅ Notificación de aprobación enviada'))
            else:
                self.stdout.write(self.style.ERROR('  ❌ Error enviando notificación de aprobación'))
                
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'  ❌ Error: {e}'))

    def test_solicitud_rechazada(self, test_email):
        self.stdout.write('❌ Probando notificación de rechazo...')
        
        try:
            # Crear solicitud de prueba
            solicitud = self.create_test_solicitud(
                email=test_email, 
                estado='RECHAZADA',
                motivo_rechazo='Documentación incompleta para fines de prueba'
            )
            
            # Enviar notificación de rechazo
            success = EmailService.enviar_solicitud_rechazada(solicitud)
            
            if success:
                self.stdout.write(self.style.SUCCESS('  ✅ Notificación de rechazo enviada'))
            else:
                self.stdout.write(self.style.ERROR('  ❌ Error enviando notificación de rechazo'))
                
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'  ❌ Error: {e}'))

    def create_test_solicitud(self, email='test@example.com', estado='PENDIENTE', motivo_rechazo=''):
        """Crea una solicitud de prueba temporal"""
        from datetime import date
        
        solicitud = SolicitudRegistroPropietario(
            nombres='Juan Carlos',
            apellidos='Pérez García',
            documento_identidad='12345678',
            fecha_nacimiento=date(1985, 3, 15),
            email=email,
            telefono='591-70123456',
            numero_casa='A-101',
            estado=estado,
            token_seguimiento=str(uuid.uuid4())[:8].upper(),
            created_at=timezone.now(),
            motivo_rechazo=motivo_rechazo,
            fecha_rechazo=timezone.now() if estado == 'RECHAZADA' else None,
            fecha_aprobacion=timezone.now() if estado == 'APROBADA' else None,
        )
        # No guardamos en BD, solo para pruebas
        return solicitud

    def create_test_usuario(self, email='test@example.com'):
        """Crea un usuario de prueba temporal"""
        class TestUser:
            def __init__(self, email):
                self.email = email
                self.id = 999
        
        return TestUser(email)