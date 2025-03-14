#!/usr/bin/env python
"""
MRJBot System Component Test

This script tests all the major components of the MRJBot system:
1. PostgreSQL database connection
2. Redis connection
3. Django configuration
4. API endpoints (basic health check)
5. Telegram bot connection
"""

import os
import sys
import time
import json
import socket
import requests
import importlib
from datetime import datetime

# Set up colored output
RESET = "\033[0m"
RED = "\033[91m"
GREEN = "\033[92m"
YELLOW = "\033[93m"
BLUE = "\033[94m"
MAGENTA = "\033[95m"
CYAN = "\033[96m"

def print_header(text):
    """Print a section header"""
    print(f"\n{MAGENTA}{'=' * 80}{RESET}")
    print(f"{MAGENTA}= {text}{RESET}")
    print(f"{MAGENTA}{'=' * 80}{RESET}\n")

def print_status(status, message):
    """Print a status message with color"""
    if status == "PASS":
        print(f"{GREEN}✅ PASS: {message}{RESET}")
    elif status == "FAIL":
        print(f"{RED}❌ FAIL: {message}{RESET}")
    elif status == "WARN":
        print(f"{YELLOW}⚠️ WARNING: {message}{RESET}")
    elif status == "INFO":
        print(f"{BLUE}ℹ️ INFO: {message}{RESET}")
    else:
        print(f"{CYAN}🔍 {status}: {message}{RESET}")

def test_database_connection():
    """Test the connection to PostgreSQL"""
    print_header("Testing PostgreSQL Database Connection")
    
    try:
        import psycopg2
        
        host = os.environ.get("DB_HOST", "postgres")
        port = int(os.environ.get("DB_PORT", "5432"))
        user = os.environ.get("DB_USER", "mrjbot")
        password = os.environ.get("DB_PASSWORD", "mrjbot")
        dbname = os.environ.get("DB_NAME", "mrjbot")
        
        # Try to connect
        print_status("INFO", f"Connecting to PostgreSQL at {host}:{port}...")
        conn = psycopg2.connect(
            host=host,
            port=port,
            user=user,
            password=password,
            dbname=dbname,
            connect_timeout=10
        )
        
        # Check server version
        cursor = conn.cursor()
        cursor.execute("SELECT version();")
        version = cursor.fetchone()[0]
        print_status("PASS", f"Connected to PostgreSQL successfully: {version}")
        
        # Test creating a table
        print_status("INFO", "Testing table creation...")
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS test_table (
                id SERIAL PRIMARY KEY,
                name VARCHAR(255) NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Test inserting data
        test_value = f"Test entry {datetime.now().isoformat()}"
        cursor.execute(
            "INSERT INTO test_table (name) VALUES (%s) RETURNING id",
            (test_value,)
        )
        inserted_id = cursor.fetchone()[0]
        
        # Test retrieving data
        cursor.execute("SELECT name FROM test_table WHERE id = %s", (inserted_id,))
        retrieved_value = cursor.fetchone()[0]
        
        if retrieved_value == test_value:
            print_status("PASS", f"Database read/write test successful (ID: {inserted_id})")
        else:
            print_status("FAIL", f"Database read/write test failed. Expected: {test_value}, Got: {retrieved_value}")
        
        # Clean up
        cursor.execute("DROP TABLE test_table")
        conn.commit()
        cursor.close()
        conn.close()
        
        return True
    except ImportError:
        print_status("FAIL", "psycopg2 module not installed. Please install it with: pip install psycopg2-binary")
        return False
    except Exception as e:
        print_status("FAIL", f"Database connection failed: {str(e)}")
        return False

def test_redis_connection():
    """Test the connection to Redis"""
    print_header("Testing Redis Connection")
    
    try:
        import redis
        
        host = os.environ.get("REDIS_HOST", "redis")
        port = int(os.environ.get("REDIS_PORT", "6379"))
        password = os.environ.get("REDIS_PASSWORD", "")
        db = int(os.environ.get("REDIS_DB", "0"))
        
        # Try to connect
        print_status("INFO", f"Connecting to Redis at {host}:{port}...")
        r = redis.Redis(
            host=host,
            port=port,
            password=password or None,
            db=db,
            socket_timeout=10
        )
        
        # Check ping
        ping_response = r.ping()
        if ping_response:
            print_status("PASS", "Redis ping successful")
        else:
            print_status("FAIL", "Redis ping failed")
            return False
        
        # Test set/get
        test_key = f"test_key_{int(time.time())}"
        test_value = f"test_value_{datetime.now().isoformat()}"
        
        r.set(test_key, test_value)
        retrieved_value = r.get(test_key).decode('utf-8')
        
        if retrieved_value == test_value:
            print_status("PASS", f"Redis set/get test successful: {test_key} = {test_value}")
        else:
            print_status("FAIL", f"Redis set/get test failed. Expected: {test_value}, Got: {retrieved_value}")
        
        # Clean up
        r.delete(test_key)
        
        # Check info
        info = r.info()
        print_status("INFO", f"Redis version: {info.get('redis_version')}")
        print_status("INFO", f"Redis uptime: {info.get('uptime_in_seconds')} seconds")
        
        return True
    except ImportError:
        print_status("FAIL", "redis module not installed. Please install it with: pip install redis")
        return False
    except Exception as e:
        print_status("FAIL", f"Redis connection failed: {str(e)}")
        return False

def test_django_configuration():
    """Test Django configuration and environment"""
    print_header("Testing Django Configuration")
    
    try:
        # Attempt to add the project directory to the Python path
        project_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), 'backend'))
        if os.path.exists(project_dir):
            sys.path.insert(0, project_dir)
        
        # Try to set the Django settings
        os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
        
        # Try to import Django
        try:
            import django
            print_status("INFO", f"Django version: {django.get_version()}")
            
            try:
                django.setup()
                print_status("PASS", "Django configuration loaded successfully")
                
                # Try to access the database
                try:
                    from django.db import connection
                    with connection.cursor() as cursor:
                        cursor.execute("SELECT 1")
                        result = cursor.fetchone()[0]
                        if result == 1:
                            print_status("PASS", "Django database connection working")
                        else:
                            print_status("FAIL", f"Django database test returned unexpected value: {result}")
                except Exception as e:
                    print_status("FAIL", f"Django database connection failed: {str(e)}")
                
                # Try to import models
                try:
                    # First check if auth User model is available
                    from django.contrib.auth import get_user_model
                    User = get_user_model()
                    print_status("PASS", f"Django auth User model available: {User.__name__}")
                    
                    # Try to count users
                    user_count = User.objects.count()
                    print_status("INFO", f"User count: {user_count}")
                except Exception as e:
                    print_status("FAIL", f"Django model import failed: {str(e)}")
                
                return True
            except Exception as e:
                print_status("FAIL", f"Django setup failed: {str(e)}")
        except ImportError:
            print_status("FAIL", "Django not installed")
    except Exception as e:
        print_status("FAIL", f"Django configuration test failed: {str(e)}")
    
    return False

def test_api_health():
    """Test API health endpoints"""
    print_header("Testing API Health")
    
    base_url = os.environ.get("API_URL", "http://localhost:8000")
    health_endpoint = f"{base_url}/api/health/"
    
    try:
        print_status("INFO", f"Checking API health at {health_endpoint}...")
        response = requests.get(health_endpoint, timeout=10)
        
        if response.status_code == 200:
            try:
                data = response.json()
                print_status("PASS", f"API health check successful: {json.dumps(data, indent=2)}")
                return True
            except ValueError:
                print_status("WARN", "API health check returned non-JSON response")
                print_status("INFO", f"Response: {response.text[:200]}")
        else:
            print_status("FAIL", f"API health check failed with status code: {response.status_code}")
            print_status("INFO", f"Response: {response.text[:200]}")
    except requests.RequestException as e:
        print_status("FAIL", f"API health check request failed: {str(e)}")
    
    return False

def test_telegram_bot():
    """Test Telegram bot configuration"""
    print_header("Testing Telegram Bot Configuration")
    
    try:
        bot_token = os.environ.get("TELEGRAM_BOT_TOKEN")
        if not bot_token:
            print_status("WARN", "TELEGRAM_BOT_TOKEN not set in environment variables")
            return False
        
        try:
            import telegram
            print_status("INFO", f"python-telegram-bot version: {telegram.__version__}")
            
            from telegram import Bot
            bot = Bot(token=bot_token)
            
            # Get bot info
            bot_info = bot.get_me()
            print_status("PASS", f"Bot connected successfully: @{bot_info.username} ({bot_info.first_name})")
            
            # Check webhook info
            webhook_info = bot.get_webhook_info()
            if webhook_info.url:
                print_status("INFO", f"Bot webhook set to: {webhook_info.url}")
                print_status("INFO", f"Pending update count: {webhook_info.pending_update_count}")
                if webhook_info.last_error_date:
                    from datetime import datetime
                    error_time = datetime.fromtimestamp(webhook_info.last_error_date)
                    print_status("WARN", f"Last webhook error: {webhook_info.last_error_message} at {error_time}")
            else:
                print_status("INFO", "Bot is using polling (no webhook set)")
            
            return True
        except ImportError:
            print_status("FAIL", "python-telegram-bot module not installed. Please install it with: pip install python-telegram-bot")
    except Exception as e:
        print_status("FAIL", f"Telegram bot test failed: {str(e)}")
    
    return False

def run_all_tests():
    """Run all component tests and report results"""
    print_header("MRJBot System Component Test")
    print(f"{BLUE}Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}{RESET}")
    print(f"{BLUE}Python: {sys.version}{RESET}")
    print(f"{BLUE}Platform: {sys.platform}{RESET}")
    
    results = {
        "database": test_database_connection(),
        "redis": test_redis_connection(),
        "django": test_django_configuration(),
        "api": test_api_health(),
        "telegram": test_telegram_bot()
    }
    
    # Summary
    print_header("Test Results Summary")
    
    all_passed = True
    for component, result in results.items():
        if result:
            print_status("PASS", f"{component.title()} tests passed")
        else:
            print_status("FAIL", f"{component.title()} tests failed")
            all_passed = False
    
    if all_passed:
        print(f"\n{GREEN}🎉 All tests passed! The MRJBot system is functioning properly.{RESET}")
    else:
        print(f"\n{YELLOW}⚠️ Some tests failed. Please check the detailed logs above for more information.{RESET}")
    
    return all_passed

if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1) 