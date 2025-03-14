from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

# Create a router and register our viewsets with it
router = DefaultRouter()
router.register(r'users', views.UserViewSet)
router.register(r'servers', views.ServerViewSet)
router.register(r'subscription-plans', views.SubscriptionPlanViewSet)
router.register(r'subscriptions', views.SubscriptionViewSet)
router.register(r'inbounds', views.InboundViewSet)
router.register(r'clients', views.ClientViewSet)
router.register(r'transactions', views.TransactionViewSet)
router.register(r'card-payments', views.CardPaymentViewSet)
router.register(r'zarinpal-payments', views.ZarinpalPaymentViewSet)
router.register(r'payment-methods', views.PaymentMethodViewSet)
router.register(r'discounts', views.DiscountViewSet)
router.register(r'telegram-messages', views.TelegramMessageViewSet)
router.register(r'telegram-notifications', views.TelegramNotificationViewSet)
router.register(r'plan-suggestions', views.PlanSuggestionViewSet, basename='plan-suggestion')
router.register(r'points-rules', views.PointsRedemptionRuleViewSet, basename='points-rule')
router.register(r'points-redemptions', views.PointsRedemptionViewSet, basename='points-redemption')

# The API URLs are now determined automatically by the router
urlpatterns = [
    path('', include(router.urls)),
    # Add the BotConfig endpoint
    path('bot/config/', views.BotConfigView.as_view(), name='bot-config'),
] 