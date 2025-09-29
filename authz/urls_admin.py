"""
URLs para funcionalidades administrativas de usuarios
"""

from django.urls import path
from .views_admin import (
    CrearUsuarioSeguridadAPIView,
    ListarUsuariosSeguridadAPIView,
    ActualizarEstadoUsuarioSeguridadAPIView,
    ResetPasswordSeguridadAPIView,
    ListarPropietariosAdminAPIView,
    EditarPropietarioAdminAPIView
)

urlpatterns = [
    # Gestión de usuarios de seguridad
    path(
        'admin/seguridad/crear/', 
        CrearUsuarioSeguridadAPIView.as_view(), 
        name='admin-crear-usuario-seguridad'
    ),
    path(
        'admin/seguridad/listar/', 
        ListarUsuariosSeguridadAPIView.as_view(), 
        name='admin-listar-usuarios-seguridad'
    ),
    path(
        'admin/seguridad/<int:usuario_id>/estado/', 
        ActualizarEstadoUsuarioSeguridadAPIView.as_view(), 
        name='admin-actualizar-estado-seguridad'
    ),
    path(
        'admin/seguridad/<int:usuario_id>/reset-password/', 
        ResetPasswordSeguridadAPIView.as_view(), 
        name='admin-reset-password-seguridad'
    ),
    
    # Gestión de propietarios
    path(
        'admin/propietarios/listar/', 
        ListarPropietariosAdminAPIView.as_view(), 
        name='admin-listar-propietarios'
    ),
    path(
        'admin/propietarios/<int:usuario_id>/editar/', 
        EditarPropietarioAdminAPIView.as_view(), 
        name='admin-editar-propietario'
    ),
]