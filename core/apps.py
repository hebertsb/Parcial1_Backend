from django.apps import AppConfig


class CoreConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'core'
    verbose_name = 'Sistema Central'

    def ready(self):
        # Importar señales de bitácora
        import core.api.bitacora.signals