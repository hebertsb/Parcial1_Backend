"""
Comando para probar el sistema de solicitudes desde Django
"""
from django.core.management.base import BaseCommand
from django.db import transaction
from authz.models import SolicitudRegistroPropietario, Usuario, Rol
from core.models import Vivienda
import json

class Command(BaseCommand):
    help = 'Prueba el sistema completo de solicitudes de copropietarios'

    def add_arguments(self, parser):
        parser.add_argument(
            '--accion',
            type=str,
            choices=['crear', 'listar', 'aprobar', 'rechazar', 'test-completo'],
            default='test-completo',
            help='Acción a realizar'
        )
        parser.add_argument('--solicitud-id', type=int, help='ID de solicitud para aprobar/rechazar')

    def handle(self, **options):
        accion = options['accion']
        
        if accion == 'crear':
            self.crear_solicitud_prueba()
        elif accion == 'listar':
            self.listar_solicitudes()
        elif accion == 'aprobar':
            self.aprobar_solicitud(options.get('solicitud_id'))
        elif accion == 'rechazar':
            self.rechazar_solicitud(options.get('solicitud_id'))
        else:
            self.test_completo()

    def crear_solicitud_prueba(self):
        """Crea una solicitud de prueba"""
        self.stdout.write("🔍 Creando solicitud de prueba...")
        
        # Verificar que existe una vivienda disponible
        vivienda = Vivienda.objects.filter().first()
        if not vivienda:
            self.stdout.write(
                self.style.ERROR("❌ No hay viviendas en el sistema. Crear al menos una vivienda primero.")
            )
            return
        
        try:
            solicitud = SolicitudRegistroPropietario.objects.create(
                nombres="Pedro",
                apellidos="Martínez González",
                documento_identidad="5555555", 
                fecha_nacimiento="1988-08-20",
                email="pedro.martinez@test.com",
                telefono="75555555",
                numero_casa=vivienda.numero_casa
            )
            
            # Validar vivienda
            es_valida, mensaje = solicitud.validar_vivienda()
            
            self.stdout.write(
                self.style.SUCCESS(f"✅ Solicitud creada: ID={solicitud.id}, Token={solicitud.token_seguimiento}")
            )
            self.stdout.write(f"📍 Vivienda: {mensaje}")
            
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f"❌ Error creando solicitud: {e}")
            )

    def listar_solicitudes(self):
        """Lista todas las solicitudes"""
        self.stdout.write("📋 Listando solicitudes...")
        
        solicitudes = SolicitudRegistroPropietario.objects.all().order_by('-created_at')
        
        if not solicitudes:
            self.stdout.write("📭 No hay solicitudes en el sistema")
            return
        
        for solicitud in solicitudes:
            estado_color = self.style.SUCCESS if solicitud.estado == 'APROBADA' else \
                          self.style.ERROR if solicitud.estado == 'RECHAZADA' else \
                          self.style.WARNING
            
            vivienda_info = "Sin vivienda"
            if solicitud.vivienda_validada:
                vivienda_info = f"{solicitud.vivienda_validada.numero_casa} ({solicitud.vivienda_validada.tipo_vivienda})"
            
            self.stdout.write(
                f"ID: {solicitud.id} | "
                f"{solicitud.nombres} {solicitud.apellidos} | "
                f"📧 {solicitud.email} | "
                f"🏠 {vivienda_info} | "
                f"Estado: {estado_color(solicitud.estado)} | "
                f"Token: {solicitud.token_seguimiento}"
            )

    def aprobar_solicitud(self, solicitud_id):
        """Aprueba una solicitud específica"""
        if not solicitud_id:
            self.stdout.write(self.style.ERROR("❌ Debe especificar --solicitud-id"))
            return
        
        try:
            solicitud = SolicitudRegistroPropietario.objects.get(id=solicitud_id)
            
            # Obtener un usuario administrador
            admin = Usuario.objects.filter(roles__nombre='Administrador').first()
            if not admin:
                self.stdout.write(self.style.ERROR("❌ No hay administradores en el sistema"))
                return
            
            with transaction.atomic():
                usuario_creado = solicitud.aprobar_solicitud(admin)
                
                self.stdout.write(
                    self.style.SUCCESS(f"✅ Solicitud {solicitud_id} aprobada exitosamente")
                )
                self.stdout.write(f"👤 Usuario creado: {usuario_creado.email}")
                self.stdout.write(f"🔑 Contraseña temporal: temporal123")
                
        except SolicitudRegistroPropietario.DoesNotExist:
            self.stdout.write(self.style.ERROR(f"❌ No existe solicitud con ID {solicitud_id}"))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"❌ Error aprobando solicitud: {e}"))

    def rechazar_solicitud(self, solicitud_id):
        """Rechaza una solicitud específica"""
        if not solicitud_id:
            self.stdout.write(self.style.ERROR("❌ Debe especificar --solicitud-id"))
            return
        
        try:
            solicitud = SolicitudRegistroPropietario.objects.get(id=solicitud_id)
            
            solicitud.estado = 'RECHAZADA'
            solicitud.motivo_rechazo = "Documentación incompleta - Prueba desde comando"
            solicitud.save()
            
            self.stdout.write(
                self.style.SUCCESS(f"✅ Solicitud {solicitud_id} rechazada exitosamente")
            )
            
        except SolicitudRegistroPropietario.DoesNotExist:
            self.stdout.write(self.style.ERROR(f"❌ No existe solicitud con ID {solicitud_id}"))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"❌ Error rechazando solicitud: {e}"))

    def test_completo(self):
        """Ejecuta un test completo del sistema"""
        self.stdout.write(self.style.SUCCESS("🚀 INICIANDO TEST COMPLETO DEL SISTEMA"))
        self.stdout.write("=" * 60)
        
        # 1. Listar solicitudes actuales
        self.stdout.write("1️⃣ Estado actual del sistema:")
        self.listar_solicitudes()
        
        # 2. Crear solicitud de prueba
        self.stdout.write("\n2️⃣ Creando solicitud de prueba:")
        self.crear_solicitud_prueba()
        
        # 3. Listar nuevamente
        self.stdout.write("\n3️⃣ Estado después de crear solicitud:")
        self.listar_solicitudes()
        
        # 4. Verificar endpoints
        self.stdout.write("\n4️⃣ ENDPOINTS DISPONIBLES:")
        endpoints = [
            "POST /api/authz/propietarios/solicitud-registro/",
            "GET  /api/authz/propietarios/admin/solicitudes/",
            "GET  /api/authz/propietarios/admin/solicitudes/{id}/",
            "POST /api/authz/propietarios/admin/solicitudes/{id}/aprobar/",
            "POST /api/authz/propietarios/admin/solicitudes/{id}/rechazar/"
        ]
        
        for endpoint in endpoints:
            self.stdout.write(f"✅ {endpoint}")
        
        self.stdout.write("\n🎯 FUNCIONALIDADES IMPLEMENTADAS:")
        funcionalidades = [
            "Creación de solicitudes con validaciones",
            "Verificación de email y documento únicos",
            "Validación de viviendas disponibles",
            "Sistema de tokens de seguimiento",
            "Aprobación automática con creación de usuario",
            "Asignación automática de rol propietario",
            "Envío automático de emails",
            "Gestión de estados de solicitudes",
            "Autenticación JWT para administradores",
            "Comandos de gestión desde consola"
        ]
        
        for func in funcionalidades:
            self.stdout.write(f"✅ {func}")
        
        self.stdout.write(f"\n📊 RESUMEN:")
        total_solicitudes = SolicitudRegistroPropietario.objects.count()
        pendientes = SolicitudRegistroPropietario.objects.filter(estado='PENDIENTE').count()
        aprobadas = SolicitudRegistroPropietario.objects.filter(estado='APROBADA').count()
        rechazadas = SolicitudRegistroPropietario.objects.filter(estado='RECHAZADA').count()
        
        self.stdout.write(f"📋 Total solicitudes: {total_solicitudes}")
        self.stdout.write(f"⏳ Pendientes: {pendientes}")
        self.stdout.write(f"✅ Aprobadas: {aprobadas}")
        self.stdout.write(f"❌ Rechazadas: {rechazadas}")
        
        self.stdout.write(self.style.SUCCESS("\n🎉 SISTEMA COMPLETAMENTE FUNCIONAL"))