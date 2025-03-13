from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django.utils import timezone
from .models import Service, Plan, Subscription, Config, Usage, ServiceLog, ServiceMetric, ServiceAlert

@receiver(post_save, sender=Service)
def service_post_save(sender, instance, created, **kwargs):
    if created:
        ServiceLog.objects.create(
            service=instance,
            level='info',
            message=f'Service {instance.name} was created'
        )
    else:
        ServiceLog.objects.create(
            service=instance,
            level='info',
            message=f'Service {instance.name} was updated'
        )

@receiver(post_save, sender=Plan)
def plan_post_save(sender, instance, created, **kwargs):
    if created:
        ServiceLog.objects.create(
            service=instance.service,
            level='info',
            message=f'Plan {instance.name} was created for service {instance.service.name}'
        )
    else:
        ServiceLog.objects.create(
            service=instance.service,
            level='info',
            message=f'Plan {instance.name} was updated for service {instance.service.name}'
        )

@receiver(post_save, sender=Subscription)
def subscription_post_save(sender, instance, created, **kwargs):
    if created:
        ServiceLog.objects.create(
            service=instance.plan.service,
            level='info',
            message=f'New subscription created for user {instance.user.username} on plan {instance.plan.name}'
        )
    else:
        ServiceLog.objects.create(
            service=instance.plan.service,
            level='info',
            message=f'Subscription updated for user {instance.user.username} on plan {instance.plan.name}'
        )

@receiver(post_save, sender=Config)
def config_post_save(sender, instance, created, **kwargs):
    if created:
        ServiceLog.objects.create(
            service=instance.service,
            level='info',
            message=f'New configuration {instance.key} was added for service {instance.service.name}'
        )
    else:
        ServiceLog.objects.create(
            service=instance.service,
            level='info',
            message=f'Configuration {instance.key} was updated for service {instance.service.name}'
        )

@receiver(post_save, sender=Usage)
def usage_post_save(sender, instance, created, **kwargs):
    if created:
        ServiceLog.objects.create(
            service=instance.subscription.plan.service,
            level='info',
            message=f'New usage recorded for user {instance.subscription.user.username} on plan {instance.subscription.plan.name}'
        )

@receiver(post_save, sender=ServiceMetric)
def metric_post_save(sender, instance, created, **kwargs):
    if created:
        ServiceLog.objects.create(
            service=instance.service,
            level='info',
            message=f'New metric {instance.name} was recorded for service {instance.service.name}'
        )

@receiver(post_save, sender=ServiceAlert)
def alert_post_save(sender, instance, created, **kwargs):
    if created:
        ServiceLog.objects.create(
            service=instance.service,
            level=instance.level,
            message=f'New alert: {instance.message}'
        )
    elif instance.is_resolved:
        ServiceLog.objects.create(
            service=instance.service,
            level='info',
            message=f'Alert resolved: {instance.message}'
        )

@receiver(post_delete, sender=Service)
def service_post_delete(sender, instance, **kwargs):
    ServiceLog.objects.create(
        service=instance,
        level='warning',
        message=f'Service {instance.name} was deleted'
    )

@receiver(post_delete, sender=Plan)
def plan_post_delete(sender, instance, **kwargs):
    ServiceLog.objects.create(
        service=instance.service,
        level='warning',
        message=f'Plan {instance.name} was deleted from service {instance.service.name}'
    )

@receiver(post_delete, sender=Subscription)
def subscription_post_delete(sender, instance, **kwargs):
    ServiceLog.objects.create(
        service=instance.plan.service,
        level='warning',
        message=f'Subscription was deleted for user {instance.user.username} on plan {instance.plan.name}'
    )

@receiver(post_delete, sender=Config)
def config_post_delete(sender, instance, **kwargs):
    ServiceLog.objects.create(
        service=instance.service,
        level='warning',
        message=f'Configuration {instance.key} was deleted from service {instance.service.name}'
    ) 