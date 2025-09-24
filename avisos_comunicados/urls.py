from django.urls import path
from .views import AvisosPersonalizadosViewSet, ComunicadosAdministracionViewSet

app_name = 'avisos_comunicados'

urlpatterns = [
    path('avisos-personalizados/', AvisosPersonalizadosViewSet.as_view({'get': 'list', 'post': 'create'}), name='avisos-personalizados-list-create'),
    path('avisos-personalizados/<int:pk>/', AvisosPersonalizadosViewSet.as_view({'get': 'retrieve', 'put': 'update', 'delete': 'destroy'}), name='avisos-personalizados-detail'),
    path('comunicados-administracion/', ComunicadosAdministracionViewSet.as_view({'get': 'list', 'post': 'create'}), name='comunicados-administracion-list-create'),
    path('comunicados-administracion/<int:pk>/', ComunicadosAdministracionViewSet.as_view({'get': 'retrieve', 'put': 'update', 'delete': 'destroy'}), name='comunicados-administracion-detail'),
]

