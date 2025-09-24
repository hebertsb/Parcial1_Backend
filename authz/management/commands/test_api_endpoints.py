"""
Comando para probar los endpoints de solicitudes de propietarios
"""
import json
import requests
from django.core.management.base import BaseCommand
from django.contrib.auth import authenticate
from django.conf import settings
from rest_framework_simplejwt.tokens import RefreshToken
from authz.models import Usuario, SolicitudRegistroPropietario


class Command(BaseCommand):
    help = 'Prueba los endpoints de solicitudes de propietarios'

    def add_arguments(self, parser):
        parser.add_argument('--accion', choices=['test_api', 'test_auth', 'test_admin_list'], 
                          default='test_admin_list', help='Acción a realizar')

    def handle(self, *args, **options):
        accion = options['accion']
        
        if accion == 'test_auth':
            self.test_authentication()
        elif accion == 'test_admin_list':
            self.test_admin_list_endpoint()
        elif accion == 'test_api':
            self.test_complete_api()

    def test_authentication(self):
        """Prueba la autenticación JWT"""
        self.stdout.write("🔐 Probando autenticación JWT...")
        
        # Buscar usuario admin
        try:
            admin_user = Usuario.objects.filter(
                roles__nombre__in=['Administrador', 'ADMIN']
            ).first()
            
            if not admin_user:
                self.stdout.write(self.style.ERROR("❌ No se encontró usuario administrador"))
                return None
                
            self.stdout.write(f"✅ Usuario admin encontrado: {admin_user.email}")
            
            # Generar token JWT
            refresh = RefreshToken.for_user(admin_user)
            access_token = str(refresh.access_token)
            
            self.stdout.write(f"✅ Token JWT generado: {access_token[:50]}...")
            return access_token
            
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"❌ Error en autenticación: {str(e)}"))
            return None

    def test_admin_list_endpoint(self):
        """Prueba el endpoint de listar solicitudes para admin"""
        self.stdout.write("📋 Probando endpoint de listar solicitudes...")
        
        # Obtener token
        token = self.test_authentication()
        if not token:
            return
            
        # Base URL del servidor
        base_url = "http://127.0.0.1:8000"  # Ajustar según tu configuración
        
        try:
            # Hacer petición al endpoint
            headers = {
                'Authorization': f'Bearer {token}',
                'Content-Type': 'application/json'
            }
            
            url = f"{base_url}/api/authz/propietarios/admin/solicitudes/"
            self.stdout.write(f"🌐 Haciendo petición GET a: {url}")
            
            response = requests.get(url, headers=headers, timeout=10)
            
            self.stdout.write(f"📊 Status Code: {response.status_code}")
            self.stdout.write(f"📊 Headers: {dict(response.headers)}")
            
            if response.status_code == 200:
                data = response.json()
                self.stdout.write(self.style.SUCCESS(f"✅ Respuesta exitosa:"))
                self.stdout.write(f"📊 Count: {data.get('count', 'N/A')}")
                
                results = data.get('results', [])
                self.stdout.write(f"📊 Resultados encontrados: {len(results)}")
                
                for i, solicitud in enumerate(results, 1):
                    self.stdout.write(f"\n  🔍 Solicitud {i}:")
                    self.stdout.write(f"    ID: {solicitud.get('id')}")
                    self.stdout.write(f"    Nombre: {solicitud.get('nombres')} {solicitud.get('apellidos')}")
                    self.stdout.write(f"    Email: {solicitud.get('email')}")
                    self.stdout.write(f"    Vivienda: {solicitud.get('numero_casa')}")
                    self.stdout.write(f"    Estado: {solicitud.get('estado')}")
                    self.stdout.write(f"    Fecha: {solicitud.get('created_at')}")
                    
            else:
                self.stdout.write(self.style.ERROR(f"❌ Error {response.status_code}:"))
                try:
                    error_data = response.json()
                    self.stdout.write(f"Error: {error_data}")
                except:
                    self.stdout.write(f"Response text: {response.text}")
                    
        except requests.exceptions.RequestException as e:
            self.stdout.write(self.style.ERROR(f"❌ Error de conexión: {str(e)}"))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"❌ Error inesperado: {str(e)}"))

    def test_complete_api(self):
        """Prueba completa de la API"""
        self.stdout.write("🧪 Iniciando prueba completa de API...")
        
        # 1. Verificar datos en BD
        solicitudes_bd = SolicitudRegistroPropietario.objects.all()
        self.stdout.write(f"📊 Solicitudes en BD: {solicitudes_bd.count()}")
        
        for sol in solicitudes_bd:
            self.stdout.write(f"  - ID:{sol.id} | {sol.nombres} {sol.apellidos} | {sol.estado} | {sol.numero_casa}")
        
        # 2. Probar endpoint
        self.test_admin_list_endpoint()
        
        # 3. Verificar usuarios admin
        admins = Usuario.objects.filter(roles__nombre__in=['Administrador', 'ADMIN'])
        self.stdout.write(f"\n👥 Usuarios admin: {admins.count()}")
        for admin in admins:
            self.stdout.write(f"  - {admin.email} | Activo: {admin.is_active}")