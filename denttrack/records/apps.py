from django.apps import AppConfig


class RecordsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'records'
    verbose_name = 'Dental Records'

    def ready(self):
        import records.signals  # noqa: F401  registers audit-log signal handlers
