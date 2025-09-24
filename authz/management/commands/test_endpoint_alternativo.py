"""
Comando para probar el endpoint alternativo de solicitudes
"""
import json
import requests
from django.core.management.base import BaseCommand
from authz.models import SolicitudRegistroPropietario


class Command(BaseCommand):
    help = 'Prueba el endpoint alternativo que podría estar usando el frontend'

    def handle(self, *args, **options):
        self.stdout.write("🔍 PROBANDO ENDPOINT ALTERNATIVO DE SOLICITUDES")
        self.stdout.write("=" * 60)
        
        # Datos de prueba
        solicitud_data = {
            "nombres": "María José",
            "apellidos": "Ramírez Castro",
            "documento_identidad": "55555555",
            "email": "maria.ramirez@test.com",
            "telefono": "77888999",
            "numero_casa": "009C",
            "fecha_nacimiento": "1992-03-15",
            "acepta_terminos": True,
            "acepta_tratamiento_datos": True,
            "password": "MiPassword123!",
            "password_confirm": "MiPassword123!",
            "confirm_password": "MiPassword123!"
        }
        
        base_url = "http://127.0.0.1:8000"
        
        # Lista de endpoints posibles que podría estar usando el frontend
        endpoints_a_probar = [
            "/api/authz/propietarios/solicitud/",  # De urls_propietario.py
            "/api/authz/propietarios/solicitud-registro/",  # De urls.py
            "/api/authz/propietarios/registro-inicial/",  # Registro inicial
        ]
        
        for endpoint in endpoints_a_probar:
            self.probar_endpoint_crear(base_url + endpoint, solicitud_data)
            self.stdout.write("-" * 40)

    def probar_endpoint_crear(self, url, data):
        """Prueba crear solicitud en un endpoint específico"""
        self.stdout.write(f"🌐 Probando: {url}")
        
        try:
            headers = {'Content-Type': 'application/json'}
            response = requests.post(url, headers=headers, json=data, timeout=10)
            
            self.stdout.write(f"📊 Status Code: {response.status_code}")
            
            if response.status_code == 201:
                response_data = response.json()
                self.stdout.write(self.style.SUCCESS(f"✅ ¡ÉXITO! Solicitud creada:"))
                self.stdout.write(f"   Respuesta: {json.dumps(response_data, indent=2)}")
                
                # Verificar en BD
                if 'data' in response_data and 'id' in response_data['data']:
                    solicitud_id = response_data['data']['id']
                    solicitud = SolicitudRegistroPropietario.objects.filter(pk=solicitud_id).first()
                    if solicitud:
                        self.stdout.write(f"✅ Verificado en BD: ID={solicitud.pk}, Estado={solicitud.estado}")
                
            elif response.status_code == 400:
                try:
                    error_data = response.json()
                    self.stdout.write(self.style.WARNING(f"⚠️  Error 400 - Datos inválidos:"))
                    self.stdout.write(f"   {json.dumps(error_data, indent=2)}")
                except:
                    self.stdout.write(f"⚠️  Error 400: {response.text}")
                    
            elif response.status_code == 404:
                self.stdout.write(self.style.ERROR(f"❌ Error 404 - Endpoint no encontrado"))
                
            elif response.status_code == 405:
                self.stdout.write(self.style.WARNING(f"⚠️  Error 405 - Método no permitido (endpoint existe pero no acepta POST)"))
                
            else:
                self.stdout.write(f"❓ Status Code {response.status_code}: {response.text[:200]}")
                
        except requests.exceptions.RequestException as e:
            self.stdout.write(self.style.ERROR(f"💥 Error de conexión: {str(e)}"))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"💥 Error inesperado: {str(e)}"))