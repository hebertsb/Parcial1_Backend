from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from authz.models import SolicitudRegistroPropietario, RelacionesPropietarioInquilino, FamiliarPropietario
from core.models.propiedades_residentes import Visita
from core.models.administracion import BitacoraAcciones
from django.contrib.auth import get_user_model
import threading

# Helper para obtener usuario actual (si usas middleware personalizado)
def get_current_user():
    # Si tienes un middleware que guarda el usuario en threading.local()
    return getattr(threading.local(), 'user', None)

@receiver(post_save, sender=SolicitudRegistroPropietario)
def bitacora_solicitud_propietario(sender, instance, created, **kwargs):
    usuario = get_current_user() or getattr(instance, 'usuario_creado', None)
    accion_tipo = 'CREATE' if created else 'UPDATE'
    rol = None
    if usuario and hasattr(usuario, 'roles'):
        rol = usuario.roles.first()
    if not rol:
        from authz.models import Rol
        rol, _ = Rol.objects.get_or_create(nombre='Invitado', defaults={'descripcion': 'Rol por defecto'})
    BitacoraAcciones.objects.create(
        usuario=usuario,
        rol=rol,
        descripcion=f'{accion_tipo} de solicitud de registro de propietario',
        ip_address='127.0.0.1',
        modulo_afectado='SolicitudRegistroPropietario',
        accion_tipo=accion_tipo,
        tabla_afectada='SolicitudRegistroPropietario',
        registro_id=instance.id,
        datos_antes={},
        datos_despues={},
    )

@receiver(post_delete, sender=SolicitudRegistroPropietario)
def bitacora_delete_solicitud(sender, instance, **kwargs):
    usuario = get_current_user() or getattr(instance, 'usuario_creado', None)
    rol = None
    if usuario and hasattr(usuario, 'roles'):
        rol = usuario.roles.first()
    if not rol:
        from authz.models import Rol
        rol, _ = Rol.objects.get_or_create(nombre='Invitado', defaults={'descripcion': 'Rol por defecto'})
    BitacoraAcciones.objects.create(
        usuario=usuario,
        rol=rol,
        descripcion='DELETE de solicitud de registro de propietario',
        ip_address='127.0.0.1',
        modulo_afectado='SolicitudRegistroPropietario',
        accion_tipo='DELETE',
        tabla_afectada='SolicitudRegistroPropietario',
        registro_id=instance.id,
        datos_antes={},
        datos_despues={},
    )

@receiver(post_save, sender=RelacionesPropietarioInquilino)
def bitacora_relacion_inquilino(sender, instance, created, **kwargs):
    usuario = get_current_user() or getattr(instance, 'propietario', None)
    accion_tipo = 'CREATE' if created else 'UPDATE'
    rol = None
    if usuario and hasattr(usuario, 'roles'):
        rol = usuario.roles.first()
    if not rol:
        from authz.models import Rol
        rol, _ = Rol.objects.get_or_create(nombre='Invitado', defaults={'descripcion': 'Rol por defecto'})
    BitacoraAcciones.objects.create(
        usuario=usuario,
        rol=rol,
        descripcion=f'{accion_tipo} de relación propietario-inquilino',
        ip_address='127.0.0.1',
        modulo_afectado='RelacionesPropietarioInquilino',
        accion_tipo=accion_tipo,
        tabla_afectada='RelacionesPropietarioInquilino',
        registro_id=instance.id,
        datos_antes={},
        datos_despues={},
    )

@receiver(post_delete, sender=RelacionesPropietarioInquilino)
def bitacora_delete_relacion(sender, instance, **kwargs):
    usuario = get_current_user() or getattr(instance, 'propietario', None)
    BitacoraAcciones.objects.create(
        usuario=usuario,
        rol=None,
        descripcion='DELETE de relación propietario-inquilino',
        ip_address='127.0.0.1',
        modulo_afectado='RelacionesPropietarioInquilino',
        accion_tipo='DELETE',
        tabla_afectada='RelacionesPropietarioInquilino',
        registro_id=instance.id,
        datos_antes={},
        datos_despues={},
    )

@receiver(post_save, sender=FamiliarPropietario)
def bitacora_familiar(sender, instance, created, **kwargs):
    usuario = get_current_user() or getattr(instance, 'propietario', None)
    accion_tipo = 'CREATE' if created else 'UPDATE'
    BitacoraAcciones.objects.create(
        usuario=usuario,
        rol=None,
        descripcion=f'{accion_tipo} de familiar propietario',
        ip_address='127.0.0.1',
        modulo_afectado='FamiliarPropietario',
        accion_tipo=accion_tipo,
        tabla_afectada='FamiliarPropietario',
        registro_id=instance.id,
        datos_antes={},
        datos_despues={},
    )

@receiver(post_delete, sender=FamiliarPropietario)
def bitacora_delete_familiar(sender, instance, **kwargs):
    usuario = get_current_user() or getattr(instance, 'propietario', None)
    BitacoraAcciones.objects.create(
        usuario=usuario,
        rol=None,
        descripcion='DELETE de familiar propietario',
        ip_address='127.0.0.1',
        modulo_afectado='FamiliarPropietario',
        accion_tipo='DELETE',
        tabla_afectada='FamiliarPropietario',
        registro_id=instance.id,
        datos_antes={},
        datos_despues={},
    )

@receiver(post_save, sender=Visita)
def bitacora_visita(sender, instance, created, **kwargs):
    usuario = get_current_user() or getattr(instance, 'usuario', None)
    accion_tipo = 'CREATE' if created else 'UPDATE'
    BitacoraAcciones.objects.create(
        usuario=usuario,
        rol=None,
        descripcion=f'{accion_tipo} de visita',
        ip_address='127.0.0.1',
        modulo_afectado='Visita',
        accion_tipo=accion_tipo,
        tabla_afectada='Visita',
        registro_id=instance.id,
        datos_antes={},
        datos_despues={},
    )

@receiver(post_delete, sender=Visita)
def bitacora_delete_visita(sender, instance, **kwargs):
    usuario = get_current_user() or getattr(instance, 'usuario', None)
    BitacoraAcciones.objects.create(
        usuario=usuario,
        rol=None,
        descripcion='DELETE de visita',
        ip_address='127.0.0.1',
        modulo_afectado='Visita',
        accion_tipo='DELETE',
        tabla_afectada='Visita',
        registro_id=instance.id,
        datos_antes={},
        datos_despues={},
    )
