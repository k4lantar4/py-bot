"""
Celery worker for background tasks.

This module sets up the Celery worker for handling background tasks like
server monitoring, session refresh, and email sending.
"""

import logging
import time
from typing import Dict, List, Any, Optional

from celery import Celery
from celery.schedules import crontab
import requests
from requests.exceptions import RequestException
import httpx

from app.core.config import settings
from app.core.redis import (
    get_threexui_session,
    save_threexui_session,
    update_server_status
)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("celery")

# Create Celery app
celery_app = Celery(
    "worker",
    backend=settings.REDIS_URL,
    broker=settings.REDIS_URL
)

# Configure Celery
celery_app.conf.task_routes = {
    "app.worker.test_celery": "main-queue",
    "app.worker.monitor_server": "monitor-queue",
    "app.worker.refresh_threexui_session": "session-queue",
    "app.worker.send_email": "email-queue",
    "app.worker.generate_reports": "report-queue",
    "app.worker.send_bulk_messages": "messaging-queue",
}

# Configure periodic tasks
celery_app.conf.beat_schedule = {
    "monitor-servers-every-5-minutes": {
        "task": "app.worker.monitor_all_servers",
        "schedule": crontab(minute=f"*/{settings.THREEXUI_PING_INTERVAL_MINUTES}"),
    },
    "refresh-sessions-every-hour": {
        "task": "app.worker.refresh_all_sessions",
        "schedule": crontab(minute=0, hour=f"*/{settings.THREEXUI_SESSION_REFRESH_MINUTES // 60}"),
    },
    "generate-daily-reports": {
        "task": "app.worker.generate_daily_reports",
        "schedule": crontab(minute=0, hour=1),  # 1:00 AM every day
    },
}


@celery_app.task(name="app.worker.test_celery")
def test_celery() -> Dict[str, str]:
    """
    Test task to verify Celery is working.
    
    Returns:
        Status message
    """
    return {"status": "ok", "message": "Celery worker is working correctly! 🎉"}


@celery_app.task(name="app.worker.monitor_server")
def monitor_server(server_id: str, server_url: str) -> Dict[str, Any]:
    """
    Monitor a server by pinging it and checking its status.
    
    Args:
        server_id: The ID of the server to monitor
        server_url: The URL of the server
        
    Returns:
        Server status information
    """
    logger.info(f"Monitoring server {server_id} at {server_url} 🔍")
    
    start_time = time.time()
    
    try:
        # Use httpx for async requests with timeout
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.get(f"{server_url}/ping")
        
        response_time = time.time() - start_time
        
        status = {
            "is_online": response.status_code == 200,
            "response_time": response_time,
            "status_code": response.status_code,
            "checked_at": time.time(),
        }
    except Exception as e:
        logger.error(f"Error monitoring server {server_id}: {str(e)} ❌")
        status = {
            "is_online": False,
            "error": str(e),
            "checked_at": time.time(),
        }
    
    # Update server status in Redis
    update_server_status(server_id, status)
    
    return status


@celery_app.task(name="app.worker.monitor_all_servers")
def monitor_all_servers() -> Dict[str, Any]:
    """
    Monitor all servers in the database.
    
    Returns:
        Status results for all servers
    """
    logger.info("Starting monitoring of all servers 🔄")
    
    # This would typically query the database for all servers
    # For demonstration, we're just returning a message
    # In a real implementation, you would:
    # 1. Query all active servers from the database
    # 2. For each server, call monitor_server.delay(server.id, server.url)
    
    return {"status": "ok", "message": "Server monitoring triggered for all servers"}


@celery_app.task(name="app.worker.refresh_threexui_session")
def refresh_threexui_session(server_id: str, server_url: str, username: str, password: str) -> Dict[str, Any]:
    """
    Refresh a 3X-UI panel session.
    
    Args:
        server_id: The ID of the server
        server_url: The URL of the 3X-UI panel
        username: The username for the panel
        password: The password for the panel
        
    Returns:
        Session refresh status
    """
    logger.info(f"Refreshing 3X-UI session for server {server_id} 🔄")
    
    try:
        # Login to 3X-UI panel
        login_data = {
            "username": username,
            "password": password
        }
        
        session = requests.Session()
        response = session.post(f"{server_url}/login", data=login_data, timeout=10)
        
        if response.status_code == 200:
            # Extract cookies and save to Redis
            cookies = session.cookies.get_dict()
            session_data = {
                "cookies": cookies,
                "refreshed_at": time.time(),
                "server_url": server_url
            }
            
            save_threexui_session(server_id, session_data)
            
            logger.info(f"Successfully refreshed 3X-UI session for server {server_id} ✅")
            return {
                "status": "success",
                "message": f"Session refreshed for server {server_id}",
                "server_id": server_id
            }
        else:
            error_msg = f"Failed to refresh 3X-UI session for server {server_id}: HTTP {response.status_code}"
            logger.error(f"{error_msg} ❌")
            return {
                "status": "error",
                "message": error_msg,
                "server_id": server_id
            }
    except RequestException as e:
        error_msg = f"Connection error while refreshing 3X-UI session for server {server_id}: {str(e)}"
        logger.error(f"{error_msg} ❌")
        return {
            "status": "error",
            "message": error_msg,
            "server_id": server_id
        }
    except Exception as e:
        error_msg = f"Unexpected error while refreshing 3X-UI session for server {server_id}: {str(e)}"
        logger.error(f"{error_msg} ❌")
        return {
            "status": "error",
            "message": error_msg,
            "server_id": server_id
        }


@celery_app.task(name="app.worker.refresh_all_sessions")
def refresh_all_sessions() -> Dict[str, Any]:
    """
    Refresh all 3X-UI panel sessions.
    
    Returns:
        Status message
    """
    logger.info("Starting refresh of all 3X-UI sessions 🔄")
    
    # This would typically query the database for all servers
    # For demonstration, we're just returning a message
    # In a real implementation, you would:
    # 1. Query all active servers from the database
    # 2. For each server, call refresh_threexui_session.delay(...)
    
    return {"status": "ok", "message": "Session refresh triggered for all servers"}


@celery_app.task(name="app.worker.send_email")
def send_email(
    email_to: str,
    subject: str,
    template_name: str,
    template_data: Dict[str, Any]
) -> Dict[str, Any]:
    """
    Send an email using a template.
    
    Args:
        email_to: Recipient email
        subject: Email subject
        template_name: Name of the email template
        template_data: Data to render in the template
        
    Returns:
        Email sending status
    """
    logger.info(f"Sending email to {email_to} with subject '{subject}' 📧")
    
    # This is a placeholder for actual email sending logic
    # In a real implementation, you would:
    # 1. Load the email template
    # 2. Render the template with the data
    # 3. Send the email using SMTP
    
    # For demonstration purposes, we'll just log it
    logger.info(f"Would send email to {email_to} using template {template_name} with data: {template_data}")
    
    return {
        "status": "success",
        "email_to": email_to,
        "subject": subject
    }


@celery_app.task(name="app.worker.send_bulk_messages")
def send_bulk_messages(
    user_ids: List[str],
    message: str,
    delivery_channel: str = "email"
) -> Dict[str, Any]:
    """
    Send a message to multiple users.
    
    Args:
        user_ids: List of user IDs to send the message to
        message: The message content
        delivery_channel: The delivery channel (email, telegram, etc.)
        
    Returns:
        Message sending status
    """
    logger.info(f"Sending bulk message to {len(user_ids)} users via {delivery_channel} 📨")
    
    # This is a placeholder for actual message sending logic
    # In a real implementation, you would:
    # 1. Query user details from the database
    # 2. Send the message via the specified channel
    # 3. Track delivery status
    
    # For demonstration purposes, we'll just log it
    logger.info(f"Would send message to {len(user_ids)} users: {message[:50]}...")
    
    return {
        "status": "success",
        "sent_count": len(user_ids),
        "channel": delivery_channel
    }


@celery_app.task(name="app.worker.generate_reports")
def generate_reports(report_type: str, date_range: Dict[str, str]) -> Dict[str, Any]:
    """
    Generate reports for various system aspects.
    
    Args:
        report_type: Type of report to generate
        date_range: Date range for the report
        
    Returns:
        Report generation status
    """
    logger.info(f"Generating {report_type} report for {date_range} 📊")
    
    # This is a placeholder for actual report generation logic
    # In a real implementation, you would:
    # 1. Query data from the database
    # 2. Process the data
    # 3. Generate the report in the desired format
    
    # For demonstration purposes, we'll just log it
    logger.info(f"Would generate {report_type} report for period: {date_range}")
    
    return {
        "status": "success",
        "report_type": report_type,
        "date_range": date_range
    }


@celery_app.task(name="app.worker.generate_daily_reports")
def generate_daily_reports() -> Dict[str, Any]:
    """
    Generate daily reports for the system.
    
    Returns:
        Report generation status
    """
    logger.info("Generating daily reports 📊")
    
    # This would typically call generate_reports with appropriate parameters
    # For demonstration, we're just returning a message
    
    return {"status": "ok", "message": "Daily reports generation triggered"} 