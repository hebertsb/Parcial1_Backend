"""
Función para sincronizar roles de usuario con tipo_persona
"""
from authz.models import Usuario, Rol
import logging

logger = logging.getLogger(__name__)

def sincronizar_roles_con_tipo_persona(persona, usuario=None):
    """
    Sincroniza los roles del usuario con el tipo_persona de la persona
    
    Args:
        persona: Instancia de Persona
        usuario: Instancia de Usuario (opcional, se buscará automáticamente)
    
    Returns:
        dict: Información sobre el cambio realizado
    """
    if not usuario:
        try:
            usuario = Usuario.objects.get(persona=persona)
        except Usuario.DoesNotExist:
            return {
                'success': False,
                'message': f'No se encontró usuario asociado a {persona.nombre_completo}',
                'roles_antes': [],
                'roles_despues': []
            }
    
    # Mapeo de tipo_persona a nombre de rol
    MAPEO_TIPO_A_ROL = {
        'administrador': 'Administrador',
        'seguridad': 'Seguridad', 
        'propietario': 'Propietario',
        'inquilino': 'Inquilino',
        'cliente': 'Inquilino',  # Por defecto cliente = inquilino
        'residente': 'Inquilino'  # Residente sin propiedad = inquilino
    }
    
    tipo_persona = persona.tipo_persona
    nombre_rol_requerido = MAPEO_TIPO_A_ROL.get(tipo_persona, 'Inquilino')
    
    # Obtener roles actuales
    roles_actuales = list(usuario.roles.values_list('nombre', flat=True))
    
    try:
        # Obtener o crear el rol requerido
        rol_requerido, created = Rol.objects.get_or_create(
            nombre=nombre_rol_requerido,
            defaults={
                'descripcion': f'Rol de {nombre_rol_requerido.lower()} del sistema',
                'activo': True
            }
        )
        
        # Verificar si ya tiene el rol correcto
        if nombre_rol_requerido in roles_actuales:
            # Ya tiene el rol correcto, solo limpiar otros roles si es necesario
            roles_a_remover = [r for r in roles_actuales if r != nombre_rol_requerido]
            if roles_a_remover:
                # Remover roles incorrectos
                roles_incorrectos = Rol.objects.filter(nombre__in=roles_a_remover)
                usuario.roles.remove(*roles_incorrectos)
                
                logger.info(f"✅ Roles limpiados para {usuario.email}: removidos {roles_a_remover}")
                
                return {
                    'success': True,
                    'message': f'Roles sincronizados: removidos roles incorrectos',
                    'persona': persona.nombre_completo,
                    'tipo_persona': tipo_persona,
                    'roles_antes': roles_actuales,
                    'roles_despues': [nombre_rol_requerido],
                    'accion': 'limpieza'
                }
            else:
                return {
                    'success': True,
                    'message': 'Roles ya están sincronizados correctamente',
                    'persona': persona.nombre_completo,
                    'tipo_persona': tipo_persona,
                    'roles_antes': roles_actuales,
                    'roles_despues': roles_actuales,
                    'accion': 'sin_cambios'
                }
        else:
            # Cambiar al rol correcto
            # 1. Limpiar todos los roles actuales
            usuario.roles.clear()
            
            # 2. Asignar el rol correcto
            usuario.roles.add(rol_requerido)
            
            logger.info(f"🔄 Rol sincronizado para {usuario.email}: {roles_actuales} → [{nombre_rol_requerido}]")
            
            return {
                'success': True,
                'message': f'Rol cambiado exitosamente de {roles_actuales} a [{nombre_rol_requerido}]',
                'persona': persona.nombre_completo,
                'tipo_persona': tipo_persona,
                'roles_antes': roles_actuales,
                'roles_despues': [nombre_rol_requerido],
                'accion': 'cambio_rol'
            }
            
    except Exception as e:
        logger.error(f"❌ Error sincronizando roles para {usuario.email}: {str(e)}")
        return {
            'success': False,
            'message': f'Error sincronizando roles: {str(e)}',
            'persona': persona.nombre_completo,
            'tipo_persona': tipo_persona,
            'roles_antes': roles_actuales,
            'roles_despues': roles_actuales,
            'error': str(e)
        }


def sincronizar_todos_los_usuarios():
    """
    Sincroniza todos los usuarios del sistema para asegurar consistencia
    
    Returns:
        dict: Resumen de sincronizaciones realizadas
    """
    usuarios = Usuario.objects.filter(persona__isnull=False)
    sincronizaciones = []
    
    for usuario in usuarios:
        resultado = sincronizar_roles_con_tipo_persona(usuario.persona, usuario)
        if resultado['success'] and resultado['accion'] != 'sin_cambios':
            sincronizaciones.append(resultado)
    
    return {
        'total_usuarios': usuarios.count(),
        'sincronizaciones_realizadas': len(sincronizaciones),
        'detalles': sincronizaciones
    }