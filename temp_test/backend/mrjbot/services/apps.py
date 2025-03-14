from django.apps import AppConfig

class ServicesConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'mrjbot.services'
    verbose_name = 'Services'
    
    def ready(self):
        import mrjbot.services.signals  # noqa 