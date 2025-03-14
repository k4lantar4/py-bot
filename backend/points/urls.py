from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r'transactions', views.PointsTransactionViewSet, basename='points-transaction')
router.register(r'rules', views.PointsRedemptionRuleViewSet, basename='points-rule')
router.register(r'redemptions', views.PointsRedemptionViewSet, basename='points-redemption')

urlpatterns = [
    path('', include(router.urls)),
] 