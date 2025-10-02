"""
URL configuration for core project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
# JWT views removidas - usando sistema authz personalizado
from drf_spectacular.views import (
    SpectacularAPIView,
    SpectacularSwaggerView,
    SpectacularRedocView,
)
# from core.views import DemoView, HealthCheckView  # DESHABILITADO: core app comentada
from core.test_views import health_check, simple_test

urlpatterns = [
    # Health Check para Railway - TEMPORALMENTE DESHABILITADO
    # path('api/health/', HealthCheckView.as_view(), name='health-check'),
    # Test endpoints temporales
    path('api/test/health/', health_check, name='test-health'),
    path('api/test/simple/', simple_test, name='test-simple'),
    
    # Admin
    path('admin/', admin.site.urls),
    
    # Demo básico - TEMPORALMENTE DESHABILITADO
    # path('api/demo/', DemoView.as_view(), name='demo-basico'),
    
    # AUTHZ TEMPORALMENTE DESHABILITADO PARA DIAGNOSTICAR ERROR 500
    # path('api/authz/', include('authz.auth_urls')),   # login, usuarios, refresh
    # path('api/authz/', include(('authz.urls', 'authz'), namespace='authz-api')),        # registro, panel propietarios
    # path('api/authz/', include('authz.urls_admin')),  # funcionalidades administrativas
    # path('authz/', include('authz.auth_urls')),       # /authz/login/, /authz/refresh/
    # path('authz/', include(('authz.urls', 'authz'), namespace='authz-direct')),            # registro, panel propietarios
    # path('authz/', include('authz.urls_admin')),      # funcionalidades administrativas
    # path('auth/', include('authz.auth_urls')),        # login, refresh compatibilidad
    # path('auth/', include('authz.urls_admin')),       # admin endpoints sin api/ prefix
    
    # JWT Authentication: REMOVIDO - usando sistema authz personalizado
    # El login funcional está en /api/authz/login/ y /auth/login/
    
    # TEMPORALMENTE DESHABILITADO PARA DIAGNOSTICAR ERROR 500
    # Pagos (Expensas y Multas)
    # path('api/pagos/', include('core.api_urls')),

    # CU05 - Gestionar Unidades Habitacionales  
    # path('api/', include('core.api.viviendas.urls')),
    # path('api/', include('core.api.mascotas.urls')),

    # OpenAPI Schema
    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
    path('api/docs/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
    path('api/redoc/', SpectacularRedocView.as_view(url_name='schema'), name='redoc'),
    
    # API de Seguridad - TEMPORALMENTE DESHABILITADO
    # path('api/seguridad/', include('seguridad.api_urls')),
    # path('seguridad/', include('seguridad.api_urls')),
    
    # WebRTC - Endpoints para reconocimiento facial en tiempo real
    path('webrtc/', include('seguridad.urls_webrtc')),
    
    # Actividad y Logs de Seguridad - Endpoints para el panel de actividades
    path('api/authz/seguridad/', include('seguridad.urls_actividad')),
    path('api/seguridad/', include('seguridad.urls_actividad')),  # URL alternativa
    
    # Entrenamiento de IA - Endpoints para gestión de modelos
    # TEMPORALMENTE COMENTADO PARA RAILWAY - Requiere dependencias ML
    # path('api/seguridad/', include('seguridad.urls_ai_training')),

    # #expensas
    # path('api/expensas/', include('expensas_multas.urls')),

     # Rutas para Expensas y Multas (CRUD) - Temporalmente comentado por error firebase_admin
    # path('api/pagos/', include('expensas_multas.urls')),

        # Rutas para Avisos y Comunicados (CRUD)

    path('api/avisos/', include('avisos_comunicados.urls')),
    #gestion de espacios comunes(crud)
    path('api/areas-comunes/', include('areas_comunes.urls')),

    # TEMPORALMENTE DESHABILITADO - DIAGNOSTICAR ERROR 500
    # path('api/avisos/', include('avisos_comunicados.urls')),
    # path('api/areas-comunes/', include('areas_comunes.urls')),
    # path('api/', include('core.api.visitas.urls')),
    # path('api/bitacora/', include('core.api.bitacora.urls')),
    # path('api/areas-comunes/', include('reservas_areas.urls')),
    # TEMPORALMENTE DESHABILITADO - DIAGNOSTICAR ERROR 500
    # path('api/mantenimiento/', include('mantenimiento.urls')),
    # path('api/politicas/', include('politicas.urls')),

    
]

# Servir archivos media en desarrollo
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)





