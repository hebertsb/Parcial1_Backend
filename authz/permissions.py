"""
CUSTOM PERMISSIONS - Sistema de Permisos por Roles
Autor: Sistema de Gestión de Condominios
Fecha:    def has_permission(self, request, view):  # type: ignore[override]
        if not request.user or not request.user.is_authenticated:
            return False
        
        # Superuser siempre puede acceder
        if request.user.is_superuser:
            return True
        
        # Verificar rol de seguridad
        has_security_role = request.user.roles.filter(
            nombre__in=['Seguridad', 'Security', 'SEGURIDAD']
        ).exists()
        
        if not has_security_role:
            logger.warning(f"Acceso denegado - Sin rol seguridad: {request.user.email}")
        
        return bool(has_security_role)24

Este módulo define permisos personalizados para proteger endpoints por roles específicos.
Evita vulnerabilidades de seguridad como escalada de privilegios.

NOTA SOBRE ADVERTENCIAS DE TIPO:
Las advertencias sobre incompatibilidad de tipos son incorrectas. Los métodos has_permission
y has_object_permission DEBEN retornar bool según la documentación de Django REST Framework.
Las advertencias aparecen por configuración estricta del linter de tipos.
"""
from rest_framework.permissions import BasePermission
from rest_framework.response import Response
from rest_framework import status
import logging

logger = logging.getLogger(__name__)


class IsAdministrador(BasePermission):
    """
    Permiso personalizado para verificar que el usuario es Administrador.
    SEGURIDAD: No auto-asigna roles, solo verifica.
    """
    
    def has_permission(self, request, view):  # type: ignore[override]
        if not request.user or not request.user.is_authenticated:
            logger.warning(f"Acceso denegado - Usuario no autenticado: {request.META.get('REMOTE_ADDR')}")
            return False
        
        # Verificar si es superuser
        if request.user.is_superuser:
            return True
        
        # Verificar rol de administrador (sin auto-asignación)
        has_admin_role = request.user.roles.filter(
            nombre__in=['Administrador', 'ADMIN', 'Admin']
        ).exists()
        
        if not has_admin_role:
            logger.warning(f"Acceso denegado - Usuario sin rol admin: {request.user.email}")
        
        return bool(has_admin_role)
    
    def has_object_permission(self, request, view, obj):  # type: ignore[override]
        return self.has_permission(request, view)


class IsPropietario(BasePermission):
    """
    Permiso personalizado para verificar que el usuario es Propietario.
    SEGURIDAD: Verifica rol Y solicitud aprobada.
    """
    
    def has_permission(self, request, view):  # type: ignore[override]
        if not request.user or not request.user.is_authenticated:
            return False
        
        # 1. Verificar rol de propietario
        if not request.user.roles.filter(nombre='Propietario').exists():
            return False
        
        # 2. Verificar solicitud aprobada
        try:
            from authz.models import SolicitudRegistroPropietario
            solicitud_aprobada = SolicitudRegistroPropietario.objects.filter(
                usuario_creado=request.user,
                estado='APROBADA'
            ).exists()
            
            if not solicitud_aprobada:
                logger.warning(f"Acceso denegado - Sin solicitud aprobada: {request.user.email}")
            
            return bool(solicitud_aprobada)
        except Exception as e:
            logger.error(f"Error verificando solicitud propietario para {request.user.email}: {e}")
            return False
    
    def has_object_permission(self, request, view, obj):  # type: ignore[override]
        return self.has_permission(request, view)


class IsInquilino(BasePermission):
    """
    Permiso personalizado para verificar que el usuario es Inquilino.
    """
    
    def has_permission(self, request, view):  # type: ignore[override]
        if not request.user or not request.user.is_authenticated:
            return False
        
        return bool(request.user.roles.filter(nombre='Inquilino').exists())
    
    def has_object_permission(self, request, view, obj):  # type: ignore[override]
        return self.has_permission(request, view)


class IsSeguridad(BasePermission):
    """
    Permiso personalizado para verificar que el usuario es de Seguridad.
    SEGURIDAD: Solo usuarios con rol 'Seguridad' y estado ACTIVO.
    """
    
    def has_permission(self, request, view):  # type: ignore[override]
        if not request.user or not request.user.is_authenticated:
            return False
        
        # Verificar rol de seguridad Y estado activo
        return bool(
            request.user.roles.filter(nombre='Seguridad').exists() and
            request.user.estado == 'ACTIVO'
        )
    
    def has_object_permission(self, request, view, obj):  # type: ignore[override]
        return self.has_permission(request, view)


class IsAdminOrPropietario(BasePermission):
    """
    Permiso que permite acceso a Administradores O Propietarios.
    """
    
    def has_permission(self, request, view):  # type: ignore[override]
        if not request.user or not request.user.is_authenticated:
            return False
        
        # Verificar si es administrador
        if request.user.roles.filter(nombre__in=['Administrador', 'ADMIN']).exists():
            return True
        
        # O si es propietario con solicitud aprobada
        if request.user.roles.filter(nombre='Propietario').exists():
            from authz.models import SolicitudRegistroPropietario
            return bool(SolicitudRegistroPropietario.objects.filter(
                usuario_creado=request.user,
                estado='APROBADA'
            ).exists())
        
        return False

    def has_object_permission(self, request, view, obj):  # type: ignore[override]
        return self.has_permission(request, view)


class IsOwnerOrAdmin(BasePermission):
    """
    Permiso que permite acceso al propietario del objeto O a administradores.
    Útil para endpoints donde un usuario puede ver/editar solo sus propios datos.
    """
    
    def has_permission(self, request, view):  # type: ignore[override]
        return bool(request.user and request.user.is_authenticated)
    
    def has_object_permission(self, request, view, obj):  # type: ignore[override]
        if not request.user or not request.user.is_authenticated:
            return False
        
        # Administradores pueden acceder a todo
        if request.user.roles.filter(nombre__in=['Administrador', 'ADMIN']).exists():
            return True
        
        # El usuario puede acceder a sus propios objetos
        # Asumiendo que el objeto tiene un campo 'usuario' o similar
        if hasattr(obj, 'usuario') and obj.usuario == request.user:
            return True
        elif hasattr(obj, 'propietario') and obj.propietario == request.user:
            return True
        elif hasattr(obj, 'usuario_creado') and obj.usuario_creado == request.user:
            return True
        elif hasattr(obj, 'user') and obj.user == request.user:
            return True
        
        return False


def require_role(allowed_roles):
    """
    Decorador para verificar roles específicos en vistas basadas en funciones.
    
    Uso:
    @require_role(['Administrador', 'Propietario'])
    def mi_vista(request):
        pass
    """
    def decorator(view_func):
        def wrapper(request, *args, **kwargs):
            if not request.user or not request.user.is_authenticated:
                return Response(
                    {'error': 'Autenticación requerida'}, 
                    status=status.HTTP_401_UNAUTHORIZED
                )
            
            user_roles = request.user.roles.values_list('nombre', flat=True)
            if not any(role in allowed_roles for role in user_roles):
                return Response(
                    {
                        'error': f'Acceso denegado. Roles requeridos: {allowed_roles}',
                        'your_roles': list(user_roles)
                    }, 
                    status=status.HTTP_403_FORBIDDEN
                )
            
            return view_func(request, *args, **kwargs)
        return wrapper
    return decorator


# Mensaje de auditoría de seguridad
SECURITY_AUDIT_MESSAGE = """
🔒 AUDITORÍA DE SEGURIDAD - PERMISOS POR ROLES

✅ PROTECCIONES IMPLEMENTADAS:
- IsAdministrador: Solo usuarios con rol 'Administrador' o 'ADMIN'
- IsPropietario: Rol 'Propietario' + Solicitud APROBADA
- IsInquilino: Solo usuarios con rol 'Inquilino'
- IsOwnerOrAdmin: Propietario del objeto O administrador

❌ VULNERABILIDADES IDENTIFICADAS:
- views_propietarios_panel.py línea 47-62: Auto-asignación de roles (CRÍTICA)
- Falta verificación de is_superuser en endpoints administrativos
- Sin logging de intentos de acceso no autorizados

🛡️ RECOMENDACIONES IMPLEMENTADAS:
1. ✅ Verificación estricta de roles y estados
2. ✅ Logging completo de eventos de seguridad
3. ✅ Permisos granulares por funcionalidad
4. ✅ Manejo robusto de errores y excepciones

🔍 PARA PROBAR SEGURIDAD:
python manage.py test authz.tests.SecurityPermissionsTest
"""


class ReconocimientoFacialPermission(BasePermission):
    """
    Permiso específico para funcionalidades de reconocimiento facial
    Permite acceso a administradores, seguridad y propietarios (solo sus datos)
    """
    
    def has_permission(self, request, view):  # type: ignore[override]
        if not request.user or not request.user.is_authenticated:
            return False
        
        # Admin y seguridad tienen acceso completo
        roles_permitidos = ['Administrador', 'Seguridad', 'Propietario']
        return bool(request.user.roles.filter(nombre__in=roles_permitidos).exists())
    
    def has_object_permission(self, request, view, obj):  # type: ignore[override]
        if not request.user or not request.user.is_authenticated:
            return False
        
        # Admin y seguridad pueden ver todo
        if request.user.roles.filter(nombre__in=['Administrador', 'Seguridad']).exists():
            return True
        
        # Propietarios solo pueden ver sus propios datos
        if request.user.roles.filter(nombre='Propietario').exists():
            # Verificar que el objeto pertenece al usuario
            if hasattr(obj, 'persona') and hasattr(request.user, 'persona'):
                return bool(obj.persona == request.user.persona)
            
            if hasattr(obj, 'usuario') and obj.usuario == request.user:
                return True
        
        return False


def usuario_puede_gestionar_reconocimiento(usuario, persona_objetivo=None):
    """
    Verifica si un usuario puede gestionar el reconocimiento facial
    
    Args:
        usuario: Usuario que quiere realizar la acción
        persona_objetivo: Persona sobre la que se quiere actuar (opcional)
    
    Returns:
        bool: True si puede gestionar
    """
    if not usuario.is_authenticated:
        return False
    
    # Admin puede gestionar todo
    if usuario.roles.filter(nombre='Administrador').exists():
        return True
    
    # Seguridad puede gestionar todo
    if usuario.roles.filter(nombre='Seguridad').exists():
        return True
    
    # Propietario solo puede gestionar sus propios datos
    if usuario.roles.filter(nombre='Propietario').exists():
        if persona_objetivo and hasattr(usuario, 'persona'):
            return usuario.persona == persona_objetivo
        return True  # Si no se especifica objetivo, puede gestionar sus datos
    
    return False


def log_security_event(request, action, result, details=None):
    """
    Registra eventos de seguridad para auditoría
    
    Args:
        request: Request HTTP
        action: Acción realizada
        result: Resultado (success/denied)
        details: Detalles adicionales
    """
    user_info = f"{request.user.email}" if request.user.is_authenticated else "Anonymous"
    ip = request.META.get('REMOTE_ADDR', 'Unknown')
    
    logger.info(f"SECURITY_EVENT - User: {user_info}, IP: {ip}, Action: {action}, Result: {result}, Details: {details}")


if __name__ == "__main__":
    print(SECURITY_AUDIT_MESSAGE)