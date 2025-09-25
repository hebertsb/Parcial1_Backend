from django.urls import path
from .views import EspacioComunViewSet, DisponibilidadEspacioComunViewSet

app_name = 'areas_comunes'

urlpatterns = [
    # Espacios Comunes
    path('espacios-comunes/', EspacioComunViewSet.as_view({'get': 'list', 'post': 'create'}), name='espacios-comunes-list-create'),
    path('espacios-comunes/<int:pk>/', EspacioComunViewSet.as_view({'get': 'retrieve', 'put': 'update', 'delete': 'destroy'}), name='espacios-comunes-detail'),
    
    # Disponibilidad de Espacios Comunes
    path('disponibilidad-espacio-comun/', DisponibilidadEspacioComunViewSet.as_view({'get': 'list', 'post': 'create'}), name='disponibilidad-espacio-comun-list-create'),
    path('disponibilidad-espacio-comun/<int:pk>/', DisponibilidadEspacioComunViewSet.as_view({'get': 'retrieve', 'put': 'update', 'delete': 'destroy'}), name='disponibilidad-espacio-comun-detail'),
]
