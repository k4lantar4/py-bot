"""Ticket-related Celery tasks."""

from datetime import datetime, timedelta
from typing import Optional

from celery import shared_task
from sqlalchemy.orm import Session

from ..db.session import SessionLocal
from ..models.ticket import Ticket, TicketStatus, TicketPriority
from ..models.user import User, UserRole
from ..utils.logger import logger
from .notifications import send_telegram_notification, notify_admin


@shared_task
def process_new_ticket(ticket_id: int) -> None:
    """Process a newly created ticket."""
    db = SessionLocal()
    try:
        ticket = db.query(Ticket).get(ticket_id)
        if not ticket:
            logger.error(f"Ticket {ticket_id} not found")
            return

        try:
            # Set initial status and auto-assign priority
            ticket.status = TicketStatus.OPEN
            if not ticket.priority:
                ticket.priority = auto_assign_priority(ticket)
            
            # Auto-assign to admin if high priority
            if ticket.priority == TicketPriority.HIGH:
                admins = db.query(User).filter(User.role == UserRole.ADMIN).all()
                if admins:
                    ticket.assigned_to = admins[0].id
                    notify_admin.delay(
                        admin_id=admins[0].id,
                        message=f"High priority ticket #{ticket.id} has been assigned to you",
                    )

            db.commit()

            # Notify user
            send_telegram_notification.delay(
                user_id=ticket.user_id,
                message=f"Your ticket #{ticket.id} has been received and is being processed",
            )

            logger.info(f"Processed new ticket: {ticket.id}")
        except Exception as e:
            logger.error(f"Error processing ticket {ticket.id}: {e}")
            ticket.status = TicketStatus.ERROR
            db.commit()
            send_telegram_notification.delay(
                user_id=ticket.user_id,
                message=f"There was an error processing your ticket #{ticket.id}",
            )
    except Exception as e:
        logger.error(f"Error in process_new_ticket task: {e}")
        raise
    finally:
        db.close()


@shared_task
def check_stale_tickets() -> None:
    """Check for stale tickets and send reminders."""
    db = SessionLocal()
    try:
        # Find tickets that haven't been updated in 24 hours
        stale_time = datetime.utcnow() - timedelta(hours=24)
        stale_tickets = (
            db.query(Ticket)
            .filter(
                Ticket.status.in_([TicketStatus.OPEN, TicketStatus.IN_PROGRESS]),
                Ticket.updated_at < stale_time
            )
            .all()
        )

        for ticket in stale_tickets:
            try:
                # Notify assigned admin if any
                if ticket.assigned_to:
                    notify_admin.delay(
                        admin_id=ticket.assigned_to,
                        message=f"Reminder: Ticket #{ticket.id} has been waiting for a response for over 24 hours",
                    )
                else:
                    # Notify all admins if unassigned
                    admins = db.query(User).filter(User.role == UserRole.ADMIN).all()
                    for admin in admins:
                        notify_admin.delay(
                            admin_id=admin.id,
                            message=f"Unassigned ticket #{ticket.id} has been waiting for over 24 hours",
                        )

                logger.info(f"Sent reminder for stale ticket: {ticket.id}")
            except Exception as e:
                logger.error(f"Error sending reminder for ticket {ticket.id}: {e}")

        logger.info(f"Checked {len(stale_tickets)} stale tickets")
    except Exception as e:
        logger.error(f"Error in check_stale_tickets task: {e}")
        raise
    finally:
        db.close()


@shared_task
def auto_close_resolved_tickets() -> None:
    """Automatically close tickets that have been resolved for a while."""
    db = SessionLocal()
    try:
        # Find tickets that have been resolved for more than 72 hours
        close_time = datetime.utcnow() - timedelta(hours=72)
        resolved_tickets = (
            db.query(Ticket)
            .filter(
                Ticket.status == TicketStatus.RESOLVED,
                Ticket.updated_at < close_time
            )
            .all()
        )

        for ticket in resolved_tickets:
            try:
                ticket.status = TicketStatus.CLOSED
                ticket.closed_at = datetime.utcnow()
                db.commit()

                # Notify user
                send_telegram_notification.delay(
                    user_id=ticket.user_id,
                    message=f"Your ticket #{ticket.id} has been automatically closed as it was resolved 72 hours ago",
                )

                logger.info(f"Auto-closed resolved ticket: {ticket.id}")
            except Exception as e:
                logger.error(f"Error auto-closing ticket {ticket.id}: {e}")
                continue

        logger.info(f"Auto-closed {len(resolved_tickets)} resolved tickets")
    except Exception as e:
        logger.error(f"Error in auto_close_resolved_tickets task: {e}")
        raise
    finally:
        db.close()


def auto_assign_priority(ticket: Ticket) -> TicketPriority:
    """Auto-assign priority based on ticket content and user status."""
    # Check for urgent keywords in title or content
    urgent_keywords = ["urgent", "emergency", "critical", "broken", "error", "failed"]
    content = f"{ticket.title} {ticket.content}".lower()
    
    if any(keyword in content for keyword in urgent_keywords):
        return TicketPriority.HIGH
    
    # Check user's status and history
    if ticket.user.role in [UserRole.ADMIN, UserRole.STAFF]:
        return TicketPriority.HIGH
    
    # Check if user has active orders or recent payments
    if any(order.status == "ACTIVE" for order in ticket.user.orders):
        return TicketPriority.MEDIUM
    
    return TicketPriority.LOW 