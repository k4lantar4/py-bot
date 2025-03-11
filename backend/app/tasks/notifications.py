"""Notification-related Celery tasks."""

from datetime import datetime, timedelta
from typing import List, Optional

from celery import shared_task
from sqlalchemy.orm import Session

from ..db.session import SessionLocal
from ..models.virtual_account import VirtualAccount, AccountStatus
from ..models.user import User
from ..utils.logger import logger
from ..core.config import settings


@shared_task
def send_expiry_notifications() -> None:
    """Send notifications for accounts expiring soon."""
    db = SessionLocal()
    try:
        # Get accounts expiring in the next 3 days
        today = datetime.utcnow().date()
        expiry_date = (today + timedelta(days=3)).isoformat()
        expiring_accounts = (
            db.query(VirtualAccount)
            .filter(
                VirtualAccount.status == AccountStatus.SOLD,
                VirtualAccount.is_active == True,
                VirtualAccount.expiry_date == expiry_date,
            )
            .all()
        )

        # Send notifications
        for account in expiring_accounts:
            if account.user and account.user.telegram_id:
                send_telegram_notification.delay(
                    user_id=account.user.telegram_id,
                    message=f"Your account {account.name} will expire in 3 days. Please renew it to avoid service interruption.",
                )

        logger.info(f"Sent expiry notifications for {len(expiring_accounts)} accounts")
    except Exception as e:
        logger.error(f"Error sending expiry notifications: {e}")
        raise
    finally:
        db.close()


@shared_task
def send_telegram_notification(user_id: int, message: str) -> None:
    """Send notification via Telegram."""
    try:
        # TODO: Implement Telegram bot API call
        # bot.send_message(chat_id=user_id, text=message)
        logger.info(f"Sent Telegram notification to user {user_id}")
    except Exception as e:
        logger.error(f"Error sending Telegram notification to user {user_id}: {e}")
        raise


@shared_task
def send_bulk_notifications(user_ids: List[int], message: str) -> None:
    """Send bulk notifications via Telegram."""
    for user_id in user_ids:
        send_telegram_notification.delay(user_id=user_id, message=message)


@shared_task
def notify_admin(message: str) -> None:
    """Send notification to admin users."""
    db = SessionLocal()
    try:
        admin_users = db.query(User).filter(User.is_superuser == True).all()
        for admin in admin_users:
            if admin.telegram_id:
                send_telegram_notification.delay(
                    user_id=admin.telegram_id,
                    message=f"[ADMIN] {message}",
                )
    except Exception as e:
        logger.error(f"Error sending admin notification: {e}")
        raise
    finally:
        db.close()


@shared_task
def send_order_notification(order_id: int, status: str) -> None:
    """Send order status notification."""
    db = SessionLocal()
    try:
        from ..models.order import Order

        order = db.query(Order).get(order_id)
        if not order or not order.user or not order.user.telegram_id:
            return

        message = f"Order #{order.order_number} status: {status}"
        send_telegram_notification.delay(
            user_id=order.user.telegram_id,
            message=message,
        )
    except Exception as e:
        logger.error(f"Error sending order notification: {e}")
        raise
    finally:
        db.close()


@shared_task
def send_payment_notification(payment_id: int, status: str) -> None:
    """Send payment status notification."""
    db = SessionLocal()
    try:
        from ..models.payment import Payment

        payment = db.query(Payment).get(payment_id)
        if not payment or not payment.user or not payment.user.telegram_id:
            return

        message = f"Payment #{payment.payment_id} status: {status}"
        if hasattr(payment, "formatted_amount"):
            message += f"\nAmount: {payment.formatted_amount}"

        send_telegram_notification.delay(
            user_id=payment.user.telegram_id,
            message=message,
        )
    except Exception as e:
        logger.error(f"Error sending payment notification: {e}")
        raise
    finally:
        db.close() 