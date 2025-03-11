"""Wallet-related Celery tasks."""

from datetime import datetime
from decimal import Decimal
from typing import Optional

from celery import shared_task
from sqlalchemy.orm import Session

from ..db.session import SessionLocal
from ..models.user import User
from ..models.wallet import WalletTransaction, TransactionType, TransactionStatus
from ..utils.logger import logger
from .notifications import send_telegram_notification


@shared_task
def process_wallet_deposit(transaction_id: int) -> None:
    """Process a wallet deposit transaction."""
    db = SessionLocal()
    try:
        transaction = db.query(WalletTransaction).get(transaction_id)
        if not transaction:
            logger.error(f"Transaction {transaction_id} not found")
            return

        if transaction.type != TransactionType.DEPOSIT:
            logger.error(f"Transaction {transaction_id} is not a deposit")
            return

        try:
            # Update user's wallet balance
            transaction.user.wallet_balance += transaction.amount
            transaction.status = TransactionStatus.COMPLETED
            transaction.completed_at = datetime.utcnow()
            db.commit()

            # Send notification
            send_telegram_notification.delay(
                user_id=transaction.user_id,
                message=f"Your wallet has been credited with {transaction.amount:,.0f} Toman",
            )

            logger.info(f"Processed wallet deposit: {transaction.id}")
        except Exception as e:
            logger.error(f"Error processing wallet deposit {transaction.id}: {e}")
            transaction.status = TransactionStatus.FAILED
            db.commit()
            send_telegram_notification.delay(
                user_id=transaction.user_id,
                message="Failed to process your wallet deposit",
            )
    except Exception as e:
        logger.error(f"Error in process_wallet_deposit task: {e}")
        raise
    finally:
        db.close()


@shared_task
def process_wallet_withdrawal(transaction_id: int) -> None:
    """Process a wallet withdrawal transaction."""
    db = SessionLocal()
    try:
        transaction = db.query(WalletTransaction).get(transaction_id)
        if not transaction:
            logger.error(f"Transaction {transaction_id} not found")
            return

        if transaction.type != TransactionType.WITHDRAWAL:
            logger.error(f"Transaction {transaction_id} is not a withdrawal")
            return

        try:
            # Check if user has sufficient balance
            if transaction.user.wallet_balance < transaction.amount:
                raise ValueError("Insufficient wallet balance")

            # Update user's wallet balance
            transaction.user.wallet_balance -= transaction.amount
            transaction.status = TransactionStatus.COMPLETED
            transaction.completed_at = datetime.utcnow()
            db.commit()

            # Send notification
            send_telegram_notification.delay(
                user_id=transaction.user_id,
                message=f"Your withdrawal of {transaction.amount:,.0f} Toman has been processed",
            )

            logger.info(f"Processed wallet withdrawal: {transaction.id}")
        except ValueError as e:
            logger.error(f"Insufficient balance for withdrawal {transaction.id}: {e}")
            transaction.status = TransactionStatus.FAILED
            transaction.failure_reason = str(e)
            db.commit()
            send_telegram_notification.delay(
                user_id=transaction.user_id,
                message="Insufficient balance for withdrawal",
            )
        except Exception as e:
            logger.error(f"Error processing wallet withdrawal {transaction.id}: {e}")
            transaction.status = TransactionStatus.FAILED
            transaction.failure_reason = str(e)
            db.commit()
            send_telegram_notification.delay(
                user_id=transaction.user_id,
                message="Failed to process your withdrawal",
            )
    except Exception as e:
        logger.error(f"Error in process_wallet_withdrawal task: {e}")
        raise
    finally:
        db.close()


@shared_task
def check_pending_transactions() -> None:
    """Check and update status of pending wallet transactions."""
    db = SessionLocal()
    try:
        pending_transactions = (
            db.query(WalletTransaction)
            .filter(WalletTransaction.status == TransactionStatus.PENDING)
            .all()
        )

        for transaction in pending_transactions:
            try:
                if transaction.type == TransactionType.DEPOSIT:
                    process_wallet_deposit.delay(transaction.id)
                elif transaction.type == TransactionType.WITHDRAWAL:
                    process_wallet_withdrawal.delay(transaction.id)
            except Exception as e:
                logger.error(f"Error processing transaction {transaction.id}: {e}")

        logger.info(f"Checked {len(pending_transactions)} pending transactions")
    except Exception as e:
        logger.error(f"Error in check_pending_transactions task: {e}")
        raise
    finally:
        db.close()


@shared_task
def sync_wallet_balances() -> None:
    """Sync wallet balances with transaction history."""
    db = SessionLocal()
    try:
        users = db.query(User).all()
        for user in users:
            try:
                # Calculate balance from completed transactions
                deposits = sum(
                    t.amount
                    for t in user.wallet_transactions
                    if t.type == TransactionType.DEPOSIT
                    and t.status == TransactionStatus.COMPLETED
                )
                withdrawals = sum(
                    t.amount
                    for t in user.wallet_transactions
                    if t.type == TransactionType.WITHDRAWAL
                    and t.status == TransactionStatus.COMPLETED
                )
                
                calculated_balance = deposits - withdrawals
                
                # Update if there's a discrepancy
                if user.wallet_balance != calculated_balance:
                    logger.warning(
                        f"Balance mismatch for user {user.id}: "
                        f"stored={user.wallet_balance}, calculated={calculated_balance}"
                    )
                    user.wallet_balance = calculated_balance
                    db.commit()
                    
                    # Notify user of balance adjustment
                    send_telegram_notification.delay(
                        user_id=user.id,
                        message="Your wallet balance has been adjusted based on transaction history",
                    )
            except Exception as e:
                logger.error(f"Error syncing balance for user {user.id}: {e}")
                continue

        logger.info(f"Synced wallet balances for {len(users)} users")
    except Exception as e:
        logger.error(f"Error in sync_wallet_balances task: {e}")
        raise
    finally:
        db.close() 