"""Celery worker configuration."""

import os
from celery.signals import (
    worker_init,
    worker_ready,
    worker_shutting_down,
    task_prerun,
    task_postrun,
    task_failure,
    task_retry,
    task_success,
    task_revoked,
)
from celery.utils.log import get_task_logger

from ..core.config import settings
from ..db.session import SessionLocal
from ..utils.logger import logger

# Configure worker logger
worker_logger = get_task_logger(__name__)


@worker_init.connect
def init_worker(**kwargs):
    """Initialize worker with required setup."""
    worker_logger.info('Initializing worker...')
    
    try:
        # Test database connection
        db = SessionLocal()
        db.execute('SELECT 1')
        db.close()
        worker_logger.info('Database connection successful')
        
        # Set worker environment
        os.environ['TZ'] = settings.TIMEZONE
        
        worker_logger.info('Worker initialization complete')
    except Exception as e:
        worker_logger.error(f'Worker initialization failed: {e}')
        raise


@worker_ready.connect
def worker_ready_handler(**kwargs):
    """Handle worker ready signal."""
    worker_logger.info('Worker is ready to receive tasks')


@worker_shutting_down.connect
def worker_shutdown_handler(**kwargs):
    """Handle worker shutdown signal."""
    worker_logger.info('Worker is shutting down')


@task_prerun.connect
def task_prerun_handler(task_id, task, *args, **kwargs):
    """Handle task pre-run signal."""
    worker_logger.info(f'Starting task: {task.name}[{task_id}]')
    
    # Set up task context
    task.request.update(
        correlation_id=kwargs.get('correlation_id', task_id),
        task_name=task.name,
        task_id=task_id,
    )


@task_postrun.connect
def task_postrun_handler(task_id, task, *args, **kwargs):
    """Handle task post-run signal."""
    worker_logger.info(f'Completed task: {task.name}[{task_id}]')
    
    # Clean up task context
    task.request.clear()


@task_success.connect
def task_success_handler(sender=None, result=None, **kwargs):
    """Handle task success signal."""
    task_id = sender.request.id if sender else 'Unknown'
    task_name = sender.name if sender else 'Unknown'
    worker_logger.info(f'Task succeeded: {task_name}[{task_id}]')


@task_failure.connect
def task_failure_handler(task_id=None, exception=None, traceback=None, **kwargs):
    """Handle task failure signal."""
    worker_logger.error(
        f'Task failed: {kwargs.get("sender", "Unknown")}[{task_id}]\n'
        f'Error: {exception}\n'
        f'Traceback: {traceback}'
    )


@task_retry.connect
def task_retry_handler(request=None, reason=None, **kwargs):
    """Handle task retry signal."""
    task_id = request.id if request else 'Unknown'
    task_name = request.task if request else 'Unknown'
    worker_logger.warning(
        f'Task retrying: {task_name}[{task_id}]\n'
        f'Reason: {reason}'
    )


@task_revoked.connect
def task_revoked_handler(request=None, terminated=None, signum=None, **kwargs):
    """Handle task revocation signal."""
    task_id = request.id if request else 'Unknown'
    task_name = request.task if request else 'Unknown'
    worker_logger.warning(
        f'Task revoked: {task_name}[{task_id}]\n'
        f'Terminated: {terminated}\n'
        f'Signal: {signum}'
    )


# Error handlers
def handle_task_exception(task, exc, task_id, args, kwargs, einfo):
    """Handle task exceptions."""
    worker_logger.error(
        f'Task exception: {task.name}[{task_id}]\n'
        f'Args: {args}\n'
        f'Kwargs: {kwargs}\n'
        f'Error: {exc}\n'
        f'Info: {einfo}'
    )
    
    # You can implement custom error handling here
    # For example:
    # - Send error notifications
    # - Log to error tracking service
    # - Cleanup resources
    # - etc.


# Task base class with common functionality
class BaseTask:
    """Base class for all Celery tasks."""
    
    abstract = True
    
    def on_failure(self, exc, task_id, args, kwargs, einfo):
        """Handle task failure."""
        handle_task_exception(self, exc, task_id, args, kwargs, einfo)
    
    def on_retry(self, exc, task_id, args, kwargs, einfo):
        """Handle task retry."""
        worker_logger.warning(
            f'Task retrying: {self.name}[{task_id}]\n'
            f'Args: {args}\n'
            f'Kwargs: {kwargs}\n'
            f'Error: {exc}\n'
            f'Info: {einfo}'
        )
    
    def after_return(self, status, retval, task_id, args, kwargs, einfo):
        """Handle task completion."""
        worker_logger.info(
            f'Task completed: {self.name}[{task_id}]\n'
            f'Status: {status}\n'
            f'Return: {retval}'
        )
    
    def on_success(self, retval, task_id, args, kwargs):
        """Handle task success."""
        worker_logger.info(
            f'Task succeeded: {self.name}[{task_id}]\n'
            f'Args: {args}\n'
            f'Kwargs: {kwargs}\n'
            f'Return: {retval}'
        ) 