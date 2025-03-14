from django.apps import AppConfig


class ChatConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'chat'
    verbose_name = 'Live Chat Support'

    def ready(self):
        """Import signals when the app is ready."""
        import chat.signals  # noqa
