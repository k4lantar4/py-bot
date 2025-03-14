from celery import shared_task
from django.utils import timezone
from django.db.models import Q
from .models import Service, Plan, Subscription, Usage, ServiceMetric, ServiceAlert

@shared_task
def check_expired_subscriptions():
    """
    Check for expired subscriptions and update their status
    """
    expired_subs = Subscription.objects.filter(
        status='active',
        end_date__lt=timezone.now()
    )
    
    for sub in expired_subs:
        if sub.auto_renew:
            # Try to renew subscription
            try:
                sub.renew()
            except Exception as e:
                ServiceAlert.objects.create(
                    service=sub.plan.service,
                    level='error',
                    message=f'Failed to auto-renew subscription for user {sub.user.username}: {str(e)}'
                )
        else:
            sub.status = 'expired'
            sub.save()
            
            ServiceAlert.objects.create(
                service=sub.plan.service,
                level='warning',
                message=f'Subscription expired for user {sub.user.username}'
            )

@shared_task
def collect_service_metrics():
    """
    Collect metrics for all active services
    """
    for service in Service.objects.filter(is_active=True):
        # Get total active subscriptions
        active_subs = Subscription.objects.filter(
            plan__service=service,
            status='active'
        ).count()
        
        # Get total usage for today
        today = timezone.now().date()
        daily_usage = Usage.objects.filter(
            subscription__plan__service=service,
            date=today
        ).aggregate(total=Sum('amount'))['total'] or 0
        
        # Create metrics
        ServiceMetric.objects.create(
            service=service,
            name='active_subscriptions',
            value=active_subs,
            timestamp=timezone.now()
        )
        
        ServiceMetric.objects.create(
            service=service,
            name='daily_usage',
            value=daily_usage,
            timestamp=timezone.now()
        )

@shared_task
def check_service_health():
    """
    Check health of all active services
    """
    for service in Service.objects.filter(is_active=True):
        try:
            # Implement service-specific health checks here
            # For example, check API endpoints, database connections, etc.
            is_healthy = service.check_health()
            
            if not is_healthy:
                ServiceAlert.objects.create(
                    service=service,
                    level='error',
                    message=f'Service {service.name} is not responding'
                )
        except Exception as e:
            ServiceAlert.objects.create(
                service=service,
                level='error',
                message=f'Health check failed for service {service.name}: {str(e)}'
            )

@shared_task
def cleanup_old_metrics():
    """
    Clean up old metrics data
    """
    cutoff_date = timezone.now() - timezone.timedelta(days=30)
    ServiceMetric.objects.filter(timestamp__lt=cutoff_date).delete()

@shared_task
def cleanup_old_alerts():
    """
    Clean up resolved alerts older than 7 days
    """
    cutoff_date = timezone.now() - timezone.timedelta(days=7)
    ServiceAlert.objects.filter(
        is_resolved=True,
        created_at__lt=cutoff_date
    ).delete()

@shared_task
def notify_expiring_subscriptions():
    """
    Send notifications for subscriptions that are about to expire
    """
    # Notify users whose subscriptions expire in 3 days
    three_days = timezone.now() + timezone.timedelta(days=3)
    expiring_subs = Subscription.objects.filter(
        status='active',
        end_date__lte=three_days,
        end_date__gt=timezone.now()
    )
    
    for sub in expiring_subs:
        if sub.auto_renew:
            message = f'Your subscription to {sub.plan.name} will auto-renew in 3 days'
        else:
            message = f'Your subscription to {sub.plan.name} will expire in 3 days'
            
        # Send notification to user
        sub.user.notify(message)

@shared_task
def generate_usage_report():
    """
    Generate daily usage report for all services
    """
    today = timezone.now().date()
    
    for service in Service.objects.filter(is_active=True):
        # Get usage data
        usage_data = Usage.objects.filter(
            subscription__plan__service=service,
            date=today
        ).aggregate(
            total_usage=Sum('amount'),
            total_users=Count('subscription__user', distinct=True)
        )
        
        # Create report
        report = {
            'date': today,
            'service': service.name,
            'total_usage': usage_data['total_usage'] or 0,
            'total_users': usage_data['total_users'] or 0
        }
        
        # Send report to service owner
        service.owner.notify(
            f'Daily Usage Report for {service.name}:\n'
            f'Total Usage: {report["total_usage"]}\n'
            f'Total Users: {report["total_users"]}'
        ) 