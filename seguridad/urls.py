"""
URLs for Face Recognition API
"""

from django.urls import path, include
from django.shortcuts import render
from .views import (
    FaceEnrollView, FaceVerifyView, FaceDeleteView, FaceStatusView, ListarUsuariosReconocimientoFacialView,
    DashboardSeguridadView, IncidentesSeguridadView, VisitasActivasView, 
    AlertasActivasView, ListaUsuariosActivosView
)

app_name = 'seguridad'

# Vista para el panel del guardia - usando versión temporal
from . import facial_recognition_views_temp

def panel_guardia(request):
    return facial_recognition_views_temp.panel_guardia(request)

urlpatterns = [
    # Face Recognition Endpoints originales
    path('api/faces/enroll/', FaceEnrollView.as_view(), name='face-enroll'),
    path('api/faces/verify/', FaceVerifyView.as_view(), name='face-verify'),
    path('api/faces/enroll/<int:copropietario_id>/', FaceDeleteView.as_view(), name='face-delete'),
    path('api/faces/status/<int:copropietario_id>/', FaceStatusView.as_view(), name='face-status'),
    
    # Panel del guardia (interfaz web)
    path('panel-guardia/', panel_guardia, name='panel-guardia'),
    
    # Lista de usuarios con reconocimiento facial
    path('api/usuarios-reconocimiento/', ListarUsuariosReconocimientoFacialView.as_view(), name='usuarios-reconocimiento'),
    
    # === ENDPOINTS DEL DASHBOARD DE SEGURIDAD ===
    path('api/dashboard/', DashboardSeguridadView.as_view(), name='dashboard-seguridad'),
    path('api/incidentes/', IncidentesSeguridadView.as_view(), name='incidentes-seguridad'),
    path('api/visitas/activas/', VisitasActivasView.as_view(), name='visitas-activas'),
    path('api/alertas/activas/', AlertasActivasView.as_view(), name='alertas-activas'),
    path('api/lista-usuarios-activos/', ListaUsuariosActivosView.as_view(), name='lista-usuarios-activos'),
    
    # APIs para reconocimiento facial del guardia
    path('', include('seguridad.facial_urls')),
]
