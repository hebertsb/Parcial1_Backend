"""
URLs específicas para el registro de propietarios
"""
from django.urls import path
from .views_propietario import (
    RegistroSolicitudPropietarioView, 
    StatusSolicitudView,
    SolicitudesPendientesView,
    AprobarSolicitudView,
    RechazarSolicitudView,
    DetalleSolicitudView
)

urlpatterns = [
    # URLs públicas para solicitud de registro
    path('solicitud/', RegistroSolicitudPropietarioView.as_view(), name='registro-solicitud-propietario'),
    path('solicitud/status/<str:token>/', StatusSolicitudView.as_view(), name='status-solicitud'),
    
    # URLs para administración (requieren autenticación de admin)
    path('admin/solicitudes/', SolicitudesPendientesView.as_view(), name='solicitudes-pendientes'),
    path('admin/solicitudes/<int:solicitud_id>/', DetalleSolicitudView.as_view(), name='detalle-solicitud'),
    path('admin/solicitudes/<int:solicitud_id>/aprobar/', AprobarSolicitudView.as_view(), name='aprobar-solicitud'),
    path('admin/solicitudes/<int:solicitud_id>/rechazar/', RechazarSolicitudView.as_view(), name='rechazar-solicitud'),
]