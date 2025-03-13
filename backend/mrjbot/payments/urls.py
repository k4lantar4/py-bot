from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r'transactions', views.TransactionViewSet, basename='transaction')
router.register(r'commissions', views.CommissionViewSet, basename='commission')
router.register(r'withdrawals', views.WithdrawalRequestViewSet, basename='withdrawal')
router.register(r'cards', views.CardViewSet, basename='card')

urlpatterns = [
    # Payment management
    path('', include(router.urls)),
    
    # Transaction management
    path('transactions/<int:pk>/verify/', views.TransactionVerifyView.as_view(), name='transaction_verify'),
    path('transactions/<int:pk>/cancel/', views.TransactionCancelView.as_view(), name='transaction_cancel'),
    path('transactions/<int:pk>/refund/', views.TransactionRefundView.as_view(), name='transaction_refund'),
    
    # Commission management
    path('commissions/<int:pk>/calculate/', views.CommissionCalculateView.as_view(), name='commission_calculate'),
    path('commissions/<int:pk>/withdraw/', views.CommissionWithdrawView.as_view(), name='commission_withdraw'),
    
    # Withdrawal management
    path('withdrawals/<int:pk>/approve/', views.WithdrawalApproveView.as_view(), name='withdrawal_approve'),
    path('withdrawals/<int:pk>/reject/', views.WithdrawalRejectView.as_view(), name='withdrawal_reject'),
    path('withdrawals/<int:pk>/process/', views.WithdrawalProcessView.as_view(), name='withdrawal_process'),
    
    # Card management
    path('cards/<int:pk>/verify/', views.CardVerifyView.as_view(), name='card_verify'),
    path('cards/<int:pk>/block/', views.CardBlockView.as_view(), name='card_block'),
    path('cards/<int:pk>/unblock/', views.CardUnblockView.as_view(), name='card_unblock'),
    
    # Payment gateway integration
    path('gateways/', views.PaymentGatewayListView.as_view(), name='gateway_list'),
    path('gateways/<str:gateway>/callback/', views.PaymentGatewayCallbackView.as_view(), name='gateway_callback'),
    path('gateways/<str:gateway>/webhook/', views.PaymentGatewayWebhookView.as_view(), name='gateway_webhook'),
    
    # Payment reports
    path('reports/sales/', views.SalesReportView.as_view(), name='sales_report'),
    path('reports/commissions/', views.CommissionReportView.as_view(), name='commission_report'),
    path('reports/withdrawals/', views.WithdrawalReportView.as_view(), name='withdrawal_report'),
] 