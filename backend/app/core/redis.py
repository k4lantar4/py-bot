"""
Redis client module for caching and session management.

This module initializes and manages the Redis connection for caching and
session management in the 3X-UI Management System.
"""

import json
from typing import Any, Dict, List, Optional, Union
import redis
from redis.exceptions import RedisError

from app.core.config import settings

# Create a Redis client instance
redis_client = redis.from_url(settings.REDIS_URL, decode_responses=True)

# Define key prefixes for different types of data
USER_SESSION_PREFIX = "user_session:"
THREEXUI_SESSION_PREFIX = "threexui_session:"
SERVER_STATUS_PREFIX = "server_status:"
CACHE_PREFIX = "cache:"
RATE_LIMIT_PREFIX = "rate_limit:"
NOTIFICATION_PREFIX = "notification:"


def format_key(prefix: str, key: str) -> str:
    """
    Format a Redis key with the given prefix.
    
    Args:
        prefix: The key prefix
        key: The key to format
        
    Returns:
        The formatted key with prefix
    """
    return f"{prefix}{key}"


def set_json(key: str, data: Any, prefix: str = CACHE_PREFIX, expire: Optional[int] = None) -> bool:
    """
    Set JSON data in Redis.
    
    Args:
        key: The key to store the data under
        data: The data to store
        prefix: The key prefix to use
        expire: Optional expiration time in seconds
        
    Returns:
        True if successful, False otherwise
    """
    formatted_key = format_key(prefix, key)
    try:
        redis_client.set(formatted_key, json.dumps(data))
        if expire:
            redis_client.expire(formatted_key, expire)
        return True
    except RedisError:
        return False


def get_json(key: str, prefix: str = CACHE_PREFIX) -> Optional[Any]:
    """
    Get JSON data from Redis.
    
    Args:
        key: The key to retrieve data for
        prefix: The key prefix to use
        
    Returns:
        The data if found and valid JSON, None otherwise
    """
    formatted_key = format_key(prefix, key)
    try:
        data = redis_client.get(formatted_key)
        if data:
            return json.loads(data)
        return None
    except (RedisError, json.JSONDecodeError):
        return None


def delete_key(key: str, prefix: str = CACHE_PREFIX) -> bool:
    """
    Delete a key from Redis.
    
    Args:
        key: The key to delete
        prefix: The key prefix to use
        
    Returns:
        True if successful, False otherwise
    """
    formatted_key = format_key(prefix, key)
    try:
        return bool(redis_client.delete(formatted_key))
    except RedisError:
        return False


def get_keys_pattern(pattern: str) -> List[str]:
    """
    Get all keys matching a pattern.
    
    Args:
        pattern: The pattern to match
        
    Returns:
        A list of matching keys
    """
    try:
        return redis_client.keys(pattern)
    except RedisError:
        return []


# 3X-UI session management functions
def save_threexui_session(server_id: str, session_data: Dict[str, Any], expire_seconds: int = 3600) -> bool:
    """
    Save a 3X-UI session for a server.
    
    Args:
        server_id: The server ID
        session_data: The session data to save
        expire_seconds: Expiration time in seconds
        
    Returns:
        True if successful, False otherwise
    """
    return set_json(server_id, session_data, THREEXUI_SESSION_PREFIX, expire_seconds)


def get_threexui_session(server_id: str) -> Optional[Dict[str, Any]]:
    """
    Get a 3X-UI session for a server.
    
    Args:
        server_id: The server ID
        
    Returns:
        The session data if found, None otherwise
    """
    return get_json(server_id, THREEXUI_SESSION_PREFIX)


def delete_threexui_session(server_id: str) -> bool:
    """
    Delete a 3X-UI session for a server.
    
    Args:
        server_id: The server ID
        
    Returns:
        True if successful, False otherwise
    """
    return delete_key(server_id, THREEXUI_SESSION_PREFIX)


# Server status functions
def update_server_status(server_id: str, status_data: Dict[str, Any], expire_seconds: int = 600) -> bool:
    """
    Update server status in Redis.
    
    Args:
        server_id: The server ID
        status_data: The status data to save
        expire_seconds: Expiration time in seconds
        
    Returns:
        True if successful, False otherwise
    """
    return set_json(server_id, status_data, SERVER_STATUS_PREFIX, expire_seconds)


def get_server_status(server_id: str) -> Optional[Dict[str, Any]]:
    """
    Get server status from Redis.
    
    Args:
        server_id: The server ID
        
    Returns:
        The status data if found, None otherwise
    """
    return get_json(server_id, SERVER_STATUS_PREFIX)


def get_all_server_statuses() -> Dict[str, Any]:
    """
    Get all server statuses from Redis.
    
    Returns:
        A dictionary mapping server IDs to status data
    """
    keys = get_keys_pattern(f"{SERVER_STATUS_PREFIX}*")
    result = {}
    for key in keys:
        server_id = key.replace(SERVER_STATUS_PREFIX, "")
        status = get_server_status(server_id)
        if status:
            result[server_id] = status
    return result


# Rate limiting functions
def increment_rate_limit(key: str, window_seconds: int = 60) -> int:
    """
    Increment rate limit counter for a key.
    
    Args:
        key: The rate limit key
        window_seconds: The time window in seconds
        
    Returns:
        The new count
    """
    formatted_key = format_key(RATE_LIMIT_PREFIX, key)
    try:
        pipe = redis_client.pipeline()
        pipe.incr(formatted_key)
        pipe.expire(formatted_key, window_seconds)
        result = pipe.execute()
        return result[0]
    except RedisError:
        return 0


def get_rate_limit_count(key: str) -> int:
    """
    Get rate limit count for a key.
    
    Args:
        key: The rate limit key
        
    Returns:
        The count if found, 0 otherwise
    """
    formatted_key = format_key(RATE_LIMIT_PREFIX, key)
    try:
        count = redis_client.get(formatted_key)
        return int(count) if count else 0
    except (RedisError, ValueError):
        return 0 