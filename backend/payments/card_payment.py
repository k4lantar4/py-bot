import logging
from django.utils import timezone
from django.conf import settings
from datetime import timedelta
from .models import Transaction, CardPayment

logger = logging.getLogger(__name__)

class CardPaymentProcessor:
    """Processor for card-to-card payments"""
    
    def __init__(self):
        """Initialize the card payment processor"""
        self.card_number = settings.CARD_NUMBER
        self.card_holder = settings.CARD_HOLDER
        self.verification_timeout = getattr(settings, 'CARD_PAYMENT_VERIFICATION_TIMEOUT_MINUTES', 30)
    
    def create_payment(self, transaction_id, card_number, reference_number, transfer_time):
        """Create a card payment record"""
        try:
            # Get transaction
            transaction = Transaction.objects.get(id=transaction_id)
            
            # Calculate expiry time
            expires_at = timezone.now() + timedelta(minutes=self.verification_timeout)
            
            # Create card payment record
            card_payment = CardPayment.objects.create(
                transaction=transaction,
                card_number=card_number,
                reference_number=reference_number,
                transfer_time=transfer_time,
                expires_at=expires_at,
                status='pending'
            )
            
            return {
                "success": True,
                "verification_code": card_payment.verification_code,
                "expires_at": expires_at,
                "transaction_id": transaction.id
            }
        except Transaction.DoesNotExist:
            logger.error(f"Transaction with ID {transaction_id} does not exist")
            return {
                "success": False,
                "error_message": "Transaction not found"
            }
        except Exception as e:
            logger.error(f"Error creating card payment: {str(e)}")
            return {
                "success": False,
                "error_message": str(e)
            }
    
    def verify_payment(self, verification_code, admin_user=None, admin_note=None):
        """Verify a card payment"""
        try:
            # Get card payment
            card_payment = CardPayment.objects.get(verification_code=verification_code)
            transaction = card_payment.transaction
            
            # Check if payment is already verified or rejected
            if card_payment.status == 'verified':
                return {
                    "success": True,
                    "message": "Payment already verified",
                    "transaction_id": transaction.id
                }
            elif card_payment.status == 'rejected':
                return {
                    "success": False,
                    "error_message": "Payment already rejected",
                    "transaction_id": transaction.id
                }
            
            # Check if payment is expired
            if card_payment.is_expired():
                # Update card payment record
                card_payment.status = 'expired'
                card_payment.save()
                
                # Update transaction
                transaction.status = 'expired'
                transaction.save()
                
                return {
                    "success": False,
                    "error_message": "Payment verification expired",
                    "transaction_id": transaction.id
                }
            
            # Update card payment record
            card_payment.status = 'verified'
            card_payment.verified_by = admin_user
            card_payment.verified_at = timezone.now()
            if admin_note:
                card_payment.admin_note = admin_note
            card_payment.save()
            
            # Update transaction
            transaction.status = 'completed'
            transaction.transaction_id = verification_code
            transaction.save()
            
            return {
                "success": True,
                "message": "Payment verified successfully",
                "transaction_id": transaction.id
            }
        except CardPayment.DoesNotExist:
            logger.error(f"Card payment with verification code {verification_code} does not exist")
            return {
                "success": False,
                "error_message": "Payment not found"
            }
        except Exception as e:
            logger.error(f"Error verifying card payment: {str(e)}")
            return {
                "success": False,
                "error_message": str(e)
            }
    
    def reject_payment(self, verification_code, admin_user=None, admin_note=None):
        """Reject a card payment"""
        try:
            # Get card payment
            card_payment = CardPayment.objects.get(verification_code=verification_code)
            transaction = card_payment.transaction
            
            # Check if payment is already verified or rejected
            if card_payment.status == 'verified':
                return {
                    "success": False,
                    "error_message": "Payment already verified",
                    "transaction_id": transaction.id
                }
            elif card_payment.status == 'rejected':
                return {
                    "success": True,
                    "message": "Payment already rejected",
                    "transaction_id": transaction.id
                }
            
            # Update card payment record
            card_payment.status = 'rejected'
            card_payment.verified_by = admin_user
            card_payment.verified_at = timezone.now()
            if admin_note:
                card_payment.admin_note = admin_note
            card_payment.save()
            
            # Update transaction
            transaction.status = 'failed'
            transaction.save()
            
            return {
                "success": True,
                "message": "Payment rejected successfully",
                "transaction_id": transaction.id
            }
        except CardPayment.DoesNotExist:
            logger.error(f"Card payment with verification code {verification_code} does not exist")
            return {
                "success": False,
                "error_message": "Payment not found"
            }
        except Exception as e:
            logger.error(f"Error rejecting card payment: {str(e)}")
            return {
                "success": False,
                "error_message": str(e)
            }
    
    def get_payment_info(self, verification_code):
        """Get information about a card payment"""
        try:
            # Get card payment
            card_payment = CardPayment.objects.get(verification_code=verification_code)
            transaction = card_payment.transaction
            
            return {
                "success": True,
                "payment": {
                    "verification_code": card_payment.verification_code,
                    "card_number": card_payment.card_number,
                    "reference_number": card_payment.reference_number,
                    "transfer_time": card_payment.transfer_time,
                    "status": card_payment.status,
                    "expires_at": card_payment.expires_at,
                    "is_expired": card_payment.is_expired(),
                    "admin_note": card_payment.admin_note,
                    "verified_at": card_payment.verified_at,
                    "verified_by": card_payment.verified_by.username if card_payment.verified_by else None,
                },
                "transaction": {
                    "id": transaction.id,
                    "user": transaction.user.username,
                    "amount": transaction.amount,
                    "status": transaction.status,
                    "type": transaction.type,
                    "description": transaction.description,
                    "created_at": transaction.created_at,
                }
            }
        except CardPayment.DoesNotExist:
            logger.error(f"Card payment with verification code {verification_code} does not exist")
            return {
                "success": False,
                "error_message": "Payment not found"
            }
        except Exception as e:
            logger.error(f"Error getting card payment info: {str(e)}")
            return {
                "success": False,
                "error_message": str(e)
            }
    
    def get_pending_payments(self):
        """Get all pending card payments"""
        try:
            # Get all pending card payments
            pending_payments = CardPayment.objects.filter(status='pending')
            
            result = []
            for payment in pending_payments:
                transaction = payment.transaction
                result.append({
                    "verification_code": payment.verification_code,
                    "card_number": payment.card_number,
                    "reference_number": payment.reference_number,
                    "transfer_time": payment.transfer_time,
                    "expires_at": payment.expires_at,
                    "is_expired": payment.is_expired(),
                    "transaction": {
                        "id": transaction.id,
                        "user": transaction.user.username,
                        "amount": transaction.amount,
                        "description": transaction.description,
                        "created_at": transaction.created_at,
                    }
                })
            
            return {
                "success": True,
                "payments": result
            }
        except Exception as e:
            logger.error(f"Error getting pending card payments: {str(e)}")
            return {
                "success": False,
                "error_message": str(e)
            }
    
    def expire_old_payments(self):
        """Expire old pending card payments"""
        try:
            # Get all pending card payments that have expired
            now = timezone.now()
            expired_payments = CardPayment.objects.filter(
                status='pending',
                expires_at__lt=now
            )
            
            count = 0
            for payment in expired_payments:
                # Update card payment record
                payment.status = 'expired'
                payment.save()
                
                # Update transaction
                transaction = payment.transaction
                transaction.status = 'expired'
                transaction.save()
                
                count += 1
            
            return {
                "success": True,
                "expired_count": count
            }
        except Exception as e:
            logger.error(f"Error expiring old card payments: {str(e)}")
            return {
                "success": False,
                "error_message": str(e)
            } 