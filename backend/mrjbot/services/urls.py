from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r'services', views.ServiceViewSet, basename='service')
router.register(r'plans', views.PlanViewSet, basename='plan')
router.register(r'subscriptions', views.SubscriptionViewSet, basename='subscription')
router.register(r'configs', views.ConfigViewSet, basename='config')
router.register(r'usage', views.UsageViewSet, basename='usage')
router.register(r'logs', views.ServiceLogViewSet, basename='log')
router.register(r'metrics', views.ServiceMetricViewSet, basename='metric')
router.register(r'alerts', views.ServiceAlertViewSet, basename='alert')

urlpatterns = [
    # Service management
    path('', include(router.urls)),
    
    # Service-specific endpoints
    path('services/<int:pk>/status/', views.ServiceStatusView.as_view(), name='service_status'),
    path('services/<int:pk>/usage/', views.ServiceUsageView.as_view(), name='service_usage'),
    path('services/<int:pk>/config/', views.ServiceConfigView.as_view(), name='service_config'),
    
    # Plan management
    path('plans/<int:pk>/features/', views.PlanFeaturesView.as_view(), name='plan_features'),
    path('plans/<int:pk>/pricing/', views.PlanPricingView.as_view(), name='plan_pricing'),
    
    # Subscription management
    path('subscriptions/<int:pk>/renew/', views.SubscriptionRenewView.as_view(), name='subscription_renew'),
    path('subscriptions/<int:pk>/cancel/', views.SubscriptionCancelView.as_view(), name='subscription_cancel'),
    path('subscriptions/<int:pk>/upgrade/', views.SubscriptionUpgradeView.as_view(), name='subscription_upgrade'),
    path('subscriptions/<int:pk>/downgrade/', views.SubscriptionDowngradeView.as_view(), name='subscription_downgrade'),
    
    # Usage tracking
    path('usage/history/', views.UsageHistoryView.as_view(), name='usage_history'),
    path('usage/limits/', views.UsageLimitsView.as_view(), name='usage_limits'),
    
    # Service monitoring
    path('monitoring/status/', views.MonitoringStatusView.as_view(), name='monitoring_status'),
    path('monitoring/metrics/', views.MonitoringMetricsView.as_view(), name='monitoring_metrics'),
] 