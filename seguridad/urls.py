"""
URLs for Face Recognition API
"""

from django.urls import path, include
from .views import (
    FaceEnrollView, FaceVerifyView, FaceDeleteView, FaceStatusView, ListarUsuariosReconocimientoFacialView,
    DashboardSeguridadView, IncidentesSeguridadView, VisitasActivasView, 
    AlertasActivasView, ListaUsuariosActivosView, PropietariosConReconocimientoView,
    ReconocerTiempoRealView, HealthCheckView
)

app_name = 'seguridad'

# Vista para el panel del guardia - usando versión temporal
from . import facial_recognition_views_temp

def panel_guardia(request):
    return facial_recognition_views_temp.panel_guardia(request)
#subete

urlpatterns = [
    # Face Recognition Endpoints originales
    path('api/faces/enroll/', FaceEnrollView.as_view(), name='face-enroll'),
    path('api/faces/verify/', FaceVerifyView.as_view(), name='face-verify'),
    path('api/faces/enroll/<int:copropietario_id>/', FaceDeleteView.as_view(), name='face-delete'),
    path('api/faces/status/<int:copropietario_id>/', FaceStatusView.as_view(), name='face-status'),
    
    # NUEVO: Reconocimiento en tiempo real con cámara web
    path('api/reconocer-tiempo-real/', ReconocerTiempoRealView.as_view(), name='reconocer-tiempo-real'),
    
    # Health Check
    path('api/health/', HealthCheckView.as_view(), name='health-check'),
    
    # Panel del guardia (interfaz web)
    path('panel-guardia/', panel_guardia, name='panel-guardia'),
    
    # Lista de usuarios con reconocimiento facial
    path('api/usuarios-reconocimiento/', ListarUsuariosReconocimientoFacialView.as_view(), name='usuarios-reconocimiento'),
    
    # Lista específica de propietarios con reconocimiento facial
    path('api/propietarios-reconocimiento/', PropietariosConReconocimientoView.as_view(), name='propietarios-reconocimiento'),
    
    # === ENDPOINTS DE SINCRONIZACIÓN ===
    path('api/sincronizar-fotos/', include('seguridad.urls_sincronizacion')),
    
    # === ENDPOINTS DEL DASHBOARD DE SEGURIDAD ===
    path('api/dashboard/', DashboardSeguridadView.as_view(), name='dashboard-seguridad'),
    path('api/incidentes/', IncidentesSeguridadView.as_view(), name='incidentes-seguridad'),
    path('api/visitas/activas/', VisitasActivasView.as_view(), name='visitas-activas'),
    path('api/alertas/activas/', AlertasActivasView.as_view(), name='alertas-activas'),
    path('api/lista-usuarios-activos/', ListaUsuariosActivosView.as_view(), name='lista-usuarios-activos'),
    
    # APIs para reconocimiento facial del guardia
    path('', include('seguridad.facial_urls')),
]
