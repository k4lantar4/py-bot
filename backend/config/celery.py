from __future__ import absolute_import, unicode_literals
import os
from celery import Celery
from django.conf import settings
from celery.schedules import crontab

# Set the default Django settings module for the 'celery' program.
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')

# Create the Celery app
app = Celery('mrjbot')

# Using a string here means the worker doesn't have to serialize
# the configuration object to child processes.
# - namespace='CELERY' means all celery-related configuration keys
#   should have a `CELERY_` prefix.
app.config_from_object('django.conf:settings', namespace='CELERY')

# Load task modules from all registered Django app configs.
# Load task modules from all registered Django apps.
app.autodiscover_tasks()

# Configure Celery Beat schedule
app.conf.beat_schedule = {
    'check-expired-subscriptions': {
        'task': 'mrjbot.services.tasks.check_expired_subscriptions',
        'schedule': 3600.0,  # Run every hour
    },
    'cleanup-old-notifications': {
        'task': 'mrjbot.notifications.tasks.cleanup_old_notifications',
        'schedule': 86400.0,  # Run daily
    },
    'process-pending-withdrawals': {
        'task': 'mrjbot.payments.tasks.process_pending_withdrawals',
        'schedule': 1800.0,  # Run every 30 minutes
    },
    'sync-payment-gateways': {
        'task': 'mrjbot.payments.tasks.sync_payment_gateways',
        'schedule': 300.0,  # Run every 5 minutes
    },
    'analyze-usage-patterns': {
        'task': 'main.tasks.analyze_usage_patterns',
        'schedule': crontab(hour='*/6'),  # Run every 6 hours
    },
    # Backup task - every 30 minutes
    'backup-system': {
        'task': 'mrjbot.tasks.backup.backup_system',
        'schedule': 30 * 60,  # 30 minutes
    },
    # AI content generation - every 6 hours
    'generate-ai-content': {
        'task': 'mrjbot.services.ai_content.AIContentGenerator.schedule_content_generation',
        'schedule': 6 * 60 * 60,  # 6 hours
    },
    # Clean old backups - daily at midnight
    'cleanup-old-backups': {
        'task': 'mrjbot.tasks.backup.BackupManager._cleanup_old_backups',
        'schedule': crontab(hour=0, minute=0),
    },
    # New location management tasks
    'monitor-server-locations': {
        'task': 'mrjbot.services.location.LocationManager.monitor_servers',
        'schedule': 300.0,  # Run every 5 minutes
    },
    'balance-server-load': {
        'task': 'mrjbot.services.location.LocationManager.balance_load',
        'schedule': 600.0,  # Run every 10 minutes
    },
}

@app.task(bind=True, ignore_result=True)
def debug_task(self):
    print(f'Request: {self.request!r}') 