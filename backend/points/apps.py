from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _

class PointsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'points'
    verbose_name = _('Points System')
    
    def ready(self):
        try:
            import points.signals  # noqa F401
        except ImportError:
            pass 