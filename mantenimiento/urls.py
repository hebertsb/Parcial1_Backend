from django.urls import path
from .views import MantenimientoViewSet, TareaMantenimientoViewSet

app_name = 'mantenimiento'

urlpatterns = [
    # Rutas para Mantenimiento (crear y consultar)
    path('mantenimientos/', MantenimientoViewSet.as_view({'get': 'list', 'post': 'create'}), name='mantenimientos-list-create'),
    path('mantenimientos/<int:pk>/', MantenimientoViewSet.as_view({'get': 'retrieve'}), name='mantenimientos-detail'),  # Solo consultar
    # Acciones adicionales
    path('mantenimientos/<int:pk>/cerrar/', MantenimientoViewSet.as_view({'post': 'cerrar'}), name='mantenimientos-cerrar'),
    path('api/mantenimiento/tareas-mantenimiento/', TareaMantenimientoViewSet.as_view({'get': 'list', 'post': 'create'}), name='tareas-mantenimiento-list-create'),

    # Rutas para las Tareas de Mantenimiento
    path('tareas-mantenimiento/', TareaMantenimientoViewSet.as_view({'get': 'list', 'post': 'create'}), name='tareas-mantenimiento-list-create'),
    path('tareas-mantenimiento/<int:pk>/', TareaMantenimientoViewSet.as_view({'get': 'retrieve', 'put': 'update', 'delete': 'destroy'}), name='tareas-mantenimiento-detail'),
    path('tareas-mantenimiento/<int:pk>/completar/', TareaMantenimientoViewSet.as_view({'post': 'completar'}), name='tareas-mantenimiento-completar'),
]

