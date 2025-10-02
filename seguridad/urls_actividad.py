# seguridad/urls_actividad.py - URLs para endpoints de actividad de seguridad
from django.urls import path
from . import views_actividad

app_name = 'seguridad_actividad'

urlpatterns = [
    # ===================================================
    # ENDPOINTS PRINCIPALES PARA EL FRONTEND
    # ===================================================
    
    # Logs de acceso (endpoint principal)
    path('acceso/logs/', views_actividad.logs_acceso, name='logs-acceso'),
    
    # Actividad reciente (endpoint alternativo)
    path('actividad/reciente/', views_actividad.actividad_reciente, name='actividad-reciente'),
    
    # Incidentes de seguridad
    path('incidentes/', views_actividad.incidentes_seguridad, name='incidentes-seguridad'),
    
    # Dashboard con estadísticas
    path('dashboard/', views_actividad.dashboard_estadisticas, name='dashboard-estadisticas'),
    
    # Visitas activas
    path('visitas/activas/', views_actividad.visitas_activas, name='visitas-activas'),
    
    # ===================================================
    # ENDPOINTS AUXILIARES (DESARROLLO)
    # ===================================================
    
    # Crear logs de prueba (solo desarrollo)
    path('logs/crear-prueba/', views_actividad.crear_log_prueba, name='crear-log-prueba'),
]