"""
Comando para probar la creación de solicitudes via API
"""
import json
import requests
from django.core.management.base import BaseCommand
from authz.models import SolicitudRegistroPropietario


class Command(BaseCommand):
    help = 'Prueba crear una nueva solicitud via API'

    def handle(self, *args, **options):
        self.stdout.write("🧪 Probando creación de solicitud via API...")
        
        # Datos de prueba - usando info similar a la que reportaste
        solicitud_data = {
            "nombres": "Hebert",
            "apellidos": "Suarez Burgos",
            "documento_identidad": "98765432",
            "email": "hebert.suarez@test.com",
            "telefono": "77777777",
            "numero_casa": "008E",  # Usemos una vivienda disponible
            "fecha_nacimiento": "1990-01-01",
            "acepta_terminos": True,
            "acepta_tratamiento_datos": True,
            "password": "MiPassword123!",
            "password_confirm": "MiPassword123!",
            "confirm_password": "MiPassword123!"
        }
        
        # Base URL del servidor
        base_url = "http://127.0.0.1:8000"
        
        try:
            # Hacer petición POST al endpoint de crear solicitud
            headers = {
                'Content-Type': 'application/json'
            }
            
            url = f"{base_url}/api/authz/propietarios/solicitud-registro/"
            self.stdout.write(f"🌐 Haciendo petición POST a: {url}")
            self.stdout.write(f"📝 Datos enviados: {json.dumps(solicitud_data, indent=2)}")
            
            response = requests.post(url, headers=headers, json=solicitud_data, timeout=10)
            
            self.stdout.write(f"📊 Status Code: {response.status_code}")
            
            if response.status_code == 201:
                data = response.json()
                self.stdout.write(self.style.SUCCESS(f"✅ Solicitud creada exitosamente:"))
                self.stdout.write(f"📊 Respuesta: {json.dumps(data, indent=2)}")
                
                # Verificar que se creó en la BD
                nueva_solicitud = SolicitudRegistroPropietario.objects.filter(
                    documento_identidad="98765432"
                ).first()
                
                if nueva_solicitud:
                    self.stdout.write(f"✅ Solicitud encontrada en BD:")
                    self.stdout.write(f"    ID: {nueva_solicitud.id}")
                    self.stdout.write(f"    Nombre: {nueva_solicitud.nombres} {nueva_solicitud.apellidos}")
                    self.stdout.write(f"    Estado: {nueva_solicitud.estado}")
                    self.stdout.write(f"    Vivienda: {nueva_solicitud.numero_casa}")
                    
                    # Ahora verificar que aparece en el endpoint de admin
                    self.verificar_endpoint_admin()
                    
            else:
                self.stdout.write(self.style.ERROR(f"❌ Error {response.status_code}:"))
                try:
                    error_data = response.json()
                    self.stdout.write(f"Error: {json.dumps(error_data, indent=2)}")
                except:
                    self.stdout.write(f"Response text: {response.text}")
                    
        except requests.exceptions.RequestException as e:
            self.stdout.write(self.style.ERROR(f"❌ Error de conexión: {str(e)}"))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"❌ Error inesperado: {str(e)}"))
    
    def verificar_endpoint_admin(self):
        """Verificar que la nueva solicitud aparece en el endpoint de admin"""
        self.stdout.write("\n🔍 Verificando endpoint de admin después de crear solicitud...")
        
        # Obtener token (código copiado del otro comando)
        from rest_framework_simplejwt.tokens import RefreshToken
        from authz.models import Usuario
        
        admin_user = Usuario.objects.filter(
            roles__nombre__in=['Administrador', 'ADMIN']
        ).first()
        
        if not admin_user:
            self.stdout.write(self.style.ERROR("❌ No se encontró usuario administrador"))
            return
            
        refresh = RefreshToken.for_user(admin_user)
        access_token = str(refresh.access_token)
        
        # Hacer petición al endpoint de admin
        headers = {
            'Authorization': f'Bearer {access_token}',
            'Content-Type': 'application/json'
        }
        
        url = "http://127.0.0.1:8000/api/authz/propietarios/admin/solicitudes/"
        response = requests.get(url, headers=headers, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            self.stdout.write(f"✅ Endpoint admin responde correctamente:")
            self.stdout.write(f"📊 Count: {data.get('count', 'N/A')}")
            
            results = data.get('results', [])
            self.stdout.write(f"📊 Solicitudes pendientes encontradas: {len(results)}")
            
            for i, solicitud in enumerate(results, 1):
                self.stdout.write(f"  🔍 Solicitud {i}:")
                self.stdout.write(f"    ID: {solicitud.get('id')}")
                self.stdout.write(f"    Nombre: {solicitud.get('nombres')} {solicitud.get('apellidos')}")
                self.stdout.write(f"    Estado: {solicitud.get('estado')}")
        else:
            self.stdout.write(self.style.ERROR(f"❌ Error en endpoint admin: {response.status_code}"))