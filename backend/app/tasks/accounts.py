"""Account-related Celery tasks."""

from datetime import datetime, timedelta
from typing import List

from celery import shared_task
from sqlalchemy.orm import Session

from ..db.session import SessionLocal
from ..models.virtual_account import VirtualAccount, AccountStatus
from ..utils.logger import logger


@shared_task
def check_expired_accounts() -> None:
    """Check and update expired accounts."""
    db = SessionLocal()
    try:
        # Get active accounts that have expired
        today = datetime.utcnow().date().isoformat()
        expired_accounts = (
            db.query(VirtualAccount)
            .filter(
                VirtualAccount.status == AccountStatus.SOLD,
                VirtualAccount.is_active == True,
                VirtualAccount.expiry_date <= today,
            )
            .all()
        )

        # Update expired accounts
        for account in expired_accounts:
            account.status = AccountStatus.EXPIRED
            account.is_active = False
            logger.info(f"Account {account.id} has expired")

        db.commit()
        logger.info(f"Updated {len(expired_accounts)} expired accounts")
    except Exception as e:
        logger.error(f"Error checking expired accounts: {e}")
        db.rollback()
        raise
    finally:
        db.close()


@shared_task
def sync_account_usage() -> None:
    """Sync account usage data from server."""
    db = SessionLocal()
    try:
        # Get active accounts
        active_accounts = (
            db.query(VirtualAccount)
            .filter(
                VirtualAccount.status == AccountStatus.SOLD,
                VirtualAccount.is_active == True,
            )
            .all()
        )

        # Update usage data for each account
        for account in active_accounts:
            try:
                # TODO: Implement server API call to get usage data
                # usage_data = get_account_usage(account.server_address, account.username)
                # account.data_used = usage_data.get("data_used", 0)
                # account.last_connection = usage_data.get("last_connection")
                pass
            except Exception as e:
                logger.error(f"Error syncing usage for account {account.id}: {e}")

        db.commit()
        logger.info(f"Synced usage data for {len(active_accounts)} accounts")
    except Exception as e:
        logger.error(f"Error syncing account usage: {e}")
        db.rollback()
        raise
    finally:
        db.close()


@shared_task
def create_account(account_data: dict) -> None:
    """Create a new virtual account on the server."""
    db = SessionLocal()
    try:
        # Create account in database
        account = VirtualAccount(**account_data)
        db.add(account)
        db.commit()

        # TODO: Implement server API call to create account
        # create_server_account(account.server_address, account.username, account.password)

        logger.info(f"Created new account: {account.id}")
    except Exception as e:
        logger.error(f"Error creating account: {e}")
        db.rollback()
        raise
    finally:
        db.close()


@shared_task
def delete_account(account_id: int) -> None:
    """Delete a virtual account from the server."""
    db = SessionLocal()
    try:
        account = db.query(VirtualAccount).get(account_id)
        if not account:
            logger.error(f"Account {account_id} not found")
            return

        # TODO: Implement server API call to delete account
        # delete_server_account(account.server_address, account.username)

        db.delete(account)
        db.commit()
        logger.info(f"Deleted account: {account_id}")
    except Exception as e:
        logger.error(f"Error deleting account: {e}")
        db.rollback()
        raise
    finally:
        db.close() 