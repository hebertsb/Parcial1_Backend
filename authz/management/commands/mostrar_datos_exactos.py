"""
Comando para mostrar todos los datos exactos del endpoint de solicitudes
"""
import json
import requests
from django.core.management.base import BaseCommand
from rest_framework_simplejwt.tokens import RefreshToken
from authz.models import Usuario, SolicitudRegistroPropietario


class Command(BaseCommand):
    help = 'Muestra todos los datos exactos que envía el endpoint de solicitudes'

    def handle(self, *args, **options):
        self.stdout.write("📊 DATOS EXACTOS DEL ENDPOINT DE SOLICITUDES")
        self.stdout.write("=" * 55)
        
        # 1. Mostrar datos raw de la base de datos
        self.mostrar_datos_bd()
        
        # 2. Mostrar datos del endpoint con todos los campos
        self.mostrar_datos_endpoint()

    def mostrar_datos_bd(self):
        """Muestra datos directos de la base de datos"""
        self.stdout.write("\n🗃️  DATOS DIRECTOS DE LA BASE DE DATOS:")
        self.stdout.write("-" * 45)
        
        solicitudes = SolicitudRegistroPropietario.objects.filter(
            estado='PENDIENTE'
        ).order_by('-created_at')
        
        for sol in solicitudes:
            self.stdout.write(f"\n📋 Solicitud ID: {sol.pk}")
            self.stdout.write(f"   👤 Nombres: '{sol.nombres}'")
            self.stdout.write(f"   👤 Apellidos: '{sol.apellidos}'")
            self.stdout.write(f"   📧 Email: '{sol.email}'")
            self.stdout.write(f"   📞 Teléfono: '{sol.telefono}'")
            self.stdout.write(f"   📄 Documento: '{sol.documento_identidad}'")
            self.stdout.write(f"   🏠 Vivienda: '{sol.numero_casa}'")
            self.stdout.write(f"   📅 Fecha Nac: {sol.fecha_nacimiento}")
            self.stdout.write(f"   📊 Estado: '{sol.estado}'")
            self.stdout.write(f"   🎫 Token: '{sol.token_seguimiento}'")
            self.stdout.write(f"   ⏰ Creado: {sol.created_at}")
            if sol.vivienda_validada:
                self.stdout.write(f"   🏘️  Vivienda Validada: {sol.vivienda_validada.numero_casa}")

    def mostrar_datos_endpoint(self):
        """Muestra datos exactos del endpoint con autenticación"""
        self.stdout.write("\n🌐 DATOS EXACTOS DEL ENDPOINT:")
        self.stdout.write("-" * 35)
        
        try:
            # Obtener token
            admin_user = Usuario.objects.filter(
                roles__nombre__in=['Administrador', 'ADMIN']
            ).first()
            
            if not admin_user:
                self.stdout.write(self.style.ERROR("❌ No se encontró usuario admin"))
                return
                
            refresh = RefreshToken.for_user(admin_user)
            access_token = str(refresh.access_token)
            
            # Hacer petición completa
            headers = {
                'Authorization': f'Bearer {access_token}',
                'Content-Type': 'application/json',
                'Accept': 'application/json'
            }
            
            url = "http://127.0.0.1:8000/api/authz/propietarios/admin/solicitudes/"
            response = requests.get(url, headers=headers, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                
                self.stdout.write(f"📡 URL: {url}")
                self.stdout.write(f"📊 Status: {response.status_code}")
                self.stdout.write(f"📊 Content-Type: {response.headers.get('content-type')}")
                
                self.stdout.write(f"\n📋 ESTRUCTURA DE LA RESPUESTA:")
                self.stdout.write(f"   • Count: {data.get('count')}")
                self.stdout.write(f"   • Results length: {len(data.get('results', []))}")
                
                self.stdout.write(f"\n📄 RESPUESTA COMPLETA (JSON):")
                self.stdout.write("-" * 40)
                print(json.dumps(data, indent=2, ensure_ascii=False))
                
                self.stdout.write(f"\n🔍 ANÁLISIS DE CADA SOLICITUD:")
                self.stdout.write("-" * 35)
                
                for i, solicitud in enumerate(data.get('results', []), 1):
                    self.stdout.write(f"\n🔸 Solicitud {i}:")
                    for key, value in solicitud.items():
                        self.stdout.write(f"     {key}: {value}")
                        
            else:
                self.stdout.write(self.style.ERROR(f"❌ Error {response.status_code}: {response.text}"))
                
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"💥 Error: {str(e)}"))
            import traceback
            self.stdout.write(traceback.format_exc())