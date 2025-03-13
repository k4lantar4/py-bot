"""
Database utilities for the Telegram bot.

This module provides functions for interacting with the PostgreSQL database for
account management, orders, payments, and other related data.
"""

import os
import json
import logging
from datetime import datetime
from typing import Dict, List, Any, Optional, Tuple
import psycopg2
from psycopg2.extras import DictCursor
from psycopg2.pool import SimpleConnectionPool
import uuid

# Configure logging
logger = logging.getLogger("telegram_bot")

# Database configuration
DB_CONFIG = {
    "dbname": os.getenv("DB_NAME", "v2ray_bot"),
    "user": os.getenv("DB_USER", "postgres"),
    "password": os.getenv("DB_PASSWORD", ""),
    "host": os.getenv("DB_HOST", "localhost"),
    "port": os.getenv("DB_PORT", "5432"),
    "minconn": 1,
    "maxconn": 10
}

# Create connection pool
pool = None

def setup_database() -> None:
    """Set up the database by creating tables if they don't exist."""
    global pool
    
    conn = None
    cursor = None
    
    try:
        # Create connection pool
        pool = SimpleConnectionPool(**DB_CONFIG)
        conn = pool.getconn()
        cursor = conn.cursor()
        
        # Create users table
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id BIGINT PRIMARY KEY,
            username TEXT,
            first_name TEXT,
            last_name TEXT,
            language_code TEXT DEFAULT 'en',
            is_admin BOOLEAN DEFAULT FALSE,
            balance INTEGER DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        ''')
        
        # Create user_preferences table
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS user_preferences (
            user_id BIGINT PRIMARY KEY,
            preferences JSONB DEFAULT '{}',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users (id)
        )
        ''')
        
        # Create accounts table
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS accounts (
            id SERIAL PRIMARY KEY,
            user_id BIGINT,
            service_id INTEGER,
            server_id INTEGER,
            name TEXT,
            config JSONB,
            status TEXT DEFAULT 'active',
            expiry_date TIMESTAMP,
            traffic_limit BIGINT,
            traffic_used BIGINT DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users (id)
        )
        ''')
        
        # Create orders table
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS orders (
            id SERIAL PRIMARY KEY,
            user_id BIGINT,
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
            id SERIAL PRIMARY KEY,
            order_id INTEGER,
            user_id BIGINT,
            amount INTEGER,
            payment_method TEXT,
            status TEXT DEFAULT 'pending',
            transaction_id TEXT,
            details JSONB,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (order_id) REFERENCES orders (id),
            FOREIGN KEY (user_id) REFERENCES users (id)
        )
        ''')
        
        # Create tickets table
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS tickets (
            id SERIAL PRIMARY KEY,
            user_id BIGINT,
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
            id SERIAL PRIMARY KEY,
            ticket_id INTEGER,
            user_id BIGINT,
            message TEXT,
            is_from_admin BOOLEAN DEFAULT FALSE,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (ticket_id) REFERENCES tickets (id),
            FOREIGN KEY (user_id) REFERENCES users (id)
        )
        ''')
        
        # Create settings table
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS settings (
            key TEXT PRIMARY KEY,
            value JSONB,
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
            ('zarinpal_merchant', json.dumps(''), 'ZarinPal merchant ID'),
            ('card_number', json.dumps(''), 'Card number for card-to-card payments'),
            ('card_holder', json.dumps(''), 'Card holder name for card-to-card payments'),
        ]
        
        for key, value, description in default_settings:
            cursor.execute(
                'INSERT INTO settings (key, value, description) VALUES (%s, %s, %s) ON CONFLICT (key) DO NOTHING',
                (key, value, description)
            )
        
        conn.commit()
        logger.info("Database setup complete")
        
    except Exception as e:
        logger.error(f"Error setting up database: {e}")
        if conn:
            conn.rollback()
        raise
    finally:
        if cursor:
            cursor.close()
        if conn:
            pool.putconn(conn)

def get_db_connection():
    """Get a database connection from the pool."""
    if not pool:
        setup_database()
    return pool.getconn()

def release_db_connection(conn):
    """Release a database connection back to the pool."""
    if conn and pool:
        pool.putconn(conn)

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
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        # Check if user exists
        cursor.execute('SELECT id FROM users WHERE id = %s', (user_id,))
        user = cursor.fetchone()
        
        if not user:
            # Create user
            cursor.execute(
                'INSERT INTO users (id, username, first_name, last_name, language_code) VALUES (%s, %s, %s, %s, %s)',
                (user_id, username, first_name, last_name, language_code)
            )
            conn.commit()
            logger.info(f"Created new user: {user_id} ({username})")
        else:
            # Update user information
            cursor.execute(
                'UPDATE users SET username = %s, first_name = %s, last_name = %s, updated_at = CURRENT_TIMESTAMP WHERE id = %s',
                (username, first_name, last_name, user_id)
            )
            conn.commit()
    except Exception as e:
        logger.error(f"Error creating/updating user: {e}")
        conn.rollback()
    finally:
        cursor.close()
        release_db_connection(conn)


def get_user(user_id: int) -> Optional[Dict[str, Any]]:
    """
    Get user information from the database.
    
    Args:
        user_id: Telegram user ID
        
    Returns:
        User information as a dictionary or None if not found
    """
    conn = get_db_connection()
    cursor = conn.cursor(cursor_factory=DictCursor)
    
    try:
        cursor.execute('''
        SELECT * FROM users WHERE id = %s
        ''', (user_id,))
        
        user = cursor.fetchone()
        if user:
            return dict(user)
        return None
    except Exception as e:
        logger.error(f"Error getting user {user_id}: {e}")
        return None
    finally:
        cursor.close()
        release_db_connection(conn)

def get_user_preferences(user_id: int) -> Dict[str, Any]:
    """
    Get user preferences.
    
    Args:
        user_id: Telegram user ID
        
    Returns:
        User preferences as dictionary
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        # Check if user exists
        cursor.execute('SELECT id FROM users WHERE id = %s', (user_id,))
        user = cursor.fetchone()
        
        if not user:
            # Create user with default preferences
            return {"language": "en"}
        
        # Check if preferences exist
        cursor.execute('SELECT preferences FROM user_preferences WHERE user_id = %s', (user_id,))
        preferences = cursor.fetchone()
        
        if preferences:
            return preferences[0] if preferences[0] else {"language": "en"}
        else:
            # Create default preferences
            default_prefs = {"language": "en"}
            cursor.execute(
                'INSERT INTO user_preferences (user_id, preferences) VALUES (%s, %s)',
                (user_id, json.dumps(default_prefs))
            )
            conn.commit()
            return default_prefs
    except Exception as e:
        logger.error(f"Error getting user preferences: {e}")
        return {"language": "en"}
    finally:
        cursor.close()
        release_db_connection(conn)

def update_user_preferences(user_id: int, preferences: Dict[str, Any]) -> bool:
    """
    Update user preferences.
    
    Args:
        user_id: Telegram user ID
        preferences: Dictionary of preferences
        
    Returns:
        True if successful, False otherwise
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        # Check if user exists
        cursor.execute('SELECT id FROM users WHERE id = %s', (user_id,))
        user = cursor.fetchone()
        
        if not user:
            logger.error(f"Cannot update preferences for non-existent user: {user_id}")
            return False
        
        # Update preferences
        cursor.execute(
            '''
            INSERT INTO user_preferences (user_id, preferences) 
            VALUES (%s, %s)
            ON CONFLICT (user_id) 
            DO UPDATE SET preferences = %s, updated_at = CURRENT_TIMESTAMP
            ''',
            (user_id, json.dumps(preferences), json.dumps(preferences))
        )
        conn.commit()
        return True
    except Exception as e:
        logger.error(f"Error updating user preferences: {e}")
        conn.rollback()
        return False
    finally:
        cursor.close()
        release_db_connection(conn)

def get_user_language(user_id: int) -> str:
    """
    Get user language code.
    
    Args:
        user_id: Telegram user ID
        
    Returns:
        Language code (defaults to 'en')
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        cursor.execute('SELECT language_code FROM users WHERE id = %s', (user_id,))
        result = cursor.fetchone()
        
        if result and result[0]:
            return result[0]
        return 'en'
    except Exception as e:
        logger.error(f"Error getting user language: {e}")
        return 'en'
    finally:
        cursor.close()
        release_db_connection(conn)

def update_user(user_id: int, **kwargs) -> bool:
    """
    Update user information.
    
    Args:
        user_id: Telegram user ID
        **kwargs: Fields to update (e.g., balance=100, language_code='en')
        
    Returns:
        True if successful, False otherwise
    """
    if not kwargs:
        logger.error("No fields provided for update_user")
        return False
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        # Build SET clause
        set_clause = ", ".join([f"{key} = %s" for key in kwargs.keys()])
        set_clause += ", updated_at = CURRENT_TIMESTAMP"
        
        # Build query
        query = f"UPDATE users SET {set_clause} WHERE id = %s"
        
        # Build parameters
        params = list(kwargs.values())
        params.append(user_id)
        
        # Execute query
        cursor.execute(query, params)
        conn.commit()
        
        if cursor.rowcount > 0:
            logger.info(f"Updated user {user_id} with {kwargs}")
            return True
        else:
            logger.warning(f"No user found with ID {user_id}")
            return False
    except Exception as e:
        logger.error(f"Error updating user: {e}")
        conn.rollback()
        return False
    finally:
        cursor.close()
        release_db_connection(conn)

def update_user_language(user_id: int, language_code: str) -> bool:
    """
    Update user's language preference.
    
    Args:
        user_id: Telegram user ID
        language_code: Language code
        
    Returns:
        True if successful, False otherwise
    """
    return update_user(user_id, language_code=language_code)

# Settings functions

def get_setting(key: str) -> Any:
    """
    Get a setting from the database.
    
    Args:
        key: Setting key
        
    Returns:
        Setting value or None if not found
    """
    conn = get_db_connection()
    cursor = conn.cursor(cursor_factory=DictCursor)
    
    try:
        cursor.execute('SELECT value FROM settings WHERE key = %s', (key,))
        result = cursor.fetchone()
        
        if result:
            # Return the value as a string to ensure it can be properly parsed by json.loads()
            if isinstance(result['value'], dict):
                return json.dumps(result['value'])
            return result['value']
        return None
    except Exception as e:
        logger.error(f"Error getting setting: {e}")
        return None
    finally:
        cursor.close()
        release_db_connection(conn)


def update_setting(key: str, value: str) -> bool:
    """
    Update a setting value.
    
    Args:
        key: Setting key
        value: Setting value
        
    Returns:
        True if successful, False otherwise
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        cursor.execute('UPDATE settings SET value = %s WHERE key = %s', (value, key))
        conn.commit()
        return True
    except Exception as e:
        logger.error(f"Error updating setting: {e}")
        conn.rollback()
        return False
    finally:
        cursor.close()
        release_db_connection(conn)


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
    conn = get_db_connection()
    cursor = conn.cursor(cursor_factory=DictCursor)
    
    try:
        # Create order
        cursor.execute(
            'INSERT INTO orders (user_id, service_id, amount) VALUES (%s, %s, %s) RETURNING *',
            (user_id, service_id, amount)
        )
        
        order = cursor.fetchone()
        conn.commit()
        
        if order:
            return dict(order)
        return None
    except Exception as e:
        logger.error(f"Error creating order: {e}")
        conn.rollback()
        return None
    finally:
        cursor.close()
        release_db_connection(conn)


def create_payment(user_id: int, order_id: int, amount: int, payment_method: str, details: Dict[str, Any] = None) -> Optional[Dict[str, Any]]:
    """
    Create a new payment.
    
    Args:
        user_id: Telegram user ID
        order_id: Order ID
        amount: Payment amount
        payment_method: Payment method (e.g., 'card', 'zarinpal', 'wallet')
        details: Optional payment details
        
    Returns:
        Payment data as dictionary or None if failed
    """
    conn = get_db_connection()
    cursor = conn.cursor(cursor_factory=DictCursor)
    
    try:
        current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
        # Create payment
        cursor.execute(
            'INSERT INTO payments (user_id, order_id, amount, payment_method, details, status, created_at, updated_at) VALUES (%s, %s, %s, %s, %s, %s, %s, %s) RETURNING *',
            (user_id, order_id, amount, payment_method, json.dumps(details) if details else None, 'pending', current_time, current_time)
        )
        
        payment = cursor.fetchone()
        conn.commit()
        
        if payment:
            return dict(payment)
        return None
    except Exception as e:
        logger.error(f"Error creating payment: {e}")
        conn.rollback()
        return None
    finally:
        cursor.close()
        release_db_connection(conn)


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
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
        # Update payment
        if transaction_id and details:
            cursor.execute(
                'UPDATE payments SET status = %s, transaction_id = %s, details = %s, updated_at = %s WHERE id = %s',
                (status, transaction_id, details, current_time, payment_id)
            )
        elif transaction_id:
            cursor.execute(
                'UPDATE payments SET status = %s, transaction_id = %s, updated_at = %s WHERE id = %s',
                (status, transaction_id, current_time, payment_id)
            )
        elif details:
            cursor.execute(
                'UPDATE payments SET status = %s, details = %s, updated_at = %s WHERE id = %s',
                (status, details, current_time, payment_id)
            )
        else:
            cursor.execute(
                'UPDATE payments SET status = %s, updated_at = %s WHERE id = %s',
                (status, current_time, payment_id)
            )
        
        conn.commit()
        
        # If payment is completed, update order status
        if status == 'completed':
            cursor.execute('SELECT order_id FROM payments WHERE id = %s', (payment_id,))
            result = cursor.fetchone()
            
            if result:
                order_id = result['order_id']
                cursor.execute(
                    'UPDATE orders SET status = %s, updated_at = %s WHERE id = %s',
                    ('completed', current_time, order_id)
                )
                conn.commit()
        
        return True
    except Exception as e:
        logger.error(f"Error updating payment status: {e}")
        conn.rollback()
        return False
    finally:
        cursor.close()
        release_db_connection(conn)


# Account functions

def create_account(user_id: int, service_id: int, server_id: int, name: str, config: Dict[str, Any], expiry_date: str, traffic_limit: int) -> Optional[Dict[str, Any]]:
    """
    Create a new account.
    
    Args:
        user_id: Telegram user ID
        service_id: Service ID
        server_id: Server ID
        name: Account name
        config: Account configuration
        expiry_date: Account expiry date
        traffic_limit: Traffic limit in bytes
        
    Returns:
        Account data as dictionary or None if failed
    """
    conn = get_db_connection()
    cursor = conn.cursor(cursor_factory=DictCursor)
    
    try:
        current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
        # Create account
        cursor.execute(
            'INSERT INTO accounts (user_id, service_id, server_id, name, config, expiry_date, traffic_limit, created_at, updated_at) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s) RETURNING *',
            (user_id, service_id, server_id, name, json.dumps(config), expiry_date, traffic_limit, current_time, current_time)
        )
        
        account = cursor.fetchone()
        conn.commit()
        
        if account:
            return dict(account)
        return None
    except Exception as e:
        logger.error(f"Error creating account: {e}")
        conn.rollback()
        return None
    finally:
        cursor.close()
        release_db_connection(conn)


def get_account(account_id: int) -> Optional[Dict[str, Any]]:
    """
    Get account information by ID.
    
    Args:
        account_id: Account ID
        
    Returns:
        Account information as a dictionary or None if not found
    """
    conn = get_db_connection()
    cursor = conn.cursor(cursor_factory=DictCursor)
    
    try:
        cursor.execute('''
        SELECT * FROM accounts WHERE id = %s
        ''', (account_id,))
        
        account = cursor.fetchone()
        if account:
            return dict(account)
        return None
    except Exception as e:
        logger.error(f"Error getting account {account_id}: {e}")
        return None
    finally:
        cursor.close()
        release_db_connection(conn)


def get_user_accounts(user_id: int) -> List[Dict[str, Any]]:
    """
    Get all accounts for a user.
    
    Args:
        user_id: Telegram user ID
        
    Returns:
        List of account dictionaries
    """
    conn = get_db_connection()
    cursor = conn.cursor(cursor_factory=DictCursor)
    
    try:
        cursor.execute('''
        SELECT * FROM accounts WHERE user_id = %s ORDER BY created_at DESC
        ''', (user_id,))
        
        accounts = cursor.fetchall()
        return [dict(account) for account in accounts]
    except Exception as e:
        logger.error(f"Error getting user accounts: {e}")
        return []
    finally:
        cursor.close()
        release_db_connection(conn)


def update_account_status(account_id: int, status: str) -> bool:
    """
    Update account status.
    
    Args:
        account_id: Account ID
        status: Account status ('active', 'expired', 'suspended')
        
    Returns:
        True if successful, False otherwise
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
        cursor.execute(
            'UPDATE accounts SET status = %s, updated_at = %s WHERE id = %s',
            (status, current_time, account_id)
        )
        conn.commit()
        return True
    except Exception as e:
        logger.error(f"Error updating account status: {e}")
        conn.rollback()
        return False
    finally:
        cursor.close()
        release_db_connection(conn)


def update_account_traffic(account_id: int, traffic_used: int) -> bool:
    """
    Update account traffic usage.
    
    Args:
        account_id: Account ID
        traffic_used: Traffic used in bytes
        
    Returns:
        True if successful, False otherwise
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
        cursor.execute(
            'UPDATE accounts SET traffic_used = %s, updated_at = %s WHERE id = %s',
            (traffic_used, current_time, account_id)
        )
        conn.commit()
        return True
    except Exception as e:
        logger.error(f"Error updating account traffic: {e}")
        conn.rollback()
        return False
    finally:
        cursor.close()
        release_db_connection(conn)


# Support ticket functions

def create_ticket(user_id: int, subject: str, message: str) -> Optional[str]:
    """
    Create a new support ticket.
    
    Args:
        user_id: Telegram user ID
        subject: Ticket subject
        message: Ticket message
        
    Returns:
        Ticket ID if successful, None otherwise
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        ticket_id = str(uuid.uuid4())
        
        cursor.execute(
            '''
            INSERT INTO tickets (
                id, user_id, subject, status, created_at, updated_at
            ) VALUES (%s, %s, %s, %s, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP)
            ''',
            (
                ticket_id,
                user_id,
                subject,
                'open'
            )
        )
        
        # Add the first message
        message_id = str(uuid.uuid4())
        cursor.execute(
            '''
            INSERT INTO ticket_messages (
                id, ticket_id, user_id, message, created_at
            ) VALUES (%s, %s, %s, %s, CURRENT_TIMESTAMP)
            ''',
            (
                message_id,
                ticket_id,
                user_id,
                message
            )
        )
        
        conn.commit()
        logger.info(f"Created ticket {ticket_id} for user {user_id}")
        return ticket_id
    except Exception as e:
        logger.error(f"Error creating ticket: {e}")
        conn.rollback()
        return None
    finally:
        cursor.close()
        release_db_connection(conn)


def get_ticket(ticket_id: str) -> Optional[Dict[str, Any]]:
    """
    Get ticket details.
    
    Args:
        ticket_id: Ticket ID
        
    Returns:
        Ticket data if found, None otherwise
    """
    conn = get_db_connection()
    cursor = conn.cursor(cursor_factory=DictCursor)
    
    try:
        cursor.execute(
            '''
            SELECT t.id, t.user_id, u.username, t.subject, t.status, t.created_at, t.updated_at
            FROM tickets t
            JOIN users u ON t.user_id = u.id
            WHERE t.id = %s
            ''',
            (ticket_id,)
        )
        
        result = cursor.fetchone()
        
        if not result:
            return None
            
        ticket = {
            'id': result[0],
            'user_id': result[1],
            'username': result[2],
            'subject': result[3],
            'status': result[4],
            'created_at': result[5],
            'updated_at': result[6],
            'messages': []
        }
        
        # Get messages
        cursor.execute(
            '''
            SELECT m.id, m.user_id, u.username, m.message, m.created_at
            FROM ticket_messages m
            JOIN users u ON m.user_id = u.id
            WHERE m.ticket_id = %s
            ORDER BY m.created_at ASC
            ''',
            (ticket_id,)
        )
        
        messages = cursor.fetchall()
        
        for message in messages:
            ticket['messages'].append({
                'id': message[0],
                'user_id': message[1],
                'username': message[2],
                'message': message[3],
                'created_at': message[4]
            })
            
        return ticket
    except Exception as e:
        logger.error(f"Error getting ticket: {e}")
        return None
    finally:
        cursor.close()
        release_db_connection(conn)


def update_ticket(ticket_id: str, **kwargs) -> bool:
    """
    Update ticket information.
    
    Args:
        ticket_id: Ticket ID
        **kwargs: Fields to update (e.g., status='closed')
        
    Returns:
        True if successful, False otherwise
    """
    if not kwargs:
        logger.error("No fields provided for update_ticket")
        return False
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        # Build SET clause
        set_clause = ", ".join([f"{key} = %s" for key in kwargs.keys()])
        set_clause += ", updated_at = CURRENT_TIMESTAMP"
        
        # Build query
        query = f"UPDATE tickets SET {set_clause} WHERE id = %s"
        
        # Build parameters
        params = list(kwargs.values())
        params.append(ticket_id)
        
        # Execute query
        cursor.execute(query, params)
        conn.commit()
        
        if cursor.rowcount > 0:
            logger.info(f"Updated ticket {ticket_id} with {kwargs}")
            return True
        else:
            logger.warning(f"No ticket found with ID {ticket_id}")
            return False
    except Exception as e:
        logger.error(f"Error updating ticket: {e}")
        conn.rollback()
        return False
    finally:
        cursor.close()
        release_db_connection(conn)


def add_ticket_message(ticket_id: str, user_id: int, message: str) -> Optional[str]:
    """
    Add a message to a ticket.
    
    Args:
        ticket_id: Ticket ID
        user_id: Telegram user ID
        message: Message text
        
    Returns:
        Message ID if successful, None otherwise
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        message_id = str(uuid.uuid4())
        
        cursor.execute(
            '''
            INSERT INTO ticket_messages (
                id, ticket_id, user_id, message, created_at
            ) VALUES (%s, %s, %s, %s, CURRENT_TIMESTAMP)
            ''',
            (
                message_id,
                ticket_id,
                user_id,
                message
            )
        )
        
        # Update ticket updated_at
        cursor.execute(
            'UPDATE tickets SET updated_at = CURRENT_TIMESTAMP WHERE id = %s',
            (ticket_id,)
        )
        
        conn.commit()
        logger.info(f"Added message {message_id} to ticket {ticket_id}")
        return message_id
    except Exception as e:
        logger.error(f"Error adding ticket message: {e}")
        conn.rollback()
        return None
    finally:
        cursor.close()
        release_db_connection(conn)


def get_user_tickets(user_id: int, limit: int = 10) -> List[Dict[str, Any]]:
    """
    Get user tickets.
    
    Args:
        user_id: Telegram user ID
        limit: Maximum number of tickets to return
        
    Returns:
        List of ticket data
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        cursor.execute(
            '''
            SELECT id, subject, status, created_at, updated_at
            FROM tickets
            WHERE user_id = %s
            ORDER BY updated_at DESC
            LIMIT %s
            ''',
            (user_id, limit)
        )
        
        results = cursor.fetchall()
        
        tickets = []
        for result in results:
            tickets.append({
                'id': result[0],
                'subject': result[1],
                'status': result[2],
                'created_at': result[3],
                'updated_at': result[4]
            })
            
        return tickets
    except Exception as e:
        logger.error(f"Error getting user tickets: {e}")
        return []
    finally:
        cursor.close()
        release_db_connection(conn)


def get_all_tickets(status: Optional[str] = None, limit: int = 100, offset: int = 0) -> List[Dict[str, Any]]:
    """
    Get all tickets.
    
    Args:
        status: Filter by status (optional)
        limit: Maximum number of tickets to return
        offset: Offset for pagination
        
    Returns:
        List of ticket data
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        if status:
            cursor.execute(
                '''
                SELECT t.id, t.user_id, u.username, t.subject, t.status, t.created_at, t.updated_at
                FROM tickets t
                JOIN users u ON t.user_id = u.id
                WHERE t.status = %s
                ORDER BY t.updated_at DESC
                LIMIT %s OFFSET %s
                ''',
                (status, limit, offset)
            )
        else:
            cursor.execute(
                '''
                SELECT t.id, t.user_id, u.username, t.subject, t.status, t.created_at, t.updated_at
                FROM tickets t
                JOIN users u ON t.user_id = u.id
                ORDER BY t.updated_at DESC
                LIMIT %s OFFSET %s
                ''',
                (limit, offset)
            )
        
        results = cursor.fetchall()
        
        tickets = []
        for result in results:
            tickets.append({
                'id': result[0],
                'user_id': result[1],
                'username': result[2],
                'subject': result[3],
                'status': result[4],
                'created_at': result[5],
                'updated_at': result[6]
            })
            
        return tickets
    except Exception as e:
        logger.error(f"Error getting all tickets: {e}")
        return []
    finally:
        cursor.close()
        release_db_connection(conn)


def update_system_settings(settings: Dict[str, Any]) -> bool:
    """
    Update system settings.
    
    Args:
        settings: Dictionary of settings to update
        
    Returns:
        True if successful, False otherwise
    """
    if not settings:
        logger.error("No settings provided for update_system_settings")
        return False
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        for key, value in settings.items():
            cursor.execute(
                '''
                INSERT INTO settings (key, value, updated_at)
                VALUES (%s, %s, CURRENT_TIMESTAMP)
                ON CONFLICT (key) DO UPDATE
                SET value = %s, updated_at = CURRENT_TIMESTAMP
                ''',
                (key, value, value)
            )
        
        conn.commit()
        logger.info(f"Updated system settings: {settings}")
        return True
    except Exception as e:
        logger.error(f"Error updating system settings: {e}")
        conn.rollback()
        return False
    finally:
        cursor.close()
        release_db_connection(conn)

# Transaction functions
def create_transaction(user_id: int, amount: int, payment_method: str, description: str = None, reference_id: str = None) -> Optional[str]:
    """
    Create a new transaction.
    
    Args:
        user_id: Telegram user ID
        amount: Transaction amount in Toman
        payment_method: Payment method (card, zarinpal)
        description: Transaction description
        reference_id: External reference ID (e.g., Zarinpal Authority)
        
    Returns:
        Transaction ID if successful, None otherwise
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        transaction_id = str(uuid.uuid4())
        
        cursor.execute(
            '''
            INSERT INTO transactions (
                id, user_id, amount, payment_method, status, description, reference_id, created_at, updated_at
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP)
            ''',
            (
                transaction_id,
                user_id,
                amount,
                payment_method,
                'pending',
                description,
                reference_id
            )
        )
        
        conn.commit()
        logger.info(f"Created transaction {transaction_id} for user {user_id}")
        return transaction_id
    except Exception as e:
        logger.error(f"Error creating transaction: {e}")
        conn.rollback()
        return None
    finally:
        cursor.close()
        release_db_connection(conn)

def get_transaction(transaction_id: str) -> Optional[Dict[str, Any]]:
    """
    Get transaction by ID.
    
    Args:
        transaction_id: Transaction ID
        
    Returns:
        Transaction data if found, None otherwise
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        cursor.execute(
            '''
            SELECT id, user_id, amount, payment_method, status, description, reference_id, 
                   receipt_image, created_at, updated_at
            FROM transactions
            WHERE id = %s
            ''',
            (transaction_id,)
        )
        
        result = cursor.fetchone()
        
        if not result:
            return None
            
        return {
            'id': result[0],
            'user_id': result[1],
            'amount': result[2],
            'payment_method': result[3],
            'status': result[4],
            'description': result[5],
            'reference_id': result[6],
            'receipt_image': result[7],
            'created_at': result[8],
            'updated_at': result[9]
        }
    except Exception as e:
        logger.error(f"Error getting transaction: {e}")
        return None
    finally:
        cursor.close()
        release_db_connection(conn)

def update_transaction(transaction_id: str, **kwargs) -> bool:
    """
    Update transaction information.
    
    Args:
        transaction_id: Transaction ID
        **kwargs: Fields to update (e.g., status='completed', reference_id='123')
        
    Returns:
        True if successful, False otherwise
    """
    if not kwargs:
        logger.error("No fields provided for update_transaction")
        return False
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        # Build SET clause
        set_clause = ", ".join([f"{key} = %s" for key in kwargs.keys()])
        set_clause += ", updated_at = CURRENT_TIMESTAMP"
        
        # Build query
        query = f"UPDATE transactions SET {set_clause} WHERE id = %s"
        
        # Build parameters
        params = list(kwargs.values())
        params.append(transaction_id)
        
        # Execute query
        cursor.execute(query, params)
        conn.commit()
        
        if cursor.rowcount > 0:
            logger.info(f"Updated transaction {transaction_id} with {kwargs}")
            return True
        else:
            logger.warning(f"No transaction found with ID {transaction_id}")
            return False
    except Exception as e:
        logger.error(f"Error updating transaction: {e}")
        conn.rollback()
        return False
    finally:
        cursor.close()
        release_db_connection(conn)

def get_user_transactions(user_id: int, limit: int = 10) -> List[Dict[str, Any]]:
    """
    Get user transactions.
    
    Args:
        user_id: Telegram user ID
        limit: Maximum number of transactions to return
        
    Returns:
        List of transaction data
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        cursor.execute(
            '''
            SELECT id, amount, payment_method, status, description, created_at
            FROM transactions
            WHERE user_id = %s
            ORDER BY created_at DESC
            LIMIT %s
            ''',
            (user_id, limit)
        )
        
        results = cursor.fetchall()
        
        transactions = []
        for result in results:
            transactions.append({
                'id': result[0],
                'amount': result[1],
                'payment_method': result[2],
                'status': result[3],
                'description': result[4],
                'created_at': result[5]
            })
            
        return transactions
    except Exception as e:
        logger.error(f"Error getting user transactions: {e}")
        return []
    finally:
        cursor.close()
        release_db_connection(conn)

# Admin functions
def get_all_users(limit: int = 100, offset: int = 0) -> List[Dict[str, Any]]:
    """
    Get all users.
    
    Args:
        limit: Maximum number of users to return
        offset: Offset for pagination
        
    Returns:
        List of user data
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        cursor.execute(
            '''
            SELECT id, username, first_name, last_name, language_code, status, balance, created_at
            FROM users
            ORDER BY created_at DESC
            LIMIT %s OFFSET %s
            ''',
            (limit, offset)
        )
        
        results = cursor.fetchall()
        
        users = []
        for result in results:
            users.append({
                'id': result[0],
                'username': result[1],
                'first_name': result[2],
                'last_name': result[3],
                'language_code': result[4],
                'status': result[5],
                'balance': result[6],
                'created_at': result[7]
            })
            
        return users
    except Exception as e:
        logger.error(f"Error getting all users: {e}")
        return []
    finally:
        cursor.close()
        release_db_connection(conn)

def delete_user(user_id: int) -> bool:
    """
    Delete a user.
    
    Args:
        user_id: Telegram user ID
        
    Returns:
        True if successful, False otherwise
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        # First, delete related records
        cursor.execute('DELETE FROM accounts WHERE user_id = %s', (user_id,))
        cursor.execute('DELETE FROM transactions WHERE user_id = %s', (user_id,))
        cursor.execute('DELETE FROM tickets WHERE user_id = %s', (user_id,))
        
        # Then delete the user
        cursor.execute('DELETE FROM users WHERE id = %s', (user_id,))
        conn.commit()
        
        if cursor.rowcount > 0:
            logger.info(f"Deleted user {user_id}")
            return True
        else:
            logger.warning(f"No user found with ID {user_id}")
            return False
    except Exception as e:
        logger.error(f"Error deleting user: {e}")
        conn.rollback()
        return False
    finally:
        cursor.close()
        release_db_connection(conn)

def reset_user_password(user_id: int) -> Optional[str]:
    """
    Reset user password.
    
    Args:
        user_id: Telegram user ID
        
    Returns:
        New password if successful, None otherwise
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        # Generate a random password
        new_password = str(uuid.uuid4())[:8]
        
        # Update the user
        cursor.execute(
            'UPDATE users SET password = %s, updated_at = CURRENT_TIMESTAMP WHERE id = %s',
            (new_password, user_id)
        )
        conn.commit()
        
        if cursor.rowcount > 0:
            logger.info(f"Reset password for user {user_id}")
            return new_password
        else:
            logger.warning(f"No user found with ID {user_id}")
            return None
    except Exception as e:
        logger.error(f"Error resetting user password: {e}")
        conn.rollback()
        return None
    finally:
        cursor.close()
        release_db_connection(conn)

def get_all_servers(limit: int = 100, offset: int = 0) -> List[Dict[str, Any]]:
    """
    Get all servers.
    
    Args:
        limit: Maximum number of servers to return
        offset: Offset for pagination
        
    Returns:
        List of server data
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        cursor.execute(
            '''
            SELECT id, name, url, username, status, created_at
            FROM servers
            ORDER BY created_at DESC
            LIMIT %s OFFSET %s
            ''',
            (limit, offset)
        )
        
        results = cursor.fetchall()
        
        servers = []
        for result in results:
            servers.append({
                'id': result[0],
                'name': result[1],
                'url': result[2],
                'username': result[3],
                'status': result[4],
                'created_at': result[5]
            })
            
        return servers
    except Exception as e:
        logger.error(f"Error getting all servers: {e}")
        return []
    finally:
        cursor.close()
        release_db_connection(conn)

def get_server_details(server_id: str) -> Optional[Dict[str, Any]]:
    """
    Get server details.
    
    Args:
        server_id: Server ID
        
    Returns:
        Server data if found, None otherwise
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        cursor.execute(
            '''
            SELECT id, name, url, username, password, api_key, status, created_at, updated_at
            FROM servers
            WHERE id = %s
            ''',
            (server_id,)
        )
        
        result = cursor.fetchone()
        
        if not result:
            return None
            
        return {
            'id': result[0],
            'name': result[1],
            'url': result[2],
            'username': result[3],
            'password': result[4],
            'api_key': result[5],
            'status': result[6],
            'created_at': result[7],
            'updated_at': result[8]
        }
    except Exception as e:
        logger.error(f"Error getting server details: {e}")
        return None
    finally:
        cursor.close()
        release_db_connection(conn)

def update_server(server_id: str, **kwargs) -> bool:
    """
    Update server information.
    
    Args:
        server_id: Server ID
        **kwargs: Fields to update (e.g., name='New Name', status='active')
        
    Returns:
        True if successful, False otherwise
    """
    if not kwargs:
        logger.error("No fields provided for update_server")
        return False
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        # Build SET clause
        set_clause = ", ".join([f"{key} = %s" for key in kwargs.keys()])
        set_clause += ", updated_at = CURRENT_TIMESTAMP"
        
        # Build query
        query = f"UPDATE servers SET {set_clause} WHERE id = %s"
        
        # Build parameters
        params = list(kwargs.values())
        params.append(server_id)
        
        # Execute query
        cursor.execute(query, params)
        conn.commit()
        
        if cursor.rowcount > 0:
            logger.info(f"Updated server {server_id} with {kwargs}")
            return True
        else:
            logger.warning(f"No server found with ID {server_id}")
            return False
    except Exception as e:
        logger.error(f"Error updating server: {e}")
        conn.rollback()
        return False
    finally:
        cursor.close()
        release_db_connection(conn)

def delete_server(server_id: str) -> bool:
    """
    Delete a server.
    
    Args:
        server_id: Server ID
        
    Returns:
        True if successful, False otherwise
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        cursor.execute('DELETE FROM servers WHERE id = %s', (server_id,))
        conn.commit()
        
        if cursor.rowcount > 0:
            logger.info(f"Deleted server {server_id}")
            return True
        else:
            logger.warning(f"No server found with ID {server_id}")
            return False
    except Exception as e:
        logger.error(f"Error deleting server: {e}")
        conn.rollback()
        return False
    finally:
        cursor.close()
        release_db_connection(conn)

def get_pending_payments(limit: int = 100, offset: int = 0) -> List[Dict[str, Any]]:
    """
    Get pending payments.
    
    Args:
        limit: Maximum number of payments to return
        offset: Offset for pagination
        
    Returns:
        List of payment data
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        cursor.execute(
            '''
            SELECT t.id, t.user_id, u.username, t.amount, t.payment_method, t.created_at
            FROM transactions t
            JOIN users u ON t.user_id = u.id
            WHERE t.status = 'pending'
            ORDER BY t.created_at DESC
            LIMIT %s OFFSET %s
            ''',
            (limit, offset)
        )
        
        results = cursor.fetchall()
        
        payments = []
        for result in results:
            payments.append({
                'id': result[0],
                'user_id': result[1],
                'username': result[2],
                'amount': result[3],
                'payment_method': result[4],
                'created_at': result[5]
            })
            
        return payments
    except Exception as e:
        logger.error(f"Error getting pending payments: {e}")
        return []
    finally:
        cursor.close()
        release_db_connection(conn)

def verify_payment(transaction_id: str) -> bool:
    """
    Verify a payment.
    
    Args:
        transaction_id: Transaction ID
        
    Returns:
        True if successful, False otherwise
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        # Get transaction details
        cursor.execute(
            'SELECT user_id, amount FROM transactions WHERE id = %s AND status = %s',
            (transaction_id, 'pending')
        )
        
        result = cursor.fetchone()
        
        if not result:
            logger.warning(f"No pending transaction found with ID {transaction_id}")
            return False
            
        user_id, amount = result
        
        # Update transaction status
        cursor.execute(
            'UPDATE transactions SET status = %s, updated_at = CURRENT_TIMESTAMP WHERE id = %s',
            ('completed', transaction_id)
        )
        
        # Update user balance
        cursor.execute(
            'UPDATE users SET balance = balance + %s, updated_at = CURRENT_TIMESTAMP WHERE id = %s',
            (amount, user_id)
        )
        
        conn.commit()
        logger.info(f"Verified payment {transaction_id} for user {user_id}")
        return True
    except Exception as e:
        logger.error(f"Error verifying payment: {e}")
        conn.rollback()
        return False
    finally:
        cursor.close()
        release_db_connection(conn)

def reject_payment(transaction_id: str) -> bool:
    """
    Reject a payment.
    
    Args:
        transaction_id: Transaction ID
        
    Returns:
        True if successful, False otherwise
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        # Update transaction status
        cursor.execute(
            'UPDATE transactions SET status = %s, updated_at = CURRENT_TIMESTAMP WHERE id = %s',
            ('rejected', transaction_id)
        )
        
        conn.commit()
        
        if cursor.rowcount > 0:
            logger.info(f"Rejected payment {transaction_id}")
            return True
        else:
            logger.warning(f"No transaction found with ID {transaction_id}")
            return False
    except Exception as e:
        logger.error(f"Error rejecting payment: {e}")
        conn.rollback()
        return False
    finally:
        cursor.close()
        release_db_connection(conn)

def get_payment_details(transaction_id: str) -> Optional[Dict[str, Any]]:
    """
    Get payment details.
    
    Args:
        transaction_id: Transaction ID
        
    Returns:
        Payment data if found, None otherwise
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        cursor.execute(
            '''
            SELECT t.id, t.user_id, u.username, t.amount, t.payment_method, t.status, 
                   t.description, t.reference_id, t.receipt_image, t.created_at, t.updated_at
            FROM transactions t
            JOIN users u ON t.user_id = u.id
            WHERE t.id = %s
            ''',
            (transaction_id,)
        )
        
        result = cursor.fetchone()
        
        if not result:
            return None
            
        return {
            'id': result[0],
            'user_id': result[1],
            'username': result[2],
            'amount': result[3],
            'payment_method': result[4],
            'status': result[5],
            'description': result[6],
            'reference_id': result[7],
            'receipt_image': result[8],
            'created_at': result[9],
            'updated_at': result[10]
        }
    except Exception as e:
        logger.error(f"Error getting payment details: {e}")
        return None
    finally:
        cursor.close()
        release_db_connection(conn)

def get_system_settings() -> Dict[str, Any]:
    """
    Get system settings.
    
    Returns:
        Dictionary of system settings
    """
    conn = get_db_connection()
    cursor = conn.cursor(cursor_factory=DictCursor)
    
    try:
        cursor.execute('SELECT key, value, description FROM settings')
        results = cursor.fetchall()
        
        settings = {}
        for row in results:
            settings[row['key']] = {
                'value': row['value'],
                'description': row['description']
            }
        
        return settings
    except Exception as e:
        logger.error(f"Error getting system settings: {e}")
        return {}
    finally:
        cursor.close()
        release_db_connection(conn)

def update_account(account_id: str, **kwargs) -> bool:
    """
    Update account information.
    
    Args:
        account_id: UUID of the account
        **kwargs: Fields to update (e.g., status='active', traffic_used=100)
        
    Returns:
        True if successful, False otherwise
    """
    if not kwargs:
        logger.error("No fields provided for update_account")
        return False
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        # Build SET clause
        set_clause = ", ".join([f"{key} = %s" for key in kwargs.keys()])
        set_clause += ", updated_at = CURRENT_TIMESTAMP"
        
        # Build query
        query = f"UPDATE accounts SET {set_clause} WHERE id = %s"
        
        # Build parameters
        params = list(kwargs.values())
        params.append(account_id)
        
        # Execute query
        cursor.execute(query, params)
        conn.commit()
        
        if cursor.rowcount > 0:
            logger.info(f"Updated account {account_id} with {kwargs}")
            return True
        else:
            logger.warning(f"No account found with ID {account_id}")
            return False
    except Exception as e:
        logger.error(f"Error updating account: {e}")
        conn.rollback()
        return False
    finally:
        cursor.close()
        release_db_connection(conn)

def get_all_settings() -> Dict[str, Any]:
    """Get all settings from the database."""
    conn = get_db_connection()
    cursor = conn.cursor(cursor_factory=DictCursor)
    
    try:
        cursor.execute('SELECT key, value, description FROM settings')
        results = cursor.fetchall()
        
        settings = {}
        for row in results:
            settings[row['key']] = {
                'value': row['value'],
                'description': row['description']
            }
        
        return settings
    except Exception as e:
        logger.error(f"Error getting all settings: {e}")
        return {}
    finally:
        cursor.close()
        release_db_connection(conn)

def get_order(order_id: int) -> Optional[Dict[str, Any]]:
    """
    Get order information by ID.
    
    Args:
        order_id: Order ID
        
    Returns:
        Order information as a dictionary or None if not found
    """
    conn = get_db_connection()
    cursor = conn.cursor(cursor_factory=DictCursor)
    
    try:
        cursor.execute('''
        SELECT * FROM orders WHERE id = %s
        ''', (order_id,))
        
        order = cursor.fetchone()
        if order:
            return dict(order)
        return None
    except Exception as e:
        logger.error(f"Error getting order {order_id}: {e}")
        return None
    finally:
        cursor.close()
        release_db_connection(conn)

def get_payment(payment_id: int) -> Optional[Dict[str, Any]]:
    """
    Get payment information by ID.
    
    Args:
        payment_id: Payment ID
        
    Returns:
        Payment information as a dictionary or None if not found
    """
    conn = get_db_connection()
    cursor = conn.cursor(cursor_factory=DictCursor)
    
    try:
        cursor.execute('''
        SELECT * FROM payments WHERE id = %s
        ''', (payment_id,))
        
        payment = cursor.fetchone()
        if payment:
            return dict(payment)
        return None
    except Exception as e:
        logger.error(f"Error getting payment {payment_id}: {e}")
        return None
    finally:
        cursor.close()
        release_db_connection(conn)

def get_ticket(ticket_id: int) -> Optional[Dict[str, Any]]:
    """
    Get ticket information by ID.
    
    Args:
        ticket_id: Ticket ID
        
    Returns:
        Ticket information as a dictionary or None if not found
    """
    conn = get_db_connection()
    cursor = conn.cursor(cursor_factory=DictCursor)
    
    try:
        cursor.execute('''
        SELECT * FROM tickets WHERE id = %s
        ''', (ticket_id,))
        
        ticket = cursor.fetchone()
        if ticket:
            return dict(ticket)
        return None
    except Exception as e:
        logger.error(f"Error getting ticket {ticket_id}: {e}")
        return None
    finally:
        cursor.close()
        release_db_connection(conn) 