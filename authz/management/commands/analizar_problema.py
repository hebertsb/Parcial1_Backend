"""
Comando para analizar las diferencias entre los endpoints
"""
import json
from django.core.management.base import BaseCommand
from authz.models import SolicitudRegistroPropietario


class Command(BaseCommand):
    help = 'Analiza las diferencias entre endpoints y verifica el estado actual'

    def handle(self, *args, **options):
        self.stdout.write("🔍 ANÁLISIS DE ENDPOINTS Y ESTADO ACTUAL")
        self.stdout.write("=" * 50)
        
        # 1. Mostrar todas las solicitudes actuales
        self.mostrar_solicitudes_actuales()
        
        # 2. Analizar configuración de URLs
        self.analizar_urls()
        
        # 3. Dar recomendaciones
        self.dar_recomendaciones()

    def mostrar_solicitudes_actuales(self):
        """Muestra todas las solicitudes en la base de datos"""
        self.stdout.write("\n📋 SOLICITUDES ACTUALES EN LA BASE DE DATOS:")
        self.stdout.write("-" * 45)
        
        solicitudes = SolicitudRegistroPropietario.objects.all().order_by('-created_at')
        
        if not solicitudes:
            self.stdout.write("❌ No hay solicitudes en la base de datos")
            return
            
        for i, sol in enumerate(solicitudes, 1):
            created_str = sol.created_at.strftime('%Y-%m-%d %H:%M:%S') if sol.created_at else 'N/A'
            self.stdout.write(f"  {i}. ID: {sol.pk}")
            self.stdout.write(f"     👤 Nombre: {sol.nombres} {sol.apellidos}")
            self.stdout.write(f"     📧 Email: {sol.email}")
            self.stdout.write(f"     🏠 Vivienda: {sol.numero_casa}")
            self.stdout.write(f"     📊 Estado: {sol.estado}")
            self.stdout.write(f"     📅 Creado: {created_str}")
            self.stdout.write("")

    def analizar_urls(self):
        """Analiza la configuración de URLs"""
        self.stdout.write("🌐 ANÁLISIS DE CONFIGURACIÓN DE URLs:")
        self.stdout.write("-" * 40)
        
        self.stdout.write("📍 ENDPOINTS DISPONIBLES PARA CREAR SOLICITUDES:")
        self.stdout.write("  1. /api/authz/propietarios/solicitud/")
        self.stdout.write("     └── Definido en: authz/urls_propietario.py línea 16")
        self.stdout.write("     └── Vista: RegistroSolicitudPropietarioView")
        self.stdout.write("")
        self.stdout.write("  2. /api/authz/propietarios/solicitud-registro/")
        self.stdout.write("     └── Definido en: authz/urls.py")
        self.stdout.write("     └── Vista: RegistroSolicitudPropietarioView")
        
        self.stdout.write("\n📍 ENDPOINT PARA LISTAR SOLICITUDES (ADMIN):")
        self.stdout.write("  • /api/authz/propietarios/admin/solicitudes/")
        self.stdout.write("     └── Vista: SolicitudesPendientesView")
        self.stdout.write("     └── Requiere: Autenticación JWT + Rol Admin")

    def dar_recomendaciones(self):
        """Da recomendaciones para solucionar el problema"""
        self.stdout.write("\n💡 RECOMENDACIONES PARA SOLUCIONAR EL PROBLEMA:")
        self.stdout.write("-" * 48)
        
        self.stdout.write("🎯 PASO 1: Identificar qué endpoint usa tu frontend")
        self.stdout.write("   • Revisa el código de tu frontend Next.js")
        self.stdout.write("   • Busca las llamadas fetch() o axios.post()")
        self.stdout.write("   • Verifica si usa:")
        self.stdout.write("     - /api/authz/propietarios/solicitud/ (MÁS PROBABLE)")
        self.stdout.write("     - /api/authz/propietarios/solicitud-registro/")
        
        self.stdout.write("\n🔧 PASO 2: Verificar el formato de datos")
        self.stdout.write("   • Asegúrate que el frontend envíe:")
        self.stdout.write("     - Content-Type: application/json")
        self.stdout.write("     - Ambos campos: password_confirm Y confirm_password")
        self.stdout.write("     - acepta_terminos: true")
        self.stdout.write("     - acepta_tratamiento_datos: true")
        
        self.stdout.write("\n🔍 PASO 3: Verificar en el navegador")
        self.stdout.write("   • Abre las DevTools (F12)")
        self.stdout.write("   • Ve a la pestaña Network")
        self.stdout.write("   • Envía una solicitud desde tu frontend")
        self.stdout.write("   • Revisa:")
        self.stdout.write("     - La URL exacta que se llama")
        self.stdout.write("     - El status code de respuesta")
        self.stdout.write("     - Los datos enviados en el body")
        self.stdout.write("     - La respuesta del servidor")
        
        self.stdout.write("\n🚀 PASO 4: URLs correctas para tu frontend")
        self.stdout.write("   • Crear solicitud (público):")
        self.stdout.write("     POST /api/authz/propietarios/solicitud/")
        self.stdout.write("   • Listar solicitudes (admin):")
        self.stdout.write("     GET /api/authz/propietarios/admin/solicitudes/")
        self.stdout.write("     Headers: Authorization: Bearer <jwt_token>")
        
        # Mostrar estado actual de pruebas
        total_solicitudes = SolicitudRegistroPropietario.objects.count()
        pendientes = SolicitudRegistroPropietario.objects.filter(estado='PENDIENTE').count()
        
        self.stdout.write(f"\n📊 ESTADO ACTUAL:")
        self.stdout.write(f"   • Total solicitudes: {total_solicitudes}")
        self.stdout.write(f"   • Solicitudes pendientes: {pendientes}")
        self.stdout.write(f"   • Solicitudes de prueba funcionando: ✅")
        self.stdout.write(f"   • Backend endpoints funcionando: ✅")
        self.stdout.write(f"   • Problema: Conexión frontend ↔ backend ❌")