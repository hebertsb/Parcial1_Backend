from django.urls import path
from .views import ReservaEspacioViewSet

app_name = 'reservas_areas'

urlpatterns = [
    path('reservas/', ReservaEspacioViewSet.as_view({'get': 'list', 'post': 'create'}), name='reservas-list-create'),
    path('reservas/<int:pk>/', ReservaEspacioViewSet.as_view({'get': 'retrieve', 'put': 'update', 'delete': 'destroy'}), name='reservas-detail'),
]
