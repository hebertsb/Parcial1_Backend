from .views_acceso import ListarAccesosCondominioAPIView
"""
URLs para el sistema de autenticación y autorización
"""
from django.urls import path, include
from .views_propietario import (
    RegistroPropietarioInicialView,
    RegistroSolicitudPropietarioView,
    SolicitudesPendientesView,
    DetalleSolicitudView,
    AprobarSolicitudView,
    RechazarSolicitudView,
    DetallePropietarioView,
    MiInformacionPropietarioView,
    MisFotosPropietarioView,
    SubirFotoPropietarioView
)
from .views_fotos_reconocimiento import (
    subir_fotos_reconocimiento,
    estado_reconocimiento_facial,
    eliminar_reconocimiento_facial
)
from .views_fotos_reconocimiento_corregido import (
    subir_fotos_reconocimiento_corregido,
    estado_reconocimiento_facial_corregido,
    obtener_fotos_reconocimiento_corregido
)
from .views_diagnostico import diagnostico_endpoint
from .views_seguridad_usuarios import usuarios_con_reconocimiento

app_name = 'authz'

urlpatterns = [
    # Registro inicial de propietario (formulario web principal)
    path('propietarios/registro-inicial/', RegistroPropietarioInicialView.as_view(), name='registro-inicial'),
    
    # Endpoint para crear nueva solicitud (compatible con frontend React/Next.js)
    path('propietarios/solicitud-registro/', RegistroSolicitudPropietarioView.as_view(), name='crear-solicitud'),
    
    # URLs para administradores
    path('propietarios/admin/solicitudes/', SolicitudesPendientesView.as_view(), name='solicitudes-pendientes'),
    path('propietarios/admin/solicitudes/<int:solicitud_id>/', DetalleSolicitudView.as_view(), name='detalle-solicitud'),
    path('propietarios/admin/solicitudes/<int:solicitud_id>/aprobar/', AprobarSolicitudView.as_view(), name='aprobar-solicitud'),
    path('propietarios/admin/solicitudes/<int:solicitud_id>/rechazar/', RechazarSolicitudView.as_view(), name='rechazar-solicitud'),
    
    # URLs para el panel de propietarios (gestión de familiares e inquilinos)
    path('propietarios/panel/', include('authz.urls_propietarios_panel')),
    
    # URLs para funcionalidades administrativas
    path('', include('authz.urls_admin')),
    # Endpoint de detalle de propietario por ID
    path('propietarios/<int:propietario_id>/', DetallePropietarioView.as_view(), name='detalle-propietario'),
    
    # ===== PANEL PROPIETARIO - AUTENTICADO =====
    path('propietarios/mi-informacion/', MiInformacionPropietarioView.as_view(), name='mi-informacion-propietario'),
    path('propietarios/mis-fotos/', MisFotosPropietarioView.as_view(), name='mis-fotos-propietario'),
    path('propietarios/subir-foto/', SubirFotoPropietarioView.as_view(), name='subir-foto-propietario'),
    
    # ===== PANEL SEGURIDAD - AUTENTICADO =====
    path('seguridad/', include('authz.urls_seguridad')),
    
    # ===== ENDPOINTS PARA RECONOCIMIENTO FACIAL =====
    # IMPORTANTE: Usar prefijo diferente para evitar conflicto con router /usuarios/
    
    # Endpoint de diagnóstico temporal
    path('reconocimiento/diagnostico/', diagnostico_endpoint, name='diagnostico-endpoint'),
    
    # Endpoints CORREGIDOS - buscan usuarios con rol 'Propietario'
    path('reconocimiento/fotos/', subir_fotos_reconocimiento_corregido, name='subir-fotos-reconocimiento'),
    path('reconocimiento/fotos/<int:usuario_id>/', obtener_fotos_reconocimiento_corregido, name='obtener-fotos-reconocimiento'),
    path('reconocimiento/estado/', estado_reconocimiento_facial_corregido, name='estado-reconocimiento'),
    
    # Endpoint para seguridad - Lista usuarios con reconocimiento
    path('seguridad/usuarios-reconocimiento/', usuarios_con_reconocimiento, name='usuarios-con-reconocimiento'),
    
    # Endpoints originales (mantener como backup)
    path('reconocimiento/fotos-original/', subir_fotos_reconocimiento, name='subir-fotos-original'),
    path('reconocimiento/eliminar/', eliminar_reconocimiento_facial, name='eliminar-reconocimiento'),
]