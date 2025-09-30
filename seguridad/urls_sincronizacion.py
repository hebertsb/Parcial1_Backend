"""
URLs para sincronización de reconocimiento facial entre sistemas
"""

from django.urls import path
from . import views_sincronizacion

# Sin app_name para evitar conflicto de namespaces cuando se incluye en api_urls.py

urlpatterns = [
    # Sincronización individual de propietario
    path('', views_sincronizacion.sincronizar_fotos_propietario, name='sincronizar-propietario'),
    
    # Estadísticas de sincronización
    path('estadisticas/', views_sincronizacion.estadisticas_sincronizacion, name='estadisticas-sincronizacion'),
    
    # Sincronización masiva
    path('todos/', views_sincronizacion.sincronizar_todos_usuarios, name='sincronizar-todos'),
]