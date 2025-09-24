"""
Comando para probar la seguridad de roles en el sistema.
Este comando simula intentos de acceso no autorizados para verificar que las protecciones funcionan.
"""
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from authz.models import Rol, Usuario, SolicitudRegistroPropietario
from django.test import RequestFactory
from rest_framework.test import force_authenticate
from authz.views import UsuarioViewSet
from authz.views_propietarios_panel import GestionarFamiliaresView
import json

User = get_user_model()

class Command(BaseCommand):
    help = 'Prueba la seguridad de roles del sistema'

    def add_arguments(self, parser):
        parser.add_argument(
            '--verbose',
            action='store_true',
            help='Mostrar output detallado',
        )

    def handle(self, *args, **options):
        self.verbose = options['verbose']
        
        self.stdout.write(self.style.SUCCESS('\n🔒 INICIANDO PRUEBAS DE SEGURIDAD DE ROLES\n'))
        
        # Crear usuarios de prueba
        self.setup_test_users()
        
        # Ejecutar pruebas
        self.test_admin_protection()
        self.test_propietario_protection()
        self.test_inquilino_protection()
        self.test_role_escalation()
        
        self.stdout.write(self.style.SUCCESS('\n✅ PRUEBAS DE SEGURIDAD COMPLETADAS\n'))

    def setup_test_users(self):
        """Crear usuarios de prueba con diferentes roles"""
        self.stdout.write('📋 Configurando usuarios de prueba...')
        
        # Crear roles si no existen
        admin_rol, _ = Rol.objects.get_or_create(nombre='Administrador')
        prop_rol, _ = Rol.objects.get_or_create(nombre='Propietario')
        inq_rol, _ = Rol.objects.get_or_create(nombre='Inquilino')
        
        # Usuario Administrador
        try:
            self.admin_user = Usuario.objects.get(email='admin_test@test.com')
        except Usuario.DoesNotExist:
            self.admin_user = Usuario.objects.create_user(
                email='admin_test@test.com',
                password='test123'
            )
            self.admin_user.roles.add(admin_rol)
        
        # Usuario Propietario (CON solicitud aprobada)
        try:
            self.propietario_user = Usuario.objects.get(email='propietario_test@test.com')
        except Usuario.DoesNotExist:
            self.propietario_user = Usuario.objects.create_user(
                email='propietario_test@test.com',
                password='test123'
            )
            self.propietario_user.roles.add(prop_rol)
            
            # Crear solicitud aprobada
            from datetime import date
            SolicitudRegistroPropietario.objects.get_or_create(
                usuario_creado=self.propietario_user,
                estado='APROBADA',
                defaults={
                    'nombres': 'Test',
                    'apellidos': 'Propietario',
                    'documento_identidad': '12345678',
                    'fecha_nacimiento': date(1990, 1, 1),
                    'email': 'propietario_test@test.com',
                    'telefono': '123456789',
                    'numero_casa': '101',
                }
            )
        
        # Usuario Propietario (SIN solicitud aprobada)
        try:
            self.propietario_no_aprobado = Usuario.objects.get(email='prop_no_aprobado@test.com')
        except Usuario.DoesNotExist:
            self.propietario_no_aprobado = Usuario.objects.create_user(
                email='prop_no_aprobado@test.com',
                password='test123'
            )
            self.propietario_no_aprobado.roles.add(prop_rol)
            # NO crear solicitud aprobada
        
        # Usuario Inquilino
        try:
            self.inquilino_user = Usuario.objects.get(email='inquilino_test@test.com')
        except Usuario.DoesNotExist:
            self.inquilino_user = Usuario.objects.create_user(
                email='inquilino_test@test.com',
                password='test123'
            )
            self.inquilino_user.roles.add(inq_rol)
        
        # Usuario sin roles
        try:
            self.no_role_user = Usuario.objects.get(email='no_role@test.com')
        except Usuario.DoesNotExist:
            self.no_role_user = Usuario.objects.create_user(
                email='no_role@test.com',
                password='test123'
            )
        
        self.factory = RequestFactory()

    def test_admin_protection(self):
        """Probar protección de endpoints administrativos"""
        self.stdout.write('\n🛡️ PROBANDO PROTECCIÓN DE ENDPOINTS ADMINISTRATIVOS:')
        
        # Endpoint: editar datos de usuario (solo admin)
        viewset = UsuarioViewSet()
        viewset.format_kwarg = None
        
        # Test 1: Admin puede acceder
        request = self.factory.put('/api/usuarios/1/editar-datos/')
        force_authenticate(request, user=self.admin_user)
        viewset.request = request
        viewset.kwargs = {'pk': 1}
        
        try:
            # Simular que existe el usuario
            viewset.get_object = lambda: self.propietario_user
            response = viewset.editar_datos_admin(request, pk=1)
            if response.status_code != 403:
                self.stdout.write(self.style.SUCCESS('  ✅ Admin puede editar usuarios'))
            else:
                self.stdout.write(self.style.ERROR('  ❌ Admin NO puede editar usuarios'))
        except Exception as e:
            self.stdout.write(self.style.WARNING(f'  ⚠️ Error en test admin: {e}'))
        
        # Test 2: Propietario NO puede acceder
        request = self.factory.put('/api/usuarios/1/editar-datos/')
        force_authenticate(request, user=self.propietario_user)
        viewset.request = request
        
        try:
            response = viewset.editar_datos_admin(request, pk=1)
            if response.status_code == 403:
                self.stdout.write(self.style.SUCCESS('  ✅ Propietario NO puede editar usuarios (correcto)'))
            else:
                self.stdout.write(self.style.ERROR('  ❌ VULNERABILIDAD: Propietario puede editar usuarios'))
        except Exception as e:
            self.stdout.write(self.style.WARNING(f'  ⚠️ Error en test propietario: {e}'))
        
        # Test 3: Inquilino NO puede acceder
        request = self.factory.put('/api/usuarios/1/editar-datos/')
        force_authenticate(request, user=self.inquilino_user)
        viewset.request = request
        
        try:
            response = viewset.editar_datos_admin(request, pk=1)
            if response.status_code == 403:
                self.stdout.write(self.style.SUCCESS('  ✅ Inquilino NO puede editar usuarios (correcto)'))
            else:
                self.stdout.write(self.style.ERROR('  ❌ VULNERABILIDAD: Inquilino puede editar usuarios'))
        except Exception as e:
            self.stdout.write(self.style.WARNING(f'  ⚠️ Error en test inquilino: {e}'))

    def test_propietario_protection(self):
        """Probar protección de endpoints de propietarios"""
        self.stdout.write('\n🏠 PROBANDO PROTECCIÓN DE ENDPOINTS DE PROPIETARIOS:')
        
        view = GestionarFamiliaresView()
        
        # Test 1: Propietario con solicitud aprobada puede acceder
        request = self.factory.get('/api/propietarios/familiares/')
        force_authenticate(request, user=self.propietario_user)
        
        try:
            response = view.get(request)
            if response.status_code != 403:
                self.stdout.write(self.style.SUCCESS('  ✅ Propietario aprobado puede gestionar familiares'))
            else:
                self.stdout.write(self.style.ERROR('  ❌ Propietario aprobado NO puede gestionar familiares'))
        except Exception as e:
            self.stdout.write(self.style.WARNING(f'  ⚠️ Error en test propietario: {e}'))
        
        # Test 2: Propietario SIN solicitud aprobada NO puede acceder
        request = self.factory.get('/api/propietarios/familiares/')
        force_authenticate(request, user=self.propietario_no_aprobado)
        
        try:
            response = view.get(request)
            if response.status_code == 403:
                self.stdout.write(self.style.SUCCESS('  ✅ Propietario NO aprobado no puede gestionar familiares (correcto)'))
            else:
                self.stdout.write(self.style.ERROR('  ❌ VULNERABILIDAD: Propietario NO aprobado puede gestionar familiares'))
        except Exception as e:
            self.stdout.write(self.style.WARNING(f'  ⚠️ Error en test propietario no aprobado: {e}'))
        
        # Test 3: Inquilino NO puede acceder
        request = self.factory.get('/api/propietarios/familiares/')
        force_authenticate(request, user=self.inquilino_user)
        
        try:
            response = view.get(request)
            if response.status_code == 403:
                self.stdout.write(self.style.SUCCESS('  ✅ Inquilino NO puede gestionar familiares (correcto)'))
            else:
                self.stdout.write(self.style.ERROR('  ❌ VULNERABILIDAD: Inquilino puede gestionar familiares'))
        except Exception as e:
            self.stdout.write(self.style.WARNING(f'  ⚠️ Error en test inquilino: {e}'))

    def test_inquilino_protection(self):
        """Probar que los inquilinos solo pueden acceder a sus endpoints"""
        self.stdout.write('\n🏘️ PROBANDO PROTECCIÓN DE ENDPOINTS DE INQUILINOS:')
        
        # Test: Inquilino NO puede acceder a endpoints de admin
        viewset = UsuarioViewSet()
        viewset.format_kwarg = None
        
        request = self.factory.get('/api/usuarios/clientes/')
        force_authenticate(request, user=self.inquilino_user)
        viewset.request = request
        
        try:
            response = viewset.listar_clientes(request)
            if response.status_code == 403:
                self.stdout.write(self.style.SUCCESS('  ✅ Inquilino NO puede listar clientes (correcto)'))
            else:
                self.stdout.write(self.style.ERROR('  ❌ VULNERABILIDAD: Inquilino puede listar clientes'))
        except Exception as e:
            self.stdout.write(self.style.WARNING(f'  ⚠️ Error en test inquilino: {e}'))

    def test_role_escalation(self):
        """Probar intentos de escalada de privilegios"""
        self.stdout.write('\n⚠️ PROBANDO INTENTOS DE ESCALADA DE PRIVILEGIOS:')
        
        # Test 1: Usuario sin roles intenta acceder a admin
        viewset = UsuarioViewSet()
        viewset.format_kwarg = None
        
        request = self.factory.get('/api/usuarios/clientes/')
        force_authenticate(request, user=self.no_role_user)
        viewset.request = request
        
        try:
            response = viewset.listar_clientes(request)
            if response.status_code == 403:
                self.stdout.write(self.style.SUCCESS('  ✅ Usuario sin roles NO puede acceder a admin (correcto)'))
            else:
                self.stdout.write(self.style.ERROR('  ❌ VULNERABILIDAD CRÍTICA: Usuario sin roles puede acceder a admin'))
        except Exception as e:
            self.stdout.write(self.style.WARNING(f'  ⚠️ Error en test sin roles: {e}'))
        
        # Test 2: Verificar auto-asignación de roles (VULNERABILIDAD CONOCIDA)
        self.stdout.write('\n🚨 VERIFICANDO VULNERABILIDAD DE AUTO-ASIGNACIÓN:')
        
        # Crear usuario temporal sin rol de propietario
        temp_user = Usuario.objects.create_user(
            email='temp_vulnerability_test@test.com',
            password='test123'
        )
        
        # Verificar que NO tiene rol de propietario
        has_role_before = temp_user.roles.filter(nombre='Propietario').exists()
        
        # Llamar al método que tiene la vulnerabilidad
        view = GestionarFamiliaresView()
        try:
            result = view.check_propietario_permission(temp_user)
            has_role_after = temp_user.roles.filter(nombre='Propietario').exists()
            
            if has_role_after and not has_role_before:
                self.stdout.write(self.style.ERROR('  ❌ VULNERABILIDAD CRÍTICA CONFIRMADA: Auto-asignación de roles activa'))
                self.stdout.write(self.style.ERROR('     📍 Ubicación: authz/views_propietarios_panel.py líneas 47-62'))
                self.stdout.write(self.style.ERROR('     🛠️ Solución: Remover la auto-asignación automática'))
            else:
                self.stdout.write(self.style.SUCCESS('  ✅ Auto-asignación de roles deshabilitada (correcto)'))
        except Exception as e:
            self.stdout.write(self.style.WARNING(f'  ⚠️ Error verificando auto-asignación: {e}'))
        
        # Limpiar usuario temporal
        temp_user.delete()

    def cleanup_test_users(self):
        """Limpiar usuarios de prueba"""
        test_emails = [
            'admin_test@test.com',
            'propietario_test@test.com', 
            'prop_no_aprobado@test.com',
            'inquilino_test@test.com',
            'no_role@test.com',
            'temp_vulnerability_test@test.com'
        ]
        
        Usuario.objects.filter(email__in=test_emails).delete()
        self.stdout.write('🧹 Usuarios de prueba eliminados')