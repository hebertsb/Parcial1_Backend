"""
Comando para simular exactamente lo que hace el frontend
"""
import json
from django.core.management.base import BaseCommand
from django.test import RequestFactory
from django.contrib.auth.models import AnonymousUser
from authz.views_propietario import RegistroSolicitudPropietarioView
from authz.models import SolicitudRegistroPropietario


class Command(BaseCommand):
    help = 'Simula la creación de solicitud tal como lo haría el frontend'

    def handle(self, *args, **options):
        self.stdout.write("🎭 SIMULANDO FRONTEND - CREACIÓN DE SOLICITUD")
        self.stdout.write("=" * 55)
        
        # Datos que enviaría el frontend
        frontend_data = {
            "nombres": "Carlos",
            "apellidos": "Mendoza Vargas",
            "documento_identidad": "88888888",
            "email": "carlos.mendoza@frontend.com",
            "telefono": "78901234",
            "numero_casa": "010C",
            "fecha_nacimiento": "1988-07-20",
            "acepta_terminos": True,
            "acepta_tratamiento_datos": True,
            "password": "FrontendPass123!",
            "password_confirm": "FrontendPass123!",
            "confirm_password": "FrontendPass123!"
        }
        
        self.stdout.write(f"📝 Datos del frontend:")
        self.stdout.write(json.dumps(frontend_data, indent=2, ensure_ascii=False))
        
        # Crear request simulado
        factory = RequestFactory()
        request = factory.post(
            '/api/authz/propietarios/solicitud/',
            data=json.dumps(frontend_data),
            content_type='application/json'
        )
        request.user = AnonymousUser()
        
        # Llamar a la vista directamente
        view = RegistroSolicitudPropietarioView()
        view.setup(request)
        
        try:
            self.stdout.write("\n🚀 Ejecutando vista...")
            response = view.post(request)
            
            self.stdout.write(f"📊 Status Code: {response.status_code}")
            
            if hasattr(response, 'data'):
                response_data = response.data
            else:
                response_data = json.loads(response.content.decode('utf-8'))
            
            self.stdout.write(f"📋 Respuesta:")
            self.stdout.write(json.dumps(response_data, indent=2, ensure_ascii=False))
            
            if response.status_code == 201:
                self.stdout.write(self.style.SUCCESS("\n✅ ¡SOLICITUD CREADA EXITOSAMENTE!"))
                
                # Verificar en la base de datos
                nueva_solicitud = SolicitudRegistroPropietario.objects.filter(
                    documento_identidad="88888888"
                ).first()
                
                if nueva_solicitud:
                    self.stdout.write(f"✅ Verificado en BD:")
                    self.stdout.write(f"   ID: {nueva_solicitud.pk}")
                    self.stdout.write(f"   Nombre: {nueva_solicitud.nombres} {nueva_solicitud.apellidos}")
                    self.stdout.write(f"   Estado: {nueva_solicitud.estado}")
                    self.stdout.write(f"   Email: {nueva_solicitud.email}")
                    
                    # Verificar que aparezca en el endpoint de admin
                    self.stdout.write("\n🔍 Verificando que aparezca en admin...")
                    self.verificar_en_admin()
                    
            else:
                self.stdout.write(self.style.ERROR(f"\n❌ Error al crear solicitud"))
                
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"💥 Error inesperado: {str(e)}"))
            import traceback
            self.stdout.write(f"Stack trace:\n{traceback.format_exc()}")

    def verificar_en_admin(self):
        """Verifica que la nueva solicitud aparezca en el endpoint de admin"""
        try:
            from rest_framework.test import APIRequestFactory
            from rest_framework_simplejwt.tokens import RefreshToken
            from authz.models import Usuario
            from authz.views_propietario import SolicitudesPendientesView
            
            # Obtener usuario admin
            admin_user = Usuario.objects.filter(
                roles__nombre__in=['Administrador', 'ADMIN']
            ).first()
            
            if not admin_user:
                self.stdout.write(self.style.ERROR("❌ No se encontró usuario admin"))
                return
            
            # Crear request autenticado
            factory = APIRequestFactory()
            request = factory.get('/api/authz/propietarios/admin/solicitudes/')
            
            # Simular autenticación JWT
            refresh = RefreshToken.for_user(admin_user)
            request.META['HTTP_AUTHORIZATION'] = f'Bearer {refresh.access_token}'
            request.user = admin_user
            
            # Llamar a la vista de admin
            view = SolicitudesPendientesView()
            view.setup(request)
            
            response = view.get(request)
            
            if response.status_code == 200:
                if hasattr(response, 'data'):
                    data = response.data
                else:
                    data = json.loads(response.content.decode('utf-8'))
                
                count = data.get('count', 0)
                results = data.get('results', [])
                
                self.stdout.write(f"✅ Endpoint admin responde: {count} solicitudes pendientes")
                
                # Buscar nuestra solicitud
                carlos_solicitud = None
                for solicitud in results:
                    if solicitud.get('nombres') == 'Carlos' and solicitud.get('apellidos') == 'Mendoza Vargas':
                        carlos_solicitud = solicitud
                        break
                
                if carlos_solicitud:
                    self.stdout.write(self.style.SUCCESS("✅ ¡SOLICITUD ENCONTRADA EN ADMIN!"))
                    self.stdout.write(f"   ID: {carlos_solicitud.get('id')}")
                    self.stdout.write(f"   Estado: {carlos_solicitud.get('estado')}")
                else:
                    self.stdout.write(self.style.ERROR("❌ Solicitud NO encontrada en admin"))
                    self.stdout.write("📋 Solicitudes actuales en admin:")
                    for sol in results:
                        self.stdout.write(f"   - {sol.get('nombres')} {sol.get('apellidos')} (ID: {sol.get('id')})")
            else:
                self.stdout.write(self.style.ERROR(f"❌ Error en endpoint admin: {response.status_code}"))
                
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"💥 Error verificando admin: {str(e)}"))
            import traceback
            self.stdout.write(f"Stack trace:\n{traceback.format_exc()}")