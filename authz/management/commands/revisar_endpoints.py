"""
Comando para revisar todos los endpoints disponibles en el sistema
"""
from django.core.management.base import BaseCommand
from django.urls import get_resolver
from django.conf import settings
import requests


class Command(BaseCommand):
    help = 'Revisa todos los endpoints disponibles del sistema'

    def add_arguments(self, parser):
        parser.add_argument('--accion', choices=['urls', 'test_endpoints'], 
                          default='urls', help='Acción a realizar')

    def handle(self, *args, **options):
        accion = options['accion']
        
        if accion == 'urls':
            self.mostrar_urls_sistema()
        elif accion == 'test_endpoints':
            self.probar_endpoints_propietarios()

    def mostrar_urls_sistema(self):
        """Muestra todas las URLs del sistema"""
        self.stdout.write("🌐 URLs DISPONIBLES EN EL SISTEMA")
        self.stdout.write("=" * 50)
        
        resolver = get_resolver()
        self.mostrar_urls_recursivo(resolver.url_patterns, '')

    def mostrar_urls_recursivo(self, url_patterns, prefijo=''):
        """Muestra URLs de forma recursiva"""
        for pattern in url_patterns:
            if hasattr(pattern, 'url_patterns'):
                # Es un include(), mostrar las URLs anidadas
                nuevo_prefijo = prefijo + str(pattern.pattern)
                self.stdout.write(f"\n📁 {nuevo_prefijo}")
                self.mostrar_urls_recursivo(pattern.url_patterns, nuevo_prefijo)
            else:
                # Es una URL individual
                url_completa = prefijo + str(pattern.pattern)
                nombre = getattr(pattern, 'name', 'sin_nombre')
                
                # Filtrar solo URLs relacionadas con propietarios/solicitudes
                if any(keyword in url_completa.lower() for keyword in ['propietario', 'solicitud', 'authz']):
                    self.stdout.write(f"  🔗 {url_completa} -> {nombre}")

    def probar_endpoints_propietarios(self):
        """Prueba específicamente los endpoints de propietarios"""
        self.stdout.write("🧪 PROBANDO ENDPOINTS DE PROPIETARIOS")
        self.stdout.write("=" * 50)
        
        base_url = "http://127.0.0.1:8000"
        endpoints_a_probar = [
            # Endpoints públicos
            "/api/authz/propietarios/solicitud-registro/",
            "/api/authz/propietarios/registro-inicial/",
            
            # Posibles endpoints alternativos que podría estar usando el frontend
            "/api/propietarios/solicitud/",
            "/api/propietarios/solicitud-registro/",
            "/api/propietarios/registro/",
            "/api/solicitudes/",
            "/api/solicitudes/crear/",
            
            # Endpoints de admin
            "/api/authz/propietarios/admin/solicitudes/",
        ]
        
        for endpoint in endpoints_a_probar:
            self.probar_endpoint(base_url + endpoint, "GET")

    def probar_endpoint(self, url, method="GET"):
        """Prueba un endpoint específico"""
        try:
            if method == "GET":
                response = requests.get(url, timeout=5)
            else:
                response = requests.post(url, timeout=5)
            
            if response.status_code == 200:
                self.stdout.write(f"✅ {method} {url} -> 200 OK")
            elif response.status_code == 405:
                self.stdout.write(f"⚠️  {method} {url} -> 405 Method Not Allowed (endpoint existe, método incorrecto)")
            elif response.status_code == 404:
                self.stdout.write(f"❌ {method} {url} -> 404 Not Found")
            elif response.status_code == 401:
                self.stdout.write(f"🔐 {method} {url} -> 401 Unauthorized (requiere autenticación)")
            elif response.status_code == 403:
                self.stdout.write(f"🚫 {method} {url} -> 403 Forbidden (requiere permisos)")
            else:
                self.stdout.write(f"❓ {method} {url} -> {response.status_code}")
                
        except requests.exceptions.RequestException as e:
            self.stdout.write(f"💥 {method} {url} -> Error de conexión: {str(e)}")
        except Exception as e:
            self.stdout.write(f"💥 {method} {url} -> Error: {str(e)}")