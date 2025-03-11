"""Celery application configuration."""

import os
from celery import Celery
from celery.signals import celeryd_after_setup
from celery.utils.log import get_task_logger

from ..core.config import settings
from .schedule import (
    CELERYBEAT_SCHEDULE,
    CELERY_ROUTES,
    CELERY_QUEUES,
    CELERY_TASK_SERIALIZER,
    CELERY_RESULT_SERIALIZER,
    CELERY_ACCEPT_CONTENT,
    CELERY_TIMEZONE,
    CELERY_ENABLE_UTC,
    CELERY_TASK_ACKS_LATE,
    CELERY_TASK_REJECT_ON_WORKER_LOST,
    CELERY_TASK_TRACK_STARTED,
    CELERY_RESULT_BACKEND,
    CELERY_RESULT_EXPIRES,
    CELERY_BROKER_URL,
    CELERY_BROKER_TRANSPORT_OPTIONS,
)

logger = get_task_logger(__name__)

# Create Celery app
app = Celery('app')

# Configure Celery app
app.conf.update(
    # Schedule
    beat_schedule=CELERYBEAT_SCHEDULE,
    
    # Routing
    task_routes=CELERY_ROUTES,
    task_queues=CELERY_QUEUES,
    
    # Serialization
    task_serializer=CELERY_TASK_SERIALIZER,
    result_serializer=CELERY_RESULT_SERIALIZER,
    accept_content=CELERY_ACCEPT_CONTENT,
    timezone=CELERY_TIMEZONE,
    enable_utc=CELERY_ENABLE_UTC,
    
    # Task execution
    task_acks_late=CELERY_TASK_ACKS_LATE,
    task_reject_on_worker_lost=CELERY_TASK_REJECT_ON_WORKER_LOST,
    task_track_started=CELERY_TASK_TRACK_STARTED,
    
    # Result backend
    result_backend=CELERY_RESULT_BACKEND,
    result_expires=CELERY_RESULT_EXPIRES,
    
    # Broker
    broker_url=CELERY_BROKER_URL,
    broker_transport_options=CELERY_BROKER_TRANSPORT_OPTIONS,
    
    # Additional settings
    worker_prefetch_multiplier=1,  # One task per worker at a time
    worker_max_tasks_per_child=1000,  # Restart worker after 1000 tasks
    task_default_queue='default',  # Default queue name
    task_default_exchange='default',  # Default exchange name
    task_default_routing_key='default',  # Default routing key
    task_create_missing_queues=True,  # Create queues if they don't exist
    task_soft_time_limit=3600,  # Soft time limit (1 hour)
    task_time_limit=3600 * 2,  # Hard time limit (2 hours)
    worker_send_task_events=True,  # Enable task events
    task_send_sent_event=True,  # Enable sent events
)

# Auto-discover tasks in all registered apps
app.autodiscover_tasks(['app.tasks'])

# Setup signal handlers
@celeryd_after_setup.connect
def setup_direct_queue(sender, instance, **kwargs):
    """
    Setup worker-specific queue after worker initialization.
    This allows tasks to be routed to specific workers when needed.
    """
    queue_name = f'{sender}.direct'
    logger.info(f'Creating worker-specific queue: {queue_name}')
    

@app.task(bind=True)
def debug_task(self):
    """Debug task to test Celery configuration."""
    logger.info(f'Request: {self.request!r}')


if __name__ == '__main__':
    app.start() 