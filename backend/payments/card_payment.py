import logging
import uuid
from django.conf import settings
from django.utils import timezone
from datetime import timedelta
from .models import Transaction, CardPayment

logger = logging.getLogger(__name__)

class CardPaymentProcessor:
    """Card payment processor for manual card-to-card payments"""
    
    def __init__(self):
        """Initialize the card payment processor"""
        self.admin_notification_enabled = getattr(settings, 'ADMIN_NOTIFICATION_ENABLED', True)
        self.verification_timeout_minutes = getattr(settings, 'CARD_PAYMENT_VERIFICATION_TIMEOUT_MINUTES', 30)
        self.card_number = getattr(settings, 'CARD_PAYMENT_NUMBER', '')
        self.card_holder = getattr(settings, 'CARD_PAYMENT_HOLDER', '')
        self.bank_name = getattr(settings, 'CARD_PAYMENT_BANK', '')
    
    def create_payment(self, transaction_id, card_number, reference_number, transfer_time):
        """Create a new card payment"""
        try:
            # Get transaction
            transaction = Transaction.objects.get(id=transaction_id)
            
            # Calculate expiry time
            expires_at = timezone.now() + timedelta(minutes=self.verification_timeout_minutes)
            
            # Create card payment record
            card_payment = CardPayment.objects.create(
                transaction=transaction,
                card_number=card_number,
                reference_number=reference_number,
                transfer_time=transfer_time,
                status='pending',
                expires_at=expires_at
            )
            
            # Send notification to admin if enabled
            if self.admin_notification_enabled:
                self._notify_admin_new_payment(card_payment)
            
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
    
    def verify_payment(self, verification_code):
        """Check the status of a card payment"""
        try:
            # Get card payment
            card_payment = CardPayment.objects.get(verification_code=verification_code)
            transaction = card_payment.transaction
            
            # Check payment status
            if card_payment.status == 'verified':
                return {
                    "success": True,
                    "status": "verified",
                    "transaction_id": transaction.id
                }
            elif card_payment.status == 'rejected':
                return {
                    "success": False,
                    "status": "rejected",
                    "error_message": card_payment.admin_note or "Payment was rejected by administrator",
                    "transaction_id": transaction.id
                }
            elif card_payment.status == 'expired' or card_payment.is_expired():
                # Update status if expired but not marked
                if card_payment.status != 'expired':
                    card_payment.status = 'expired'
                    card_payment.save()
                    
                    # Update transaction status
                    transaction.status = 'expired'
                    transaction.save()
                
                return {
                    "success": False,
                    "status": "expired",
                    "error_message": "Payment verification time has expired",
                    "transaction_id": transaction.id
                }
            else:
                # Payment still pending
                return {
                    "success": True,
                    "status": "pending",
                    "message": "Payment is pending verification by administrator",
                    "transaction_id": transaction.id,
                    "expires_at": card_payment.expires_at
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
    
    def admin_verify_payment(self, card_payment_id, admin_user, approved=True, note=None):
        """Admin verification of card payment"""
        try:
            # Get card payment
            card_payment = CardPayment.objects.get(id=card_payment_id)
            transaction = card_payment.transaction
            
            # Check if payment is already verified or rejected
            if card_payment.status in ['verified', 'rejected']:
                return {
                    "success": False,
                    "error_message": f"Payment already {card_payment.status}",
                    "transaction_id": transaction.id
                }
            
            # Check if payment is expired
            if card_payment.is_expired():
                card_payment.status = 'expired'
                card_payment.save()
                
                # Update transaction status
                transaction.status = 'expired'
                transaction.save()
                
                return {
                    "success": False,
                    "error_message": "Payment verification time has expired",
                    "transaction_id": transaction.id
                }
            
            # Update payment status based on admin decision
            if approved:
                card_payment.status = 'verified'
                transaction.status = 'completed'
                
                # Update user wallet if this was a deposit
                if transaction.type == 'deposit':
                    user = transaction.user
                    user.wallet_balance += transaction.amount
                    user.save()
                
                # Activate subscription if this was a purchase
                if transaction.type == 'purchase' and hasattr(transaction, 'subscription'):
                    subscription = transaction.subscription
                    if subscription and subscription.status == 'pending':
                        subscription.status = 'active'
                        subscription.save()
                        
                        # Create client in 3X-UI panel
                        from v2ray.api_client import create_client
                        create_client(subscription.id)
            else:
                card_payment.status = 'rejected'
                transaction.status = 'failed'
            
            # Update card payment record
            card_payment.verified_by = admin_user
            card_payment.verified_at = timezone.now()
            card_payment.admin_note = note
            card_payment.save()
            
            # Update transaction
            transaction.save()
            
            # Send notification to user
            self._notify_user_payment_status(card_payment)
            
            return {
                "success": True,
                "status": card_payment.status,
                "transaction_id": transaction.id
            }
        except CardPayment.DoesNotExist:
            logger.error(f"Card payment with ID {card_payment_id} does not exist")
            return {
                "success": False,
                "error_message": "Payment not found"
            }
        except Exception as e:
            logger.error(f"Error verifying card payment by admin: {str(e)}")
            return {
                "success": False,
                "error_message": str(e)
            }
    
    def get_payment_details(self):
        """Get card payment details for display to users"""
        return {
            "card_number": self.card_number,
            "card_holder": self.card_holder,
            "bank_name": self.bank_name,
            "verification_timeout_minutes": self.verification_timeout_minutes
        }
    
    def _notify_admin_new_payment(self, card_payment):
        """Send notification to admin about new card payment"""
        try:
            from telegrambot.services.notifications import AdminNotificationService
            
            transaction = card_payment.transaction
            user = transaction.user
            
            message = f"🔔 *New Card Payment*\n\n"
            message += f"👤 User: {user.username}\n"
            message += f"💰 Amount: {transaction.amount} Toman\n"
            message += f"💳 Card: {card_payment.card_number}\n"
            message += f"📝 Reference: {card_payment.reference_number}\n"
            message += f"⏱ Transfer Time: {card_payment.transfer_time.strftime('%Y-%m-%d %H:%M:%S')}\n"
            message += f"🔑 Verification Code: {card_payment.verification_code}\n"
            message += f"⏳ Expires at: {card_payment.expires_at.strftime('%Y-%m-%d %H:%M:%S')}\n\n"
            message += f"Use the admin panel to verify this payment."
            
            notification_service = AdminNotificationService()
            notification_service.send_message(message)
            
            return True
        except ImportError:
            logger.warning("AdminNotificationService not available, admin notification not sent")
            return False
        except Exception as e:
            logger.error(f"Error sending admin notification: {str(e)}")
            return False
    
    def _notify_user_payment_status(self, card_payment):
        """Send notification to user about payment status"""
        try:
            from telegrambot.services.notifications import UserNotificationService
            
            transaction = card_payment.transaction
            user = transaction.user
            
            if card_payment.status == 'verified':
                message = f"✅ *Payment Verified*\n\n"
                message += f"💰 Amount: {transaction.amount} Toman\n"
                message += f"🔑 Verification Code: {card_payment.verification_code}\n"
                message += f"⏱ Verified at: {card_payment.verified_at.strftime('%Y-%m-%d %H:%M:%S')}\n\n"
                message += f"Your account has been credited with {transaction.amount} Toman."
            
            elif card_payment.status == 'rejected':
                message = f"❌ *Payment Rejected*\n\n"
                message += f"💰 Amount: {transaction.amount} Toman\n"
                message += f"🔑 Verification Code: {card_payment.verification_code}\n"
                message += f"⏱ Rejected at: {card_payment.verified_at.strftime('%Y-%m-%d %H:%M:%S') if card_payment.verified_at else 'N/A'}\n"
                
                if card_payment.admin_note:
                    message += f"📝 Reason: {card_payment.admin_note}\n\n"
                else:
                    message += f"\nPlease contact support for more information."
            
            elif card_payment.status == 'expired':
                message = f"⌛ *Payment Expired*\n\n"
                message += f"💰 Amount: {transaction.amount} Toman\n"
                message += f"🔑 Verification Code: {card_payment.verification_code}\n"
                message += f"⏱ Expired at: {card_payment.expires_at.strftime('%Y-%m-%d %H:%M:%S')}\n\n"
                message += f"Please create a new payment if you wish to continue."
            
            else:
                return False
                
            notification_service = UserNotificationService()
            notification_service.send_message(user, message)
            
            return True
        except ImportError:
            logger.warning("UserNotificationService not available, user notification not sent")
            return False
        except Exception as e:
            logger.error(f"Error sending user notification: {str(e)}")
            return False 