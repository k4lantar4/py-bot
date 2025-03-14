from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import (
    TokenRefreshView,
    TokenVerifyView,
)

from .views import (
    AuthViewSet,
    ServiceViewSet,
    PlanViewSet,
    SubscriptionViewSet,
    PaymentViewSet,
    TransactionViewSet,
    CommissionViewSet,
    WithdrawalRequestViewSet,
    NotificationViewSet,
    SettingViewSet,
    UserSettingViewSet,
)

router = DefaultRouter()
router.register(r'auth', AuthViewSet, basename='auth')
router.register(r'services', ServiceViewSet, basename='service')
router.register(r'plans', PlanViewSet, basename='plan')
router.register(r'subscriptions', SubscriptionViewSet, basename='subscription')
router.register(r'payments', PaymentViewSet, basename='payment')
router.register(r'transactions', TransactionViewSet, basename='transaction')
router.register(r'commissions', CommissionViewSet, basename='commission')
router.register(r'withdrawals', WithdrawalRequestViewSet, basename='withdrawal')
router.register(r'notifications', NotificationViewSet, basename='notification')
router.register(r'settings', SettingViewSet, basename='setting')
router.register(r'user-settings', UserSettingViewSet, basename='user-setting')

urlpatterns = [
    path('', include(router.urls)),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('token/verify/', TokenVerifyView.as_view(), name='token_verify'),
] 