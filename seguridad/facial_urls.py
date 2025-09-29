# URLs para el sistema de reconocimiento facial
from django.urls import path
from . import facial_recognition_views_temp as facial_recognition_views

app_name = 'reconocimiento_facial'

urlpatterns = [
    # Endpoint principal de reconocimiento facial simulado
    path('reconocimiento-facial/', 
         facial_recognition_views.reconocimiento_facial_simulado, 
         name='reconocimiento_facial'),
    
    # Lista completa de usuarios con reconocimiento activo
    path('lista-usuarios-activos/', 
         facial_recognition_views.lista_usuarios_reconocimiento, 
         name='lista_usuarios_activos'),
    
    # Búsqueda de usuarios
    path('buscar-usuarios/', 
         facial_recognition_views.buscar_usuarios_reconocimiento, 
         name='buscar_usuarios'),
    
    # Estadísticas para dashboard
    path('estadisticas/', 
         facial_recognition_views.estadisticas_reconocimiento, 
         name='estadisticas'),
]