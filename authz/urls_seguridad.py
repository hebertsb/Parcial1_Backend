"""
URLs para el panel de seguridad - Gestión de reconocimiento facial
"""
from django.urls import path
from .views_seguridad import (
    ListarUsuariosConFotosView,
    DetalleUsuarioFotosView,
    EstadisticasReconocimientoView
)

urlpatterns = [
    # Panel de seguridad - Gestión de usuarios con reconocimiento facial
    path('usuarios-con-fotos/', ListarUsuariosConFotosView.as_view(), name='listar-usuarios-con-fotos'),
    path('usuario-fotos/<int:copropietario_id>/', DetalleUsuarioFotosView.as_view(), name='detalle-usuario-fotos'),
    path('estadisticas-reconocimiento/', EstadisticasReconocimientoView.as_view(), name='estadisticas-reconocimiento'),
]