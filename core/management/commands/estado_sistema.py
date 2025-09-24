"""
Comando para mostrar el estado completo del sistema: viviendas, usuarios y solicitudes
"""
from django.core.management.base import BaseCommand
from core.models import Vivienda, Propiedad
from authz.models import Usuario, Rol, SolicitudRegistroPropietario
from django.db.models import Q

class Command(BaseCommand):
    help = 'Muestra el estado completo del sistema para pruebas del frontend'

    def handle(self, **options):
        self.stdout.write(self.style.SUCCESS("🎯 ESTADO COMPLETO DEL SISTEMA PARA FRONTEND"))
        self.stdout.write("=" * 70)
        
        self.mostrar_viviendas_disponibles()
        self.mostrar_usuarios_prueba()
        self.mostrar_solicitudes()
        self.mostrar_ejemplos_frontend()

    def mostrar_viviendas_disponibles(self):
        """Muestra viviendas disponibles para nuevas solicitudes"""
        self.stdout.write("\n🏠 VIVIENDAS DISPONIBLES PARA SOLICITUDES:")
        self.stdout.write("-" * 50)
        
        # Viviendas sin propietario
        viviendas_sin_propietario = Vivienda.objects.filter(
            ~Q(id__in=Propiedad.objects.filter(
                tipo_tenencia='propietario', 
                activo=True
            ).values_list('vivienda_id', flat=True))
        ).order_by('numero_casa')
        
        # Viviendas sin solicitudes activas
        viviendas_sin_solicitud = viviendas_sin_propietario.exclude(
            numero_casa__in=SolicitudRegistroPropietario.objects.filter(
                estado__in=['PENDIENTE', 'EN_REVISION', 'APROBADA']
            ).values_list('numero_casa', flat=True)
        )
        
        self.stdout.write(f"🆓 Total viviendas disponibles: {viviendas_sin_solicitud.count()}")
        
        # Mostrar las primeras 15 viviendas disponibles
        for vivienda in viviendas_sin_solicitud[:15]:
            tipo_icon = "🏘️" if vivienda.tipo_vivienda == 'casa' else "🏢"
            self.stdout.write(
                f"   {tipo_icon} {vivienda.numero_casa} - "
                f"{vivienda.tipo_vivienda.title()} - "
                f"{vivienda.metros_cuadrados}m² - "
                f"Bs.{vivienda.tarifa_base_expensas} - "
                f"Bloque {vivienda.bloque}"
            )
        
        if viviendas_sin_solicitud.count() > 15:
            self.stdout.write(f"   ... y {viviendas_sin_solicitud.count() - 15} más disponibles")

    def mostrar_usuarios_prueba(self):
        """Muestra usuarios de prueba disponibles"""
        self.stdout.write("\n👥 USUARIOS DE PRUEBA DISPONIBLES:")
        self.stdout.write("-" * 50)
        
        # Administradores
        admins = Usuario.objects.filter(roles__nombre='Administrador')
        self.stdout.write(f"🔑 ADMINISTRADORES ({admins.count()}):")
        for admin in admins[:3]:
            self.stdout.write(f"   📧 {admin.email} | 🔐 admin123")
        
        # Propietarios
        propietarios = Usuario.objects.filter(roles__nombre='Propietario')
        self.stdout.write(f"\n🏠 PROPIETARIOS ({propietarios.count()}):")
        for prop in propietarios[:5]:
            vivienda_info = "Sin vivienda asignada"
            if hasattr(prop.persona, 'propiedad_set'):
                propiedad = prop.persona.propiedad_set.filter(activo=True).first()
                if propiedad:
                    vivienda_info = f"Vivienda {propiedad.vivienda.numero_casa}"
            self.stdout.write(f"   📧 {prop.email} | 🔐 propietario123 | 🏠 {vivienda_info}")
        
        # Seguridad
        seguridad = Usuario.objects.filter(roles__nombre='Seguridad')
        self.stdout.write(f"\n🛡️ SEGURIDAD ({seguridad.count()}):")
        for seg in seguridad[:3]:
            self.stdout.write(f"   📧 {seg.email} | 🔐 seguridad123")

    def mostrar_solicitudes(self):
        """Muestra el estado de las solicitudes"""
        self.stdout.write("\n📋 ESTADO DE SOLICITUDES:")
        self.stdout.write("-" * 50)
        
        total = SolicitudRegistroPropietario.objects.count()
        pendientes = SolicitudRegistroPropietario.objects.filter(estado='PENDIENTE').count()
        aprobadas = SolicitudRegistroPropietario.objects.filter(estado='APROBADA').count()
        rechazadas = SolicitudRegistroPropietario.objects.filter(estado='RECHAZADA').count()
        
        self.stdout.write(f"📊 Total: {total} | ⏳ Pendientes: {pendientes} | ✅ Aprobadas: {aprobadas} | ❌ Rechazadas: {rechazadas}")
        
        if pendientes > 0:
            self.stdout.write("\n⏳ SOLICITUDES PENDIENTES:")
            solicitudes_pendientes = SolicitudRegistroPropietario.objects.filter(
                estado='PENDIENTE'
            ).order_by('-created_at')
            
            for solicitud in solicitudes_pendientes:
                self.stdout.write(
                    f"   ID: {solicitud.id} | {solicitud.nombres} {solicitud.apellidos} | "
                    f"📧 {solicitud.email} | 🏠 {solicitud.numero_casa} | "
                    f"🎫 {solicitud.token_seguimiento}"
                )

    def mostrar_ejemplos_frontend(self):
        """Muestra ejemplos para probar el frontend"""
        self.stdout.write("\n🚀 EJEMPLOS PARA PROBAR EL FRONTEND:")
        self.stdout.write("=" * 50)
        
        # Ejemplo de nueva solicitud
        vivienda_ejemplo = Vivienda.objects.filter(
            ~Q(id__in=Propiedad.objects.filter(
                tipo_tenencia='propietario', 
                activo=True
            ).values_list('vivienda_id', flat=True))
        ).exclude(
            numero_casa__in=SolicitudRegistroPropietario.objects.filter(
                estado__in=['PENDIENTE', 'EN_REVISION', 'APROBADA']
            ).values_list('numero_casa', flat=True)
        ).first()
        
        if vivienda_ejemplo:
            self.stdout.write("\n📝 DATOS DE EJEMPLO PARA CREAR SOLICITUD:")
            self.stdout.write("```json")
            self.stdout.write("{")
            self.stdout.write('  "nombres": "Juan Carlos",')
            self.stdout.write('  "apellidos": "Pérez Mendoza",')
            self.stdout.write('  "documento_identidad": "9876543",')
            self.stdout.write('  "email": "juan.perez@ejemplo.com",')
            self.stdout.write('  "telefono": "79876543",')
            self.stdout.write(f'  "numero_casa": "{vivienda_ejemplo.numero_casa}",')
            self.stdout.write('  "fecha_nacimiento": "1985-06-15",')
            self.stdout.write('  "acepta_terminos": true,')
            self.stdout.write('  "password": "MiPassword123!",')
            self.stdout.write('  "confirm_password": "MiPassword123!"')
            self.stdout.write("}")
            self.stdout.write("```")
        
        # URLs de ejemplo
        self.stdout.write("\n🌐 ENDPOINTS PARA PROBAR:")
        self.stdout.write("POST http://localhost:8000/api/authz/propietarios/solicitud-registro/")
        self.stdout.write("GET  http://localhost:8000/api/authz/propietarios/admin/solicitudes/")
        
        # Token de admin
        admin = Usuario.objects.filter(roles__nombre='Administrador').first()
        if admin:
            self.stdout.write(f"\n🔑 PARA OBTENER TOKEN JWT DE ADMIN:")
            self.stdout.write("POST http://localhost:8000/api/auth/login/")
            self.stdout.write("Body:")
            self.stdout.write("{")
            self.stdout.write(f'  "email": "{admin.email}",')
            self.stdout.write('  "password": "admin123"')
            self.stdout.write("}")
        
        self.stdout.write("\n✅ ¡SISTEMA LISTO PARA PROBAR CON EL FRONTEND!")
        self.stdout.write(f"🏠 {Vivienda.objects.count()} viviendas totales")
        self.stdout.write(f"🆓 {Vivienda.objects.filter(~Q(id__in=Propiedad.objects.filter(tipo_tenencia='propietario', activo=True).values_list('vivienda_id', flat=True))).exclude(numero_casa__in=SolicitudRegistroPropietario.objects.filter(estado__in=['PENDIENTE', 'EN_REVISION', 'APROBADA']).values_list('numero_casa', flat=True)).count()} viviendas disponibles para solicitudes")
        self.stdout.write(f"👥 {Usuario.objects.count()} usuarios totales")
        self.stdout.write(f"📋 {SolicitudRegistroPropietario.objects.count()} solicitudes totales")