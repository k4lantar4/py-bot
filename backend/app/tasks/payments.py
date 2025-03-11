"""Payment-related Celery tasks."""

from datetime import datetime
from typing import Dict, Optional

from celery import shared_task
from sqlalchemy.orm import Session

from ..db.session import SessionLocal
from ..models.payment import Payment, PaymentStatus, PaymentProvider
from ..models.order import Order, OrderStatus
from ..utils.logger import logger
from .notifications import send_payment_notification


@shared_task
def process_payment(payment_id: int) -> None:
    """Process a payment."""
    db = SessionLocal()
    try:
        payment = db.query(Payment).get(payment_id)
        if not payment:
            logger.error(f"Payment {payment_id} not found")
            return

        # Process payment based on provider
        try:
            if payment.provider == PaymentProvider.ZARINPAL:
                process_zarinpal_payment(payment)
            elif payment.provider == PaymentProvider.CARD:
                process_card_payment(payment)
            elif payment.provider == PaymentProvider.WALLET:
                process_wallet_payment(payment)

            logger.info(f"Processed payment: {payment.id}")
        except Exception as e:
            logger.error(f"Error processing payment {payment.id}: {e}")
            payment.status = PaymentStatus.FAILED
            db.commit()
            send_payment_notification.delay(
                payment_id=payment.id,
                status="failed",
            )
    except Exception as e:
        logger.error(f"Error in process_payment task: {e}")
        raise
    finally:
        db.close()


@shared_task
def verify_payment(payment_id: int, verification_data: Dict) -> None:
    """Verify a payment."""
    db = SessionLocal()
    try:
        payment = db.query(Payment).get(payment_id)
        if not payment:
            logger.error(f"Payment {payment_id} not found")
            return

        # Verify payment based on provider
        try:
            if payment.provider == PaymentProvider.ZARINPAL:
                verify_zarinpal_payment(payment, verification_data)
            elif payment.provider == PaymentProvider.CARD:
                verify_card_payment(payment, verification_data)

            # If payment is verified, update status
            payment.status = PaymentStatus.COMPLETED
            db.commit()

            # Send notification
            send_payment_notification.delay(
                payment_id=payment.id,
                status="completed",
            )

            logger.info(f"Verified payment: {payment.id}")
        except Exception as e:
            logger.error(f"Error verifying payment {payment.id}: {e}")
            payment.status = PaymentStatus.FAILED
            db.commit()
            send_payment_notification.delay(
                payment_id=payment.id,
                status="verification_failed",
            )
    except Exception as e:
        logger.error(f"Error in verify_payment task: {e}")
        raise
    finally:
        db.close()


def process_zarinpal_payment(payment: Payment) -> None:
    """Process Zarinpal payment."""
    try:
        # TODO: Implement Zarinpal payment processing
        # from zarinpal import Zarinpal
        # client = Zarinpal(merchant_id=settings.ZARINPAL_MERCHANT)
        # result = client.payment_request(
        #     amount=payment.amount,
        #     description=payment.description,
        #     callback_url=f"{settings.FRONTEND_URL}/payment/verify",
        # )
        # payment.provider_payment_id = result.authority
        # payment.status = PaymentStatus.PROCESSING
        pass
    except Exception as e:
        logger.error(f"Error processing Zarinpal payment: {e}")
        raise


def verify_zarinpal_payment(payment: Payment, verification_data: Dict) -> None:
    """Verify Zarinpal payment."""
    try:
        # TODO: Implement Zarinpal payment verification
        # from zarinpal import Zarinpal
        # client = Zarinpal(merchant_id=settings.ZARINPAL_MERCHANT)
        # result = client.payment_verification(
        #     amount=payment.amount,
        #     authority=verification_data.get("authority"),
        # )
        # payment.provider_status = result.status
        # payment.provider_message = result.message
        pass
    except Exception as e:
        logger.error(f"Error verifying Zarinpal payment: {e}")
        raise


def process_card_payment(payment: Payment) -> None:
    """Process card-to-card payment."""
    try:
        # Card payments are manually verified
        payment.status = PaymentStatus.PENDING
    except Exception as e:
        logger.error(f"Error processing card payment: {e}")
        raise


def verify_card_payment(payment: Payment, verification_data: Dict) -> None:
    """Verify card-to-card payment."""
    try:
        # Manual verification by admin
        reference_number = verification_data.get("reference_number")
        if not reference_number:
            raise ValueError("Reference number is required")

        payment.reference_number = reference_number
        payment.provider_status = "verified"
    except Exception as e:
        logger.error(f"Error verifying card payment: {e}")
        raise


def process_wallet_payment(payment: Payment) -> None:
    """Process wallet payment."""
    db = SessionLocal()
    try:
        # Check user balance
        if payment.user.wallet_balance < payment.amount:
            raise ValueError("Insufficient wallet balance")

        # Deduct amount from wallet
        payment.user.wallet_balance -= payment.amount
        payment.status = PaymentStatus.COMPLETED
        db.commit()
    except Exception as e:
        logger.error(f"Error processing wallet payment: {e}")
        db.rollback()
        raise
    finally:
        db.close() 