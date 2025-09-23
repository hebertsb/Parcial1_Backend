"""
Comando para limpiar propietarios existentes en core.Propiedad

Permite desactivar (soft) o eliminar (hard) relaciones de tenencia 'propietario'.

Usos comunes:
  - Desactivar todos los propietarios activos (recomendado):
      python manage.py limpiar_propietarios

  - Desactivar propietarios de viviendas específicas:
      python manage.py limpiar_propietarios --viviendas V001 V004 V010

  - Eliminar definitivamente (hard delete) propietarios activos de una vivienda:
      python manage.py limpiar_propietarios --viviendas V004 --hard-delete

  - Previsualizar (no aplica cambios):
      python manage.py limpiar_propietarios --viviendas V004 V005 --dry-run
"""
from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import date

class Command(BaseCommand):
    help = "Limpia propietarios existentes (core.Propiedad) para liberar viviendas. Por defecto desactiva (soft)."

    def add_arguments(self, parser):
        parser.add_argument(
            '--viviendas', nargs='*', default=None,
            help='Lista de números de casa a limpiar (ej: V001 V004 V010). Si se omite, aplica a todas.'
        )
        parser.add_argument(
            '--hard-delete', action='store_true',
            help='Elimina definitivamente en lugar de desactivar. Por defecto solo desactiva (soft).'
        )
        parser.add_argument(
            '--dry-run', action='store_true',
            help='Muestra lo que se haría sin aplicar cambios.'
        )

    def handle(self, *args, **options):
        from core.models import Propiedad  # import local para evitar dependencias circulares

        viviendas = options['viviendas']
        hard_delete = options['hard_delete']
        dry_run = options['dry_run']

        qs = Propiedad.objects.filter(tipo_tenencia='propietario', activo=True)
        if viviendas:
            qs = qs.filter(vivienda__numero_casa__in=viviendas)

        total = qs.count()
        if total == 0:
            if viviendas:
                self.stdout.write(self.style.WARNING(
                    f'No se encontraron propietarios activos para las viviendas: {", ".join(viviendas)}'
                ))
            else:
                self.stdout.write(self.style.WARNING('No se encontraron propietarios activos para limpiar.'))
            return

        # Previsualización
        muestras = list(qs.select_related('vivienda', 'persona')[:5])
        preview = [
            f"{p.vivienda.numero_casa} -> {p.persona.nombre} {p.persona.apellido} (ID {p.id})"
            for p in muestras
        ]

        self.stdout.write(self.style.NOTICE(
            f"Encontradas {total} relaciones de propietario activas. Ejemplos: "
        ))
        for line in preview:
            self.stdout.write(f"  - {line}")

        if dry_run:
            self.stdout.write(self.style.WARNING('Dry-run habilitado: no se aplicaron cambios.'))
            return

        if hard_delete:
            deleted_info = qs.delete()
            self.stdout.write(self.style.SUCCESS(
                f"Eliminados definitivamente {total} propietarios activos."
            ))
        else:
            hoy = date.today()
            qs.update(activo=False, fecha_fin_tenencia=hoy)
            self.stdout.write(self.style.SUCCESS(
                f"Desactivados {total} propietarios (activo=False, fecha_fin_tenencia={hoy})."
            ))

        # Mensaje final
        if viviendas:
            self.stdout.write(self.style.SUCCESS(
                f"Viviendas liberadas: {', '.join(viviendas)}"
            ))
        else:
            self.stdout.write(self.style.SUCCESS("Todas las viviendas quedaron sin propietario activo."))

