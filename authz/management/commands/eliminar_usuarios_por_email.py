"""
Elimina usuarios y datos asociados por email.

Acciones (por cada email):
 - authz.Usuario con ese email (y su relación de roles M2M)
 - Relaciones en authz: RelacionesPropietarioInquilino (propietario/inquilino)
 - Solicitudes de registro vinculadas (por usuario_creado o email)
 - authz.Persona vinculada al Usuario, y también cualquier Persona de authz con ese email
 - (Opcional) core.Persona con ese email y sus relaciones básicas:
     - core.RelacionesPropietarioInquilino (propietario/inquilino)
     - core.Propiedad (se elimina por cascada al borrar core.Persona)

Uso:
  python manage.py eliminar_usuarios_por_email suarezburgoshebert@gmail.com test2@gmail.com

Opciones:
  --dry-run       Muestra lo que se haría sin aplicar cambios
  --skip-core     No toca registros en la app core (solo authz)
"""
from django.core.management.base import BaseCommand
from django.db import transaction


class Command(BaseCommand):
    help = "Elimina usuarios y datos vinculados por email (authz y, por defecto, core)."

    def add_arguments(self, parser):
        parser.add_argument('emails', nargs='+', help='Lista de emails a eliminar completamente')
        parser.add_argument('--dry-run', action='store_true', help='Previsualiza sin aplicar cambios')
        parser.add_argument('--skip-core', action='store_true', help='No elimina datos en app core, solo authz')

    def handle(self, *args, **options):
        emails = options['emails']
        dry_run = options['dry_run']
        skip_core = options['skip_core']

        from authz.models import (
            Usuario as AuthUser,
            Persona as AuthPersona,
            SolicitudRegistroPropietario,
            RelacionesPropietarioInquilino as AuthRelPI,
            FamiliarPropietario,
        )

        if not skip_core:
            try:
                from core.models import (
                    Persona as CorePersona,
                    Propiedad,
                )
                # Relaciones Propietario-Inquilino de core puede no existir en todos los despliegues
                try:
                    from core.models import RelacionesPropietarioInquilino as CoreRelPI  # type: ignore
                except Exception:  # pragma: no cover - si no existe
                    CoreRelPI = None  # type: ignore
            except Exception:
                CorePersona = None  # type: ignore
                Propiedad = None  # type: ignore
                CoreRelPI = None  # type: ignore
                skip_core = True

        for email in emails:
            self.stdout.write(self.style.NOTICE(f"Procesando email: {email}"))

            with transaction.atomic():
                # 1) authz.Usuario
                user = AuthUser.objects.filter(email=email).first()
                if user:
                    self.stdout.write(f"  - authz.Usuario encontrado (id={user.id})")

                    # Relaciones authz PI
                    rels_prop = AuthRelPI.objects.filter(propietario=user)
                    rels_inq = AuthRelPI.objects.filter(inquilino=user)
                    self.stdout.write(f"    · Relaciones propietario (authz): {rels_prop.count()} | inquilino: {rels_inq.count()}")

                    # Solicitudes vinculadas
                    sols_user = SolicitudRegistroPropietario.objects.filter(usuario_creado=user)
                    sols_email = SolicitudRegistroPropietario.objects.filter(email=email)
                    self.stdout.write(f"    · Solicitudes (por usuario): {sols_user.count()} | (por email): {sols_email.count()}")

                    # Persona authz vinculada al usuario (guardar id antes de borrar user)
                    auth_persona_id = user.persona_id

                    if not dry_run:
                        rels_prop.delete()
                        rels_inq.delete()
                        # Borrar solicitudes asociadas (por usuario y por email)
                        sols_user.delete()
                        # Evitar doble borrado con union
                        sols_email.exclude(id__in=list(sols_user.values_list('id', flat=True))).delete()

                        # Borrar usuario
                        user.delete()

                        # Borrar persona authz vinculada (si quedó viva)
                        if auth_persona_id:
                            AuthPersona.objects.filter(id=auth_persona_id).delete()
                else:
                    self.stdout.write(f"  - authz.Usuario no encontrado")

                # 2) Personas sueltas en authz con ese email
                personas_authz = AuthPersona.objects.filter(email=email)
                if personas_authz.exists():
                    self.stdout.write(f"  - Personas authz a eliminar: {personas_authz.count()}")
                    if not dry_run:
                        personas_authz.delete()

                # 3) Limpiar en core si corresponde
                if not skip_core and 'CorePersona' in locals() and CorePersona:
                    core_personas = CorePersona.objects.filter(email=email)
                    self.stdout.write(f"  - Personas core encontradas: {core_personas.count()}")
                    for cp in core_personas:
                        self.stdout.write(f"    · core.Persona id={cp.id} ({cp.nombre} {cp.apellido})")
                        if dry_run:
                            continue
                        # Borrar relaciones PI core si el modelo existe
                        if 'CoreRelPI' in locals() and CoreRelPI:
                            CoreRelPI.objects.filter(propietario=cp).delete()
                            CoreRelPI.objects.filter(inquilino=cp).delete()
                        # Borrar Propiedades por cascada al eliminar persona
                        cp.delete()

            if dry_run:
                self.stdout.write(self.style.WARNING(f"[Dry-run] No se aplicaron cambios para {email}"))
            else:
                self.stdout.write(self.style.SUCCESS(f"Eliminación completa para {email}"))

