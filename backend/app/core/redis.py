"""
Redis utilities for the 3X-UI Management System.

This module provides utility functions for interacting with Redis cache.
"""

import json
import logging
from typing import Any, Dict, List, Optional, Set, Union

import redis
from redis import Redis
from redis.exceptions import RedisError

from app.core.config import settings

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Redis key prefixes
CACHE_PREFIX = "cache:"
SESSION_PREFIX = "session:"
RATE_LIMIT_PREFIX = "rate_limit:"
SERVER_STATUS_PREFIX = "server_status:"

# Initialize Redis client
redis_client = None


def format_key(prefix: str, key: str) -> str:
    """
    Format a Redis key with the given prefix.
    
    Args:
        prefix: Key prefix
        key: Key name
        
    Returns:
        Formatted key
    """
    return f"{prefix}{key}"


def set_json(key: str, data: Any, prefix: str = CACHE_PREFIX, expire: Optional[int] = None) -> bool:
    """
    Set JSON data in Redis.
    
    Args:
        key: Key name
        data: Data to store
        prefix: Key prefix
        expire: Expiration time in seconds
        
    Returns:
        True if successful, False otherwise
    """
    formatted_key = format_key(prefix, key)
    try:
        redis_client = get_redis_connection()
        json_data = json.dumps(data)
        if expire:
            redis_client.setex(formatted_key, expire, json_data)
        else:
            redis_client.set(formatted_key, json_data)
        return True
    except (RedisError, TypeError) as e:
        logger.error(f"Error setting JSON in Redis: {str(e)} ❌")
        return False


def get_json(key: str, prefix: str = CACHE_PREFIX) -> Optional[Any]:
    """
    Get JSON data from Redis.
    
    Args:
        key: Key name
        prefix: Key prefix
        
    Returns:
        Data if found, None otherwise
    """
    formatted_key = format_key(prefix, key)
    try:
        redis_client = get_redis_connection()
        data = redis_client.get(formatted_key)
        if data:
            return json.loads(data)
        return None
    except (RedisError, json.JSONDecodeError, TypeError) as e:
        logger.error(f"Error getting JSON from Redis: {str(e)} ❌")
        return None


def delete_key(key: str, prefix: str = CACHE_PREFIX) -> bool:
    """
    Delete a key from Redis.
    
    Args:
        key: Key name
        prefix: Key prefix
        
    Returns:
        True if successful, False otherwise
    """
    formatted_key = format_key(prefix, key)
    try:
        redis_client = get_redis_connection()
        redis_client.delete(formatted_key)
        return True
    except RedisError as e:
        logger.error(f"Error deleting key from Redis: {str(e)} ❌")
        return False


def get_keys_pattern(pattern: str) -> List[str]:
    """
    Get keys matching a pattern.
    
    Args:
        pattern: Key pattern
        
    Returns:
        List of matching keys
    """
    try:
        redis_client = get_redis_connection()
        keys = redis_client.keys(pattern)
        return [key.decode('utf-8') if isinstance(key, bytes) else key for key in keys]
    except RedisError as e:
        logger.error(f"Error getting keys from Redis: {str(e)} ❌")
        return []


def save_threexui_session(server_id: str, session_data: Dict[str, Any], expire_seconds: int = 3600) -> bool:
    """
    Save a 3X-UI session in Redis.
    
    Args:
        server_id: Server ID
        session_data: Session data
        expire_seconds: Expiration time in seconds
        
    Returns:
        True if successful, False otherwise
    """
    return set_json(server_id, session_data, SESSION_PREFIX, expire_seconds)


def get_threexui_session(server_id: str) -> Optional[Dict[str, Any]]:
    """
    Get a 3X-UI session from Redis.
    
    Args:
        server_id: Server ID
        
    Returns:
        Session data if found, None otherwise
    """
    return get_json(server_id, SESSION_PREFIX)


def delete_threexui_session(server_id: str) -> bool:
    """
    Delete a 3X-UI session from Redis.
    
    Args:
        server_id: Server ID
        
    Returns:
        True if successful, False otherwise
    """
    return delete_key(server_id, SESSION_PREFIX)


def update_server_status(server_id: str, status_data: Dict[str, Any], expire_seconds: int = 600) -> bool:
    """
    Update server status in Redis.
    
    Args:
        server_id: Server ID
        status_data: Status data
        expire_seconds: Expiration time in seconds
        
    Returns:
        True if successful, False otherwise
    """
    return set_json(server_id, status_data, SERVER_STATUS_PREFIX, expire_seconds)


def get_server_status(server_id: str) -> Optional[Dict[str, Any]]:
    """
    Get server status from Redis.
    
    Args:
        server_id: Server ID
        
    Returns:
        Status data if found, None otherwise
    """
    return get_json(server_id, SERVER_STATUS_PREFIX)


def get_all_server_statuses() -> Dict[str, Any]:
    """
    Get all server statuses from Redis.
    
    Returns:
        Dictionary of server statuses
    """
    keys = get_keys_pattern(f"{SERVER_STATUS_PREFIX}*")
    result = {}
    
    for full_key in keys:
        server_id = full_key.replace(SERVER_STATUS_PREFIX, "")
        status = get_server_status(server_id)
        if status:
            result[server_id] = status
    
    return result


def increment_rate_limit(key: str, window_seconds: int = 60) -> int:
    """
    Increment a rate limit counter.
    
    Args:
        key: Key name
        window_seconds: Time window in seconds
        
    Returns:
        Current count
    """
    formatted_key = format_key(RATE_LIMIT_PREFIX, key)
    try:
        redis_client = get_redis_connection()
        current = redis_client.incr(formatted_key)
        
        # Set expiry if this is the first increment
        if current == 1:
            redis_client.expire(formatted_key, window_seconds)
        
        return current
    except (RedisError, ValueError):
        return 0


def get_rate_limit_count(key: str) -> int:
    """
    Get the current rate limit count.
    
    Args:
        key: Key name
        
    Returns:
        The count if found, 0 otherwise
    """
    formatted_key = format_key(RATE_LIMIT_PREFIX, key)
    try:
        redis_client = get_redis_connection()
        count = redis_client.get(formatted_key)
        return int(count) if count else 0
    except (RedisError, ValueError):
        return 0


def get_redis_connection() -> Redis:
    """
    Get a Redis connection.
    
    Returns:
        Redis: Redis connection
    """
    global redis_client
    
    if redis_client is not None:
        return redis_client
    
    try:
        redis_client = redis.Redis(
            host=settings.REDIS_HOST,
            port=settings.REDIS_PORT,
            db=settings.REDIS_DB,
            password=settings.REDIS_PASSWORD,
            decode_responses=True,
            socket_timeout=5,
            socket_connect_timeout=5,
            retry_on_timeout=True
        )
        # Test connection
        redis_client.ping()
        return redis_client
    except (RedisError, ConnectionError) as e:
        logger.error(f"Redis connection error: {str(e)} ❌")
        logger.warning("Using dummy Redis implementation ⚠️")
        redis_client = DummyRedis()
        return redis_client


class DummyRedis:
    """
    Dummy Redis implementation for development and testing.
    """
    
    def __init__(self):
        """Initialize the dummy Redis store."""
        self.store = {}
        logger.warning("Using DummyRedis - data will not persist!")
    
    def ping(self):
        """Ping the dummy Redis server."""
        return True
    
    def get(self, key):
        """Get a value from the dummy Redis store."""
        return self.store.get(key)
    
    def set(self, key, value, ex=None):
        """Set a value in the dummy Redis store."""
        self.store[key] = value
        return True
    
    def setex(self, key, time, value):
        """Set a value with an expiration time in the dummy Redis store."""
        self.store[key] = value
        return True
    
    def delete(self, key):
        """Delete a key from the dummy Redis store."""
        if key in self.store:
            del self.store[key]
        return True
    
    def keys(self, pattern):
        """Get keys matching a pattern from the dummy Redis store."""
        # Simple wildcard matching for keys
        if pattern.endswith('*'):
            prefix = pattern[:-1]
            return [k for k in self.store.keys() if k.startswith(prefix)]
        return [k for k in self.store.keys() if k == pattern]
    
    def incr(self, key):
        """Increment a value in the dummy Redis store."""
        if key not in self.store:
            self.store[key] = "1"
            return 1
        
        try:
            value = int(self.store[key]) + 1
            self.store[key] = str(value)
            return value
        except (ValueError, TypeError):
            return 1
    
    def expire(self, key, seconds):
        """Set an expiration time for a key in the dummy Redis store."""
        # In dummy implementation, we don't actually expire keys
        return True 