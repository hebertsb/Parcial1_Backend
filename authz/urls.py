"""
URLs para el sistema de autenticación y autorización
"""
from django.urls import path, include
from .views_propietario import (
    RegistroPropietarioInicialView,
    SolicitudesPendientesView,
    DetalleSolicitudView,
    AprobarSolicitudView,
    RechazarSolicitudView
)

print("🔍 DEBUG: Cargando authz/urls.py")

app_name = 'authz'

urlpatterns = [
    # Registro inicial de propietario (formulario web principal)
    path('propietarios/registro-inicial/', RegistroPropietarioInicialView.as_view(), name='registro-inicial'),
    
    # URLs para administradores
    path('propietarios/admin/solicitudes/', SolicitudesPendientesView.as_view(), name='solicitudes-pendientes'),
    path('propietarios/admin/solicitudes/<int:solicitud_id>/', DetalleSolicitudView.as_view(), name='detalle-solicitud'),
    path('propietarios/admin/solicitudes/<int:solicitud_id>/aprobar/', AprobarSolicitudView.as_view(), name='aprobar-solicitud'),
    path('propietarios/admin/solicitudes/<int:solicitud_id>/rechazar/', RechazarSolicitudView.as_view(), name='rechazar-solicitud'),
    
    # URLs para el panel de propietarios (gestión de familiares e inquilinos)
    path('propietarios/', include('authz.urls_propietarios_panel')),
]

print("🔍 DEBUG: URLs de authz cargadas exitosamente")