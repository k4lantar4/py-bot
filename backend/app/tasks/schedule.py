"""Celery beat schedule configuration."""

from celery.schedules import crontab

from .accounts import check_expired_accounts, sync_account_usage
from .notifications import send_expiry_notifications
from .orders import cancel_expired_orders
from .tickets import check_stale_tickets, auto_close_resolved_tickets
from .wallet import check_pending_transactions, sync_wallet_balances


CELERYBEAT_SCHEDULE = {
    # Account tasks
    'check-expired-accounts': {
        'task': 'app.tasks.accounts.check_expired_accounts',
        'schedule': crontab(minute='0', hour='*/1'),  # Every hour
    },
    'sync-account-usage': {
        'task': 'app.tasks.accounts.sync_account_usage',
        'schedule': crontab(minute='*/15'),  # Every 15 minutes
    },
    
    # Notification tasks
    'send-expiry-notifications': {
        'task': 'app.tasks.notifications.send_expiry_notifications',
        'schedule': crontab(minute='0', hour='9'),  # Daily at 9 AM
    },
    
    # Order tasks
    'cancel-expired-orders': {
        'task': 'app.tasks.orders.cancel_expired_orders',
        'schedule': crontab(minute='*/5'),  # Every 5 minutes
    },
    
    # Ticket tasks
    'check-stale-tickets': {
        'task': 'app.tasks.tickets.check_stale_tickets',
        'schedule': crontab(minute='0', hour='*/2'),  # Every 2 hours
    },
    'auto-close-resolved-tickets': {
        'task': 'app.tasks.tickets.auto_close_resolved_tickets',
        'schedule': crontab(minute='0', hour='0'),  # Daily at midnight
    },
    
    # Wallet tasks
    'check-pending-transactions': {
        'task': 'app.tasks.wallet.check_pending_transactions',
        'schedule': crontab(minute='*/10'),  # Every 10 minutes
    },
    'sync-wallet-balances': {
        'task': 'app.tasks.wallet.sync_wallet_balances',
        'schedule': crontab(minute='0', hour='*/6'),  # Every 6 hours
    },
}

# Task routing
CELERY_ROUTES = {
    # Account tasks
    'app.tasks.accounts.*': {'queue': 'accounts'},
    
    # Notification tasks
    'app.tasks.notifications.*': {'queue': 'notifications'},
    
    # Order tasks
    'app.tasks.orders.*': {'queue': 'orders'},
    
    # Payment tasks
    'app.tasks.payments.*': {'queue': 'payments'},
    
    # Ticket tasks
    'app.tasks.tickets.*': {'queue': 'tickets'},
    
    # Wallet tasks
    'app.tasks.wallet.*': {'queue': 'wallet'},
}

# Task queues
CELERY_QUEUES = {
    'accounts': {},
    'notifications': {},
    'orders': {},
    'payments': {},
    'tickets': {},
    'wallet': {},
}

# Task options
CELERY_TASK_ROUTES = CELERY_ROUTES
CELERY_TASK_QUEUES = CELERY_QUEUES

# Task serialization
CELERY_TASK_SERIALIZER = 'json'
CELERY_RESULT_SERIALIZER = 'json'
CELERY_ACCEPT_CONTENT = ['json']
CELERY_TIMEZONE = 'UTC'
CELERY_ENABLE_UTC = True

# Task execution settings
CELERY_TASK_ACKS_LATE = True
CELERY_TASK_REJECT_ON_WORKER_LOST = True
CELERY_TASK_TRACK_STARTED = True

# Task result backend settings
CELERY_RESULT_BACKEND = 'redis://redis:6379/0'
CELERY_RESULT_EXPIRES = 3600  # Results expire after 1 hour

# Broker settings
CELERY_BROKER_URL = 'redis://redis:6379/0'
CELERY_BROKER_TRANSPORT_OPTIONS = {
    'visibility_timeout': 3600,  # 1 hour
    'fanout_prefix': True,
    'fanout_patterns': True,
} 