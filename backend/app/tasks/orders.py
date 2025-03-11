"""Order-related Celery tasks."""

from datetime import datetime, timedelta
from typing import List, Optional

from celery import shared_task
from sqlalchemy.orm import Session

from ..db.session import SessionLocal
from ..models.order import Order, OrderStatus
from ..models.payment import Payment, PaymentStatus
from ..models.virtual_account import VirtualAccount, AccountStatus
from ..utils.logger import logger
from .notifications import send_order_notification


@shared_task
def process_pending_orders() -> None:
    """Process pending orders."""
    db = SessionLocal()
    try:
        # Get pending orders with completed payments
        pending_orders = (
            db.query(Order)
            .join(Payment)
            .filter(
                Order.status == OrderStatus.PENDING,
                Payment.status == PaymentStatus.COMPLETED,
            )
            .all()
        )

        # Process each order
        for order in pending_orders:
            try:
                # Update order status
                order.status = OrderStatus.PROCESSING
                db.commit()

                # Process order accounts
                for account in order.accounts:
                    account.status = AccountStatus.SOLD
                    account.user_id = order.user_id

                # Mark order as completed
                order.status = OrderStatus.COMPLETED
                db.commit()

                # Send notification
                send_order_notification.delay(
                    order_id=order.id,
                    status="completed",
                )

                logger.info(f"Processed order: {order.id}")
            except Exception as e:
                logger.error(f"Error processing order {order.id}: {e}")
                order.status = OrderStatus.FAILED
                db.commit()
                send_order_notification.delay(
                    order_id=order.id,
                    status="failed",
                )

        logger.info(f"Processed {len(pending_orders)} pending orders")
    except Exception as e:
        logger.error(f"Error processing pending orders: {e}")
        raise
    finally:
        db.close()


@shared_task
def cancel_expired_orders() -> None:
    """Cancel expired unpaid orders."""
    db = SessionLocal()
    try:
        # Get expired unpaid orders (older than 1 hour)
        expiry_time = datetime.utcnow() - timedelta(hours=1)
        expired_orders = (
            db.query(Order)
            .filter(
                Order.status == OrderStatus.PENDING,
                Order.created_at <= expiry_time,
            )
            .all()
        )

        # Cancel each order
        for order in expired_orders:
            try:
                # Release reserved accounts
                for account in order.accounts:
                    account.status = AccountStatus.AVAILABLE
                    account.user_id = None

                # Mark order as cancelled
                order.status = OrderStatus.CANCELLED
                db.commit()

                # Send notification
                send_order_notification.delay(
                    order_id=order.id,
                    status="cancelled",
                )

                logger.info(f"Cancelled expired order: {order.id}")
            except Exception as e:
                logger.error(f"Error cancelling order {order.id}: {e}")

        logger.info(f"Cancelled {len(expired_orders)} expired orders")
    except Exception as e:
        logger.error(f"Error cancelling expired orders: {e}")
        raise
    finally:
        db.close()


@shared_task
def process_refund(order_id: int) -> None:
    """Process order refund."""
    db = SessionLocal()
    try:
        order = db.query(Order).get(order_id)
        if not order or not order.payment:
            logger.error(f"Order {order_id} not found or has no payment")
            return

        # Process refund
        try:
            # TODO: Implement refund logic based on payment provider
            # if order.payment.provider == PaymentProvider.ZARINPAL:
            #     process_zarinpal_refund(order.payment)
            # elif order.payment.provider == PaymentProvider.CARD:
            #     process_card_refund(order.payment)

            # Update order and payment status
            order.status = OrderStatus.REFUNDED
            order.payment.status = PaymentStatus.REFUNDED
            db.commit()

            # Release accounts
            for account in order.accounts:
                account.status = AccountStatus.AVAILABLE
                account.user_id = None
            db.commit()

            # Send notification
            send_order_notification.delay(
                order_id=order.id,
                status="refunded",
            )

            logger.info(f"Processed refund for order: {order.id}")
        except Exception as e:
            logger.error(f"Error processing refund for order {order.id}: {e}")
            order.status = OrderStatus.FAILED
            db.commit()
            send_order_notification.delay(
                order_id=order.id,
                status="refund_failed",
            )
    except Exception as e:
        logger.error(f"Error processing refund: {e}")
        raise
    finally:
        db.close() 