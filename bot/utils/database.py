"""
Database utilities for the Telegram bot.

This module provides functions for interacting with the SQLite database for
account management, orders, payments, and other related data.
"""

import os
import sqlite3
import json
import logging
from datetime import datetime
from typing import Dict, List, Any, Optional, Tuple

# Configure logging
logger = logging.getLogger("telegram_bot")

# Database file path
DB_FILE = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data", "bot.db")

# Ensure data directory exists
os.makedirs(os.path.dirname(DB_FILE), exist_ok=True)


def setup_database() -> None:
    """Set up the database by creating tables if they don't exist."""
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    
    # Create users table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY,
        username TEXT,
        first_name TEXT,
        last_name TEXT,
        language_code TEXT DEFAULT 'en',
        is_admin BOOLEAN DEFAULT 0,
        balance INTEGER DEFAULT 0,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    ''')
    
    # Create accounts table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS accounts (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        service_id INTEGER,
        server_id INTEGER,
        name TEXT,
        config TEXT,
        status TEXT DEFAULT 'active',
        expiry_date TIMESTAMP,
        traffic_limit INTEGER,
        traffic_used INTEGER DEFAULT 0,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (user_id) REFERENCES users (id)
    )
    ''')
    
    # Create orders table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS orders (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        service_id INTEGER,
        amount INTEGER,
        status TEXT DEFAULT 'pending',
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (user_id) REFERENCES users (id)
    )
    ''')
    
    # Create payments table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS payments (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        order_id INTEGER,
        user_id INTEGER,
        amount INTEGER,
        payment_method TEXT,
        status TEXT DEFAULT 'pending',
        transaction_id TEXT,
        details TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (order_id) REFERENCES orders (id),
        FOREIGN KEY (user_id) REFERENCES users (id)
    )
    ''')
    
    # Create tickets table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS tickets (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        subject TEXT,
        status TEXT DEFAULT 'open',
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (user_id) REFERENCES users (id)
    )
    ''')
    
    # Create ticket_messages table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS ticket_messages (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        ticket_id INTEGER,
        user_id INTEGER,
        message TEXT,
        is_from_admin BOOLEAN DEFAULT 0,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (ticket_id) REFERENCES tickets (id),
        FOREIGN KEY (user_id) REFERENCES users (id)
    )
    ''')
    
    # Create settings table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS settings (
        key TEXT PRIMARY KEY,
        value TEXT,
        description TEXT
    )
    ''')
    
    # Insert default settings if they don't exist
    default_settings = [
        ('card_payment_details', json.dumps({
            'card_number': '',
            'card_holder': ''
        }), 'Card payment details'),
        ('zarinpal_payment_details', json.dumps({
            'merchant_id': ''
        }), 'Zarinpal payment details'),
        ('admin_user_ids', json.dumps([]), 'Admin user IDs'),
        ('zarinpal_merchant', '', 'ZarinPal merchant ID'),
        ('card_number', '', 'Card number for card-to-card payments'),
        ('card_holder', '', 'Card holder name for card-to-card payments'),
    ]
    
    for key, value, description in default_settings:
        cursor.execute('INSERT OR IGNORE INTO settings (key, value, description) VALUES (?, ?, ?)',
                      (key, value, description))
    
    conn.commit()
    conn.close()
    
    logger.info("Database setup complete")


# User functions

def create_user_if_not_exists(user_id: int, username: Optional[str], first_name: str,
                             last_name: Optional[str], language_code: str) -> None:
    """
    Create a user if they don't exist in the database.
    
    Args:
        user_id: Telegram user ID
        username: Telegram username
        first_name: User's first name
        last_name: User's last name
        language_code: User's language code
    """
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    
    try:
        # Check if user exists
        cursor.execute('SELECT id FROM users WHERE id = ?', (user_id,))
        user = cursor.fetchone()
        
        if not user:
            # Create user
            cursor.execute(
                'INSERT INTO users (id, username, first_name, last_name, language_code) VALUES (?, ?, ?, ?, ?)',
                (user_id, username, first_name, last_name, language_code)
            )
            conn.commit()
            logger.info(f"Created new user: {user_id} ({username})")
        else:
            # Update user information
            cursor.execute(
                'UPDATE users SET username = ?, first_name = ?, last_name = ?, updated_at = CURRENT_TIMESTAMP WHERE id = ?',
                (username, first_name, last_name, user_id)
            )
            conn.commit()
    except Exception as e:
        logger.error(f"Error creating/updating user: {e}")
        conn.rollback()
    finally:
        conn.close()


def get_user(user_id: int) -> Optional[Dict[str, Any]]:
    """
    Get user information.
    
    Args:
        user_id: Telegram user ID
        
    Returns:
        User data as dictionary or None if not found
    """
    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    try:
        cursor.execute('SELECT * FROM users WHERE id = ?', (user_id,))
        user = cursor.fetchone()
        
        if user:
            return dict(user)
        return None
    except Exception as e:
        logger.error(f"Error getting user: {e}")
        return None
    finally:
        conn.close()


def get_user_language(user_id: int) -> str:
    """
    Get user's language preference.
    
    Args:
        user_id: Telegram user ID
        
    Returns:
        Language code (default: 'en')
    """
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    
    try:
        cursor.execute('SELECT language_code FROM users WHERE id = ?', (user_id,))
        result = cursor.fetchone()
        
        if result and result[0]:
            return result[0]
        return 'en'
    except Exception as e:
        logger.error(f"Error getting user language: {e}")
        return 'en'
    finally:
        conn.close()


def update_user_language(user_id: int, language_code: str) -> bool:
    """
    Update user's language preference.
    
    Args:
        user_id: Telegram user ID
        language_code: Language code
        
    Returns:
        True if successful, False otherwise
    """
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    
    try:
        cursor.execute(
            'UPDATE users SET language_code = ?, updated_at = CURRENT_TIMESTAMP WHERE id = ?',
            (language_code, user_id)
        )
        conn.commit()
        return True
    except Exception as e:
        logger.error(f"Error updating user language: {e}")
        conn.rollback()
        return False
    finally:
        conn.close()


# Settings functions

def get_setting(key: str) -> Optional[str]:
    """
    Get a setting value.
    
    Args:
        key: Setting key
        
    Returns:
        Setting value or None if not found
    """
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    
    try:
        cursor.execute('SELECT value FROM settings WHERE key = ?', (key,))
        result = cursor.fetchone()
        
        if result:
            return result[0]
        return None
    except Exception as e:
        logger.error(f"Error getting setting: {e}")
        return None
    finally:
        conn.close()


def update_setting(key: str, value: str) -> bool:
    """
    Update a setting value.
    
    Args:
        key: Setting key
        value: Setting value
        
    Returns:
        True if successful, False otherwise
    """
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    
    try:
        cursor.execute('UPDATE settings SET value = ? WHERE key = ?', (value, key))
        conn.commit()
        return True
    except Exception as e:
        logger.error(f"Error updating setting: {e}")
        conn.rollback()
        return False
    finally:
        conn.close()


# Order and payment functions

def create_order(user_id: int, service_id: int, amount: int) -> Optional[Dict[str, Any]]:
    """
    Create a new order.
    
    Args:
        user_id: Telegram user ID
        service_id: Service ID
        amount: Order amount
        
    Returns:
        Order data as dictionary or None if failed
    """
    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    try:
        # Create order
        cursor.execute(
            'INSERT INTO orders (user_id, service_id, amount) VALUES (?, ?, ?)',
            (user_id, service_id, amount)
        )
        conn.commit()
        
        order_id = cursor.lastrowid
        
        # Get created order
        cursor.execute('SELECT * FROM orders WHERE id = ?', (order_id,))
        order = cursor.fetchone()
        
        if order:
            return dict(order)
        return None
    except Exception as e:
        logger.error(f"Error creating order: {e}")
        conn.rollback()
        return None
    finally:
        conn.close()


def create_payment(order_id: int, user_id: int, amount: int, payment_method: str, details: Optional[str] = None) -> Optional[Dict]:
    """
    Create a new payment.
    
    Args:
        order_id: Order ID
        user_id: Telegram user ID
        amount: Payment amount
        payment_method: Payment method (e.g., 'card', 'zarinpal', 'wallet')
        details: Optional payment details
        
    Returns:
        Payment data as dictionary or None if failed
    """
    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    try:
        current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
        # Create payment
        cursor.execute(
            'INSERT INTO payments (order_id, user_id, amount, payment_method, status, details, created_at, updated_at) VALUES (?, ?, ?, ?, ?, ?, ?, ?)',
            (order_id, user_id, amount, payment_method, 'pending', details, current_time, current_time)
        )
        conn.commit()
        
        payment_id = cursor.lastrowid
        
        # Get created payment
        cursor.execute('SELECT * FROM payments WHERE id = ?', (payment_id,))
        payment = cursor.fetchone()
        
        if payment:
            return dict(payment)
        return None
    except Exception as e:
        logger.error(f"Error creating payment: {e}")
        conn.rollback()
        return None
    finally:
        conn.close()


def update_payment_status(payment_id: int, status: str, transaction_id: Optional[str] = None, details: Optional[str] = None) -> bool:
    """
    Update payment status.
    
    Args:
        payment_id: Payment ID
        status: Payment status ('pending', 'completed', 'failed')
        transaction_id: Optional transaction ID
        details: Optional payment details
        
    Returns:
        True if successful, False otherwise
    """
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    
    try:
        current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
        # Update payment
        if transaction_id and details:
            cursor.execute(
                'UPDATE payments SET status = ?, transaction_id = ?, details = ?, updated_at = ? WHERE id = ?',
                (status, transaction_id, details, current_time, payment_id)
            )
        elif transaction_id:
            cursor.execute(
                'UPDATE payments SET status = ?, transaction_id = ?, updated_at = ? WHERE id = ?',
                (status, transaction_id, current_time, payment_id)
            )
        elif details:
            cursor.execute(
                'UPDATE payments SET status = ?, details = ?, updated_at = ? WHERE id = ?',
                (status, details, current_time, payment_id)
            )
        else:
            cursor.execute(
                'UPDATE payments SET status = ?, updated_at = ? WHERE id = ?',
                (status, current_time, payment_id)
            )
        
        conn.commit()
        
        # If payment is completed, update order status
        if status == 'completed':
            cursor.execute('SELECT order_id FROM payments WHERE id = ?', (payment_id,))
            result = cursor.fetchone()
            
            if result:
                order_id = result[0]
                cursor.execute(
                    'UPDATE orders SET status = ?, updated_at = ? WHERE id = ?',
                    ('completed', current_time, order_id)
                )
                conn.commit()
        
        return True
    except Exception as e:
        logger.error(f"Error updating payment status: {e}")
        conn.rollback()
        return False
    finally:
        conn.close()


# Account functions

def create_account(user_id: int, service_id: int, server_id: int, name: str, config: str,
                  expiry_date: str, traffic_limit: int) -> Optional[Dict[str, Any]]:
    """
    Create a new account.
    
    Args:
        user_id: Telegram user ID
        service_id: Service ID
        server_id: Server ID
        name: Account name
        config: Account configuration
        expiry_date: Account expiry date (YYYY-MM-DD HH:MM:SS)
        traffic_limit: Traffic limit in bytes
        
    Returns:
        Account data as dictionary or None if failed
    """
    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    try:
        current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
        # Create account
        cursor.execute(
            'INSERT INTO accounts (user_id, service_id, server_id, name, config, expiry_date, traffic_limit, created_at, updated_at) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)',
            (user_id, service_id, server_id, name, config, expiry_date, traffic_limit, current_time, current_time)
        )
        conn.commit()
        
        account_id = cursor.lastrowid
        
        # Get created account
        cursor.execute('SELECT * FROM accounts WHERE id = ?', (account_id,))
        account = cursor.fetchone()
        
        if account:
            return dict(account)
        return None
    except Exception as e:
        logger.error(f"Error creating account: {e}")
        conn.rollback()
        return None
    finally:
        conn.close()


def get_account(account_id: int) -> Optional[Dict[str, Any]]:
    """
    Get account information.
    
    Args:
        account_id: Account ID
        
    Returns:
        Account data as dictionary or None if not found
    """
    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    try:
        cursor.execute('SELECT * FROM accounts WHERE id = ?', (account_id,))
        account = cursor.fetchone()
        
        if account:
            return dict(account)
        return None
    except Exception as e:
        logger.error(f"Error getting account: {e}")
        return None
    finally:
        conn.close()


def get_user_accounts(user_id: int) -> List[Dict[str, Any]]:
    """
    Get all accounts for a user.
    
    Args:
        user_id: Telegram user ID
        
    Returns:
        List of account data dictionaries
    """
    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    try:
        cursor.execute('SELECT * FROM accounts WHERE user_id = ? ORDER BY created_at DESC', (user_id,))
        accounts = cursor.fetchall()
        
        return [dict(account) for account in accounts]
    except Exception as e:
        logger.error(f"Error getting user accounts: {e}")
        return []
    finally:
        conn.close()


def update_account_status(account_id: int, status: str) -> bool:
    """
    Update account status.
    
    Args:
        account_id: Account ID
        status: Account status ('active', 'expired', 'suspended')
        
    Returns:
        True if successful, False otherwise
    """
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    
    try:
        current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
        cursor.execute(
            'UPDATE accounts SET status = ?, updated_at = ? WHERE id = ?',
            (status, current_time, account_id)
        )
        conn.commit()
        return True
    except Exception as e:
        logger.error(f"Error updating account status: {e}")
        conn.rollback()
        return False
    finally:
        conn.close()


def update_account_traffic(account_id: int, traffic_used: int) -> bool:
    """
    Update account traffic usage.
    
    Args:
        account_id: Account ID
        traffic_used: Traffic used in bytes
        
    Returns:
        True if successful, False otherwise
    """
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    
    try:
        current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
        cursor.execute(
            'UPDATE accounts SET traffic_used = ?, updated_at = ? WHERE id = ?',
            (traffic_used, current_time, account_id)
        )
        conn.commit()
        return True
    except Exception as e:
        logger.error(f"Error updating account traffic: {e}")
        conn.rollback()
        return False
    finally:
        conn.close()


# Support ticket functions

def create_ticket(user_id: int, subject: str) -> Optional[Dict[str, Any]]:
    """
    Create a new support ticket.
    
    Args:
        user_id: Telegram user ID
        subject: Ticket subject
        
    Returns:
        Ticket data as dictionary or None if failed
    """
    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    try:
        current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
        # Create ticket
        cursor.execute(
            'INSERT INTO tickets (user_id, subject, created_at, updated_at) VALUES (?, ?, ?, ?)',
            (user_id, subject, current_time, current_time)
        )
        conn.commit()
        
        ticket_id = cursor.lastrowid
        
        # Get created ticket
        cursor.execute('SELECT * FROM tickets WHERE id = ?', (ticket_id,))
        ticket = cursor.fetchone()
        
        if ticket:
            return dict(ticket)
        return None
    except Exception as e:
        logger.error(f"Error creating ticket: {e}")
        conn.rollback()
        return None
    finally:
        conn.close()


def add_ticket_message(ticket_id: int, user_id: int, message: str, is_from_admin: bool = False) -> Optional[Dict[str, Any]]:
    """
    Add a message to a support ticket.
    
    Args:
        ticket_id: Ticket ID
        user_id: Telegram user ID
        message: Message text
        is_from_admin: Whether the message is from an admin
        
    Returns:
        Message data as dictionary or None if failed
    """
    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    try:
        current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
        # Add message
        cursor.execute(
            'INSERT INTO ticket_messages (ticket_id, user_id, message, is_from_admin, created_at) VALUES (?, ?, ?, ?, ?)',
            (ticket_id, user_id, message, 1 if is_from_admin else 0, current_time)
        )
        
        # Update ticket updated_at
        cursor.execute(
            'UPDATE tickets SET updated_at = ? WHERE id = ?',
            (current_time, ticket_id)
        )
        
        conn.commit()
        
        message_id = cursor.lastrowid
        
        # Get created message
        cursor.execute('SELECT * FROM ticket_messages WHERE id = ?', (message_id,))
        message = cursor.fetchone()
        
        if message:
            return dict(message)
        return None
    except Exception as e:
        logger.error(f"Error adding ticket message: {e}")
        conn.rollback()
        return None
    finally:
        conn.close()


def get_user_tickets(user_id: int) -> List[Dict[str, Any]]:
    """
    Get all tickets for a user.
    
    Args:
        user_id: Telegram user ID
        
    Returns:
        List of ticket data dictionaries
    """
    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    try:
        cursor.execute('SELECT * FROM tickets WHERE user_id = ? ORDER BY updated_at DESC', (user_id,))
        tickets = cursor.fetchall()
        
        return [dict(ticket) for ticket in tickets]
    except Exception as e:
        logger.error(f"Error getting user tickets: {e}")
        return []
    finally:
        conn.close()


def get_ticket_messages(ticket_id: int) -> List[Dict[str, Any]]:
    """
    Get all messages for a ticket.
    
    Args:
        ticket_id: Ticket ID
        
    Returns:
        List of message data dictionaries
    """
    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    try:
        cursor.execute('SELECT * FROM ticket_messages WHERE ticket_id = ? ORDER BY created_at ASC', (ticket_id,))
        messages = cursor.fetchall()
        
        return [dict(message) for message in messages]
    except Exception as e:
        logger.error(f"Error getting ticket messages: {e}")
        return []
    finally:
        conn.close()


def update_ticket_status(ticket_id: int, status: str) -> bool:
    """
    Update ticket status.
    
    Args:
        ticket_id: Ticket ID
        status: Ticket status ('open', 'closed')
        
    Returns:
        True if successful, False otherwise
    """
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    
    try:
        current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
        cursor.execute(
            'UPDATE tickets SET status = ?, updated_at = ? WHERE id = ?',
            (status, current_time, ticket_id)
        )
        conn.commit()
        return True
    except Exception as e:
        logger.error(f"Error updating ticket status: {e}")
        conn.rollback()
        return False
    finally:
        conn.close() 