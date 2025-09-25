"""
CUSTOM PERMISSIONS - Sistema de Permisos por Roles
Autor: Sistema de Gestión de Condominios
Fecha: 2025-09-24

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


class IsAdministrador(BasePermission):
    """
    Permiso personalizado para verificar que el usuario es Administrador.
    SEGURIDAD: No auto-asigna roles, solo verifica.
    """
    
    def has_permission(self, request, view):  # type: ignore[override]
        if not request.user or not request.user.is_authenticated:
            return False
        
        # Verificar rol de administrador (sin auto-asignación)
        return bool(request.user.roles.filter(
            nombre__in=['Administrador', 'ADMIN']
        ).exists())
    
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
        from authz.models import SolicitudRegistroPropietario
        solicitud_aprobada = SolicitudRegistroPropietario.objects.filter(
            usuario_creado=request.user,
            estado='APROBADA'
        ).exists()
        
        return bool(solicitud_aprobada)
    
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
        if hasattr(obj, 'usuario'):
            return bool(obj.usuario == request.user)
        elif hasattr(obj, 'propietario'):
            return bool(obj.propietario == request.user)
        elif hasattr(obj, 'user'):
            return bool(obj.user == request.user)
        
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

🛡️ RECOMENDACIONES:
1. Remover auto-asignación automática de roles
2. Implementar logging de seguridad
3. Usar permisos personalizados en todos los endpoints críticos
4. Verificar is_superuser para operaciones críticas

🔍 PARA PROBAR SEGURIDAD:
python manage.py test_security_roles
"""

if __name__ == "__main__":
    print(SECURITY_AUDIT_MESSAGE)