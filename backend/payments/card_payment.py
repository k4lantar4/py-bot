import logging
import uuid
from django.conf import settings
from django.utils import timezone
from datetime import timedelta
from .models import Transaction, CardPayment, CardOwner
from .ocr_verification import ReceiptOCRProcessor
from notifications.telegram import send_admin_notification, send_user_notification
from django.db import transaction

logger = logging.getLogger(__name__)

class CardPaymentProcessor:
    """Process card to card payments with OCR verification and card owner tracking"""
    
    def __init__(self):
        """Initialize the card payment processor"""
        self.admin_notification_enabled = getattr(settings, 'ADMIN_NOTIFICATION_ENABLED', True)
        self.verification_timeout_minutes = getattr(settings, 'CARD_PAYMENT_VERIFICATION_TIMEOUT_MINUTES', 30)
        self.card_number = getattr(settings, 'CARD_PAYMENT_NUMBER', '')
        self.card_holder = getattr(settings, 'CARD_PAYMENT_HOLDER', '')
        self.bank_name = getattr(settings, 'CARD_PAYMENT_BANK', '')
        self.ocr_processor = ReceiptOCRProcessor()
    
    def create_payment(self, user, amount, card_owner_id=None, verification_method='manual'):
        """Create a new card payment"""
        try:
            with transaction.atomic():
                # Create transaction
                tx = Transaction.objects.create(
                    user=user,
                    amount=amount,
                    type='deposit',
                    description='Card to card payment'
                )
                
                # Get card owner if provided
                card_owner = None
                if card_owner_id:
                    try:
                        card_owner = CardOwner.objects.get(id=card_owner_id, is_active=True)
                    except CardOwner.DoesNotExist:
                        logger.warning(f"Card owner {card_owner_id} not found or inactive")
                
                # Create card payment
                payment = CardPayment.objects.create(
                    transaction=tx,
                    card_owner=card_owner,
                    card_number=card_owner.card_number if card_owner else None,
                    verification_method=verification_method
                )
                
                # Send notifications
                self._notify_payment_created(payment)
                
                return payment
                
        except Exception as e:
            logger.error(f"Error creating card payment: {str(e)}")
            raise
    
    def verify_payment(self, payment_id, admin_user, receipt_image=None, admin_note=''):
        """Verify a card payment with optional OCR verification"""
        try:
            payment = CardPayment.objects.select_for_update().get(id=payment_id)
            
            if payment.is_expired():
                payment.status = 'expired'
                payment.save()
                self._notify_payment_expired(payment)
                return False, "Payment has expired"
            
            # Perform OCR verification if receipt image is provided
            ocr_verified = False
            if receipt_image and payment.verification_method in ['ocr', 'both']:
                ocr_verified, ocr_message = self.ocr_processor.verify_payment(payment_id, receipt_image)
                if not ocr_verified and payment.verification_method == 'ocr':
                    payment.status = 'retry'
                    payment.admin_note = f"OCR verification failed: {ocr_message}"
                    payment.save()
                    self._notify_payment_retry(payment)
                    return False, ocr_message
            
            # Manual verification by admin
            if payment.verification_method in ['manual', 'both']:
                with transaction.atomic():
                    # Update payment status
                    payment.status = 'verified'
                    payment.verified_by = admin_user
                    payment.verified_at = timezone.now()
                    payment.admin_note = admin_note
                    payment.save()
                    
                    # Update transaction status
                    payment.transaction.status = 'completed'
                    payment.transaction.save()
                    
                    # Update card owner if exists
                    if payment.card_owner and not payment.card_owner.is_verified:
                        payment.card_owner.verify(admin_user)
                    
                    # Send notifications
                    self._notify_payment_verified(payment)
                    
                    return True, "Payment verified successfully"
            
            return False, "Invalid verification method"
            
        except CardPayment.DoesNotExist:
            logger.error(f"Payment {payment_id} not found")
            return False, "Payment not found"
        except Exception as e:
            logger.error(f"Error verifying payment: {str(e)}")
            return False, str(e)
    
    def reject_payment(self, payment_id, admin_user, reason=''):
        """Reject a card payment"""
        try:
            with transaction.atomic():
                payment = CardPayment.objects.select_for_update().get(id=payment_id)
                
                if payment.status == 'verified':
                    return False, "Cannot reject a verified payment"
                
                payment.status = 'rejected'
                payment.verified_by = admin_user
                payment.verified_at = timezone.now()
                payment.admin_note = reason
                payment.save()
                
                payment.transaction.status = 'failed'
                payment.transaction.save()
                
                # Send notifications
                self._notify_payment_rejected(payment)
                
                return True, "Payment rejected successfully"
                
        except CardPayment.DoesNotExist:
            logger.error(f"Payment {payment_id} not found")
            return False, "Payment not found"
        except Exception as e:
            logger.error(f"Error rejecting payment: {str(e)}")
            return False, str(e)
    
    def retry_payment(self, payment_id):
        """Retry a failed or expired payment"""
        try:
            payment = CardPayment.objects.get(id=payment_id)
            
            if payment.can_retry():
                success = payment.retry_payment()
                if success:
                    self._notify_payment_retry(payment)
                    return True, "Payment retry initiated"
                return False, "Could not retry payment"
            
            return False, "Payment cannot be retried"
            
        except CardPayment.DoesNotExist:
            logger.error(f"Payment {payment_id} not found")
            return False, "Payment not found"
        except Exception as e:
            logger.error(f"Error retrying payment: {str(e)}")
            return False, str(e)
    
    def _notify_payment_created(self, payment):
        """Send notifications for new payment"""
        user_msg = (
            f"🏦 پرداخت جدید ایجاد شد!\n\n"
            f"💰 مبلغ: {payment.transaction.amount:,} تومان\n"
            f"🔑 کد پیگیری: {payment.verification_code}\n"
            f"⏰ مهلت پرداخت: {payment.expires_at.strftime('%H:%M:%S')}\n\n"
            f"لطفا مبلغ را به کارت زیر واریز کنید:\n"
            f"💳 {payment.card_number if payment.card_number else 'در انتظار تخصیص کارت'}"
        )
        
        admin_msg = (
            f"💫 درخواست پرداخت جدید\n\n"
            f"👤 کاربر: {payment.transaction.user.username}\n"
            f"💰 مبلغ: {payment.transaction.amount:,} تومان\n"
            f"🔑 کد پیگیری: {payment.verification_code}"
        )
        
        send_user_notification(payment.transaction.user.telegram_id, user_msg)
        send_admin_notification(admin_msg)
    
    def _notify_payment_verified(self, payment):
        """Send notifications for verified payment"""
        user_msg = (
            f"✅ پرداخت شما تایید شد!\n\n"
            f"💰 مبلغ: {payment.transaction.amount:,} تومان\n"
            f"🔑 کد پیگیری: {payment.verification_code}"
        )
        
        admin_msg = (
            f"✅ پرداخت تایید شد\n\n"
            f"👤 کاربر: {payment.transaction.user.username}\n"
            f"💰 مبلغ: {payment.transaction.amount:,} تومان\n"
            f"🔑 کد پیگیری: {payment.verification_code}\n"
            f"👨‍💼 تایید کننده: {payment.verified_by.username}"
        )
        
        send_user_notification(payment.transaction.user.telegram_id, user_msg)
        send_admin_notification(admin_msg)
    
    def _notify_payment_rejected(self, payment):
        """Send notifications for rejected payment"""
        user_msg = (
            f"❌ پرداخت شما رد شد\n\n"
            f"💰 مبلغ: {payment.transaction.amount:,} تومان\n"
            f"🔑 کد پیگیری: {payment.verification_code}\n"
            f"📝 دلیل: {payment.admin_note}"
        )
        
        admin_msg = (
            f"❌ پرداخت رد شد\n\n"
            f"👤 کاربر: {payment.transaction.user.username}\n"
            f"💰 مبلغ: {payment.transaction.amount:,} تومان\n"
            f"🔑 کد پیگیری: {payment.verification_code}\n"
            f"👨‍💼 رد کننده: {payment.verified_by.username}\n"
            f"📝 دلیل: {payment.admin_note}"
        )
        
        send_user_notification(payment.transaction.user.telegram_id, user_msg)
        send_admin_notification(admin_msg)
    
    def _notify_payment_expired(self, payment):
        """Send notifications for expired payment"""
        user_msg = (
            f"⏰ پرداخت شما منقضی شد\n\n"
            f"💰 مبلغ: {payment.transaction.amount:,} تومان\n"
            f"🔑 کد پیگیری: {payment.verification_code}"
        )
        
        admin_msg = (
            f"⏰ پرداخت منقضی شد\n\n"
            f"👤 کاربر: {payment.transaction.user.username}\n"
            f"💰 مبلغ: {payment.transaction.amount:,} تومان\n"
            f"🔑 کد پیگیری: {payment.verification_code}"
        )
        
        send_user_notification(payment.transaction.user.telegram_id, user_msg)
        send_admin_notification(admin_msg)
    
    def _notify_payment_retry(self, payment):
        """Send notifications for payment retry"""
        user_msg = (
            f"🔄 درخواست پرداخت مجدد\n\n"
            f"💰 مبلغ: {payment.transaction.amount:,} تومان\n"
            f"🔑 کد پیگیری: {payment.verification_code}\n"
            f"⏰ مهلت جدید: {payment.expires_at.strftime('%H:%M:%S')}"
        )
        
        admin_msg = (
            f"🔄 درخواست پرداخت مجدد\n\n"
            f"👤 کاربر: {payment.transaction.user.username}\n"
            f"💰 مبلغ: {payment.transaction.amount:,} تومان\n"
            f"🔑 کد پیگیری: {payment.verification_code}\n"
            f"🔢 تعداد تلاش: {payment.retry_count}/{payment.max_retries}"
        )
        
        send_user_notification(payment.transaction.user.telegram_id, user_msg)
        send_admin_notification(admin_msg)
    
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