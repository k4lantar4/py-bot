import json
import logging
from django.conf import settings
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST, require_GET
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from django.utils import timezone
from django.db import models

from .models import Transaction, ZarinpalPayment, CardPayment
from .zarinpal import ZarinpalGateway
from .card_payment import CardPaymentProcessor

logger = logging.getLogger(__name__)

@login_required
def payment_methods(request):
    """Display available payment methods"""
    context = {
        'zarinpal_enabled': hasattr(settings, 'ZARINPAL_MERCHANT') and settings.ZARINPAL_MERCHANT,
        'card_payment_enabled': hasattr(settings, 'CARD_PAYMENT_ENABLED') and settings.CARD_PAYMENT_ENABLED,
        'card_payment_card_number': settings.CARD_PAYMENT_CARD_NUMBER,
        'card_payment_card_holder': settings.CARD_PAYMENT_CARD_HOLDER,
        'card_payment_bank_name': settings.CARD_PAYMENT_BANK_NAME,
    }
    return render(request, 'payments/payment_methods.html', context)

@login_required
@require_POST
def create_transaction(request):
    """Create a new transaction"""
    try:
        data = json.loads(request.body)
        amount = data.get('amount')
        payment_method = data.get('payment_method')
        transaction_type = data.get('type', 'deposit')  # Default to deposit
        description = data.get('description', 'Wallet deposit')
        
        # Validate amount
        try:
            amount = int(amount)
            if amount <= 0:
                return JsonResponse({'success': False, 'error': 'Amount must be positive'})
        except (ValueError, TypeError):
            return JsonResponse({'success': False, 'error': 'Invalid amount'})
        
        # Create transaction
        transaction = Transaction.objects.create(
            user=request.user,
            amount=amount,
            type=transaction_type,
            status='pending',
            description=description
        )
        
        # Handle different payment methods
        if payment_method == 'zarinpal':
            # Redirect to Zarinpal payment
            gateway = ZarinpalGateway()
            result = gateway.request_payment(
                transaction_id=transaction.id,
                amount=amount,
                description=description,
                email=data.get('email'),
                mobile=data.get('mobile')
            )
            
            if result['success']:
                return JsonResponse({
                    'success': True,
                    'redirect_url': result['payment_url'],
                    'transaction_id': transaction.id
                })
            else:
                # Delete transaction if payment request failed
                transaction.delete()
                return JsonResponse({
                    'success': False,
                    'error': result['error_message']
                })
                
        elif payment_method == 'card':
            # Create card payment
            card_processor = CardPaymentProcessor()
            result = card_processor.create_payment(
                transaction_id=transaction.id,
                card_number=data.get('card_number'),
                reference_number=data.get('reference_number'),
                transfer_time=data.get('transfer_time')
            )
            
            if result['success']:
                return JsonResponse({
                    'success': True,
                    'transaction_id': transaction.id,
                    'verification_code': result['verification_code'],
                    'expires_at': result['expires_at'].isoformat(),
                    'message': 'Payment created successfully. Please complete the transfer and use the verification code for reference.'
                })
            else:
                # Delete transaction if payment creation failed
                transaction.delete()
                return JsonResponse({
                    'success': False,
                    'error': result['error_message']
                })
        else:
            # Invalid payment method
            transaction.delete()
            return JsonResponse({
                'success': False,
                'error': 'Invalid payment method'
            })
            
    except Exception as e:
        logger.error(f"Error creating transaction: {str(e)}")
        return JsonResponse({
            'success': False,
            'error': 'An error occurred while processing your request'
        })

@login_required
def transaction_detail(request, transaction_id):
    """View transaction details"""
    transaction = get_object_or_404(Transaction, id=transaction_id, user=request.user)
    
    # Get payment details based on transaction type
    payment_details = None
    payment_type = None
    
    try:
        # Check for Zarinpal payment
        zarinpal_payment = ZarinpalPayment.objects.filter(transaction=transaction).first()
        if zarinpal_payment:
            payment_details = zarinpal_payment
            payment_type = 'zarinpal'
    except Exception:
        pass
        
    try:
        # Check for Card payment
        card_payment = CardPayment.objects.filter(transaction=transaction).first()
        if card_payment:
            payment_details = card_payment
            payment_type = 'card'
    except Exception:
        pass
    
    context = {
        'transaction': transaction,
        'payment_details': payment_details,
        'payment_type': payment_type
    }
    
    return render(request, 'payments/transaction_detail.html', context)

@csrf_exempt
def zarinpal_callback(request):
    """Handle Zarinpal payment callback"""
    authority = request.GET.get('Authority', '')
    status = request.GET.get('Status', '')
    
    if not authority:
        return render(request, 'payments/payment_result.html', {
            'success': False,
            'message': 'Invalid payment data'
        })
    
    # Verify payment with Zarinpal
    gateway = ZarinpalGateway()
    result = gateway.verify_payment(authority)
    
    if result['success']:
        # Get transaction
        try:
            zarinpal_payment = ZarinpalPayment.objects.get(authority=authority)
            transaction = zarinpal_payment.transaction
            
            return render(request, 'payments/payment_result.html', {
                'success': True,
                'transaction': transaction,
                'ref_id': result.get('ref_id'),
                'message': 'Payment completed successfully'
            })
        except ZarinpalPayment.DoesNotExist:
            return render(request, 'payments/payment_result.html', {
                'success': False,
                'message': 'Payment record not found'
            })
    else:
        return render(request, 'payments/payment_result.html', {
            'success': False,
            'message': result.get('error_message', 'Payment verification failed')
        })

@login_required
@require_POST
def verify_card_payment(request):
    """Verify a card payment with verification code"""
    try:
        data = json.loads(request.body)
        verification_code = data.get('verification_code')
        
        if not verification_code:
            return JsonResponse({
                'success': False,
                'error': 'Verification code is required'
            })
        
        # Verify payment
        card_processor = CardPaymentProcessor()
        result = card_processor.verify_payment(verification_code)
        
        return JsonResponse(result)
    except Exception as e:
        logger.error(f"Error verifying card payment: {str(e)}")
        return JsonResponse({
            'success': False,
            'error': 'An error occurred during payment verification'
        })

@login_required
def user_transactions(request):
    """View user's transaction history"""
    transactions = Transaction.objects.filter(user=request.user).order_by('-created_at')
    
    # Calculate transaction statistics
    completed_count = transactions.filter(status='completed').count()
    pending_count = transactions.filter(status='pending').count()
    failed_count = transactions.filter(status__in=['failed', 'expired']).count()
    total_amount = transactions.filter(status='completed').aggregate(total=models.Sum('amount'))['total'] or 0
    
    context = {
        'transactions': transactions,
        'completed_count': completed_count,
        'pending_count': pending_count,
        'failed_count': failed_count,
        'total_amount': total_amount
    }
    
    return render(request, 'payments/user_transactions.html', context)

# Admin views
@login_required
def admin_pending_payments(request):
    """View pending payments for admin verification"""
    if not request.user.is_staff:
        return redirect('home')
    
    # Get pending card payments
    pending_payments = CardPayment.objects.filter(
        status='pending',
        transaction__status='pending'
    ).select_related('transaction__user').order_by('-created_at')
    
    context = {
        'pending_payments': pending_payments
    }
    
    return render(request, 'payments/admin_pending_payments.html', context)

@login_required
@require_POST
def admin_verify_payment(request):
    """Admin verification of card payments"""
    if not request.user.is_staff:
        return JsonResponse({'success': False, 'error': 'Unauthorized'})
    
    try:
        data = json.loads(request.body)
        payment_id = data.get('payment_id')
        action = data.get('action')  # 'verify' or 'reject'
        
        if not payment_id or not action:
            return JsonResponse({
                'success': False,
                'error': 'Payment ID and action are required'
            })
        
        if action not in ['verify', 'reject']:
            return JsonResponse({
                'success': False,
                'error': 'Invalid action'
            })
        
        # Process verification
        card_processor = CardPaymentProcessor()
        result = card_processor.admin_verify_payment(
            payment_id=payment_id,
            admin_user=request.user,
            action=action
        )
        
        return JsonResponse(result)
        
    except Exception as e:
        logger.error(f"Error in admin payment verification: {str(e)}")
        return JsonResponse({
            'success': False,
            'error': 'An error occurred while processing the payment verification'
        })
