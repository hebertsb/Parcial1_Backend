"""
URLs específicas para la API de Seguridad
Solo endpoints del API sin namespace para evitar conflictos
"""

from django.urls import path, include
from .views import (
    ListarUsuariosReconocimientoFacialView, PropietariosConReconocimientoView,
    FaceEnrollView, FaceVerifyView, DashboardSeguridadView, IncidentesSeguridadView,
    VisitasActivasView, AlertasActivasView, ListaUsuariosActivosView, FaceStatusView,
    HealthCheckView
)
from .views_verificacion_tiempo_real import VerificacionFacialEnTiempoRealView

# Sin app_name para evitar conflicto de namespaces

urlpatterns = [
    # Health check - sin autenticación para testing
    path('health/', HealthCheckView.as_view(), name='api-health-check'),
    
    # Usuarios con reconocimiento facial
    path('usuarios-reconocimiento/', ListarUsuariosReconocimientoFacialView.as_view(), name='api-usuarios-reconocimiento'),
    
    # Propietarios específicamente con reconocimiento facial  
    path('propietarios-reconocimiento/', PropietariosConReconocimientoView.as_view(), name='api-propietarios-reconocimiento'),
    
    # Reconocimiento facial - enrollamiento y verificación
    path('reconocimiento-facial/enroll/', FaceEnrollView.as_view(), name='api-face-enroll'),
    path('reconocimiento-facial/verify/', FaceVerifyView.as_view(), name='api-face-verify'),
    path('reconocimiento-facial/status/<int:copropietario_id>/', FaceStatusView.as_view(), name='api-face-status'),
    
    # Dashboard y monitoreo
    path('dashboard/', DashboardSeguridadView.as_view(), name='api-dashboard-seguridad'),
    path('incidentes/', IncidentesSeguridadView.as_view(), name='api-incidentes-seguridad'),
    path('visitas/activas/', VisitasActivasView.as_view(), name='api-visitas-activas'),
    path('alertas/activas/', AlertasActivasView.as_view(), name='api-alertas-activas'),
    path('usuarios-activos/', ListaUsuariosActivosView.as_view(), name='api-usuarios-activos'),
    
    # Sincronización de fotos (incluir las URLs del archivo existente)
    path('sincronizar-fotos/', include('seguridad.urls_sincronizacion')),
    
    # Verificación facial en tiempo real (simulador para testing)
    path('verificacion-tiempo-real/', VerificacionFacialEnTiempoRealView.as_view(), name='api-verificacion-tiempo-real'),
]