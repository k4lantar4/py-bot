from django.urls import path
from . import views

app_name = 'payments'

urlpatterns = [
    # User-facing payment views
    path('methods/', views.payment_methods, name='payment_methods'),
    path('create/', views.create_transaction, name='create_transaction'),
    path('transaction/<int:transaction_id>/', views.transaction_detail, name='transaction_detail'),
    path('history/', views.user_transactions, name='user_transactions'),
    
    # Card payment specific views
    path('card/verify/', views.verify_card_payment, name='verify_card_payment'),
    
    # Zarinpal specific views
    path('zarinpal/callback/', views.zarinpal_callback, name='zarinpal_callback'),
    
    # Admin views
    path('admin/pending/', views.admin_pending_payments, name='admin_pending_payments'),
    path('admin/verify/', views.admin_verify_payment, name='admin_verify_payment'),
] 