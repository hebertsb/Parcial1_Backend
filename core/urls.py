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
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
    TokenVerifyView,
)
from drf_spectacular.views import (
    SpectacularAPIView,
    SpectacularSwaggerView,
    SpectacularRedocView,
)

urlpatterns = [
    # Admin
    path('admin/', admin.site.urls),
    
    # Authz Authentication + Propietarios
    path('api/authz/', include('authz.auth_urls')),   # login, usuarios, refresh
    path('api/authz/', include('authz.urls')),        # registro, panel propietarios
    
    # JWT Authentication (Sistema anterior - mantener para compatibilidad)
    path('api/auth/login/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/auth/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('api/auth/verify/', TokenVerifyView.as_view(), name='token_verify'),
    
    # Pagos (Expensas y Multas)
    path('api/pagos/', include('core.api_urls')),

    # CU05 - Gestionar Unidades Habitacionales
    path('api/', include('core.api.viviendas.urls')),

    
    path('api/', include('core.api.mascotas.urls')),
    

    # OpenAPI Schema
    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
    path('api/docs/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
    path('api/redoc/', SpectacularRedocView.as_view(url_name='schema'), name='redoc'),
    
    # Face Recognition API
    path('', include('seguridad.urls')),

       # Rutas para Expensas y Multas (CRUD)
    path('api/pagos/', include('expensas_multas.urls')),

        # Rutas para Avisos y Comunicados (CRUD)

    path('api/avisos/', include('avisos_comunicados.urls')),
    #gestion de espacios comunes(crud)
    path('api/areas-comunes/', include('areas_comunes.urls')),

    # Rutas para la gestión de áreas comunes (crud)
    path('api/areas-comunes/', include('reservas_areas.urls')),

]

# Servir archivos media en desarrollo
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)





