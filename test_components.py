"""
Test script to verify that all components of the MRJBot system are working.
This script will:
1. Try to connect to the PostgreSQL database
2. Try to connect to Redis
3. Try to send a request to the backend API
"""

import os
import sys
import time
import requests
import psycopg2
import redis
from datetime import datetime

def log(message):
    """Log a message with timestamp."""
    print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] {message}")

def test_database(host="localhost", port=5433, max_retries=3):
    """Test connection to PostgreSQL database with retries."""
    retries = 0
    while retries < max_retries:
        try:
            log(f"Testing database connection (attempt {retries+1}/{max_retries})...")
            conn = psycopg2.connect(
                host=host,
                port=port,
                database="mrjbot",
                user="mrjbot",
                password="mrjbot"
            )
            cur = conn.cursor()
            cur.execute("SELECT version();")
            db_version = cur.fetchone()
            log(f"Database connection successful! Version: {db_version[0]}")
            cur.close()
            conn.close()
            return True
        except Exception as e:
            log(f"Database connection failed: {e}")
            retries += 1
            if retries < max_retries:
                log(f"Retrying in 5 seconds...")
                time.sleep(5)
    return False

def test_redis(host="localhost", port=6379, max_retries=3):
    """Test connection to Redis with retries."""
    retries = 0
    while retries < max_retries:
        try:
            log(f"Testing Redis connection (attempt {retries+1}/{max_retries})...")
            r = redis.Redis(host=host, port=port, db=0)
            r.ping()
            log("Redis connection successful!")
            return True
        except Exception as e:
            log(f"Redis connection failed: {e}")
            retries += 1
            if retries < max_retries:
                log(f"Retrying in 5 seconds...")
                time.sleep(5)
    return False

def test_backend_api(host="localhost", port=8000, max_retries=3):
    """Test connection to the backend API with retries."""
    retries = 0
    while retries < max_retries:
        try:
            log(f"Testing backend API connection (attempt {retries+1}/{max_retries})...")
            response = requests.get(f"http://{host}:{port}/api/health/", timeout=10)
            if response.status_code == 200:
                log(f"Backend API connection successful! Response: {response.json()}")
                return True
            else:
                log(f"Backend API connection returned unexpected status code: {response.status_code}")
        except Exception as e:
            log(f"Backend API connection failed: {e}")
        
        retries += 1
        if retries < max_retries:
            log(f"Retrying in 5 seconds...")
            time.sleep(5)
    return False

def main():
    """Run all tests and report results."""
    log("Starting MRJBot components test...")
    
    # Get connection parameters from environment variables or use defaults
    db_host = os.environ.get("DB_HOST", "localhost")
    db_port = int(os.environ.get("DB_PORT", 5433))
    redis_host = os.environ.get("REDIS_HOST", "localhost")
    redis_port = int(os.environ.get("REDIS_PORT", 6379))
    api_host = os.environ.get("API_HOST", "localhost")
    api_port = int(os.environ.get("API_PORT", 8000))
    
    results = {
        "Database": test_database(host=db_host, port=db_port),
        "Redis": test_redis(host=redis_host, port=redis_port),
        "Backend API": test_backend_api(host=api_host, port=api_port),
    }
    
    log("\nTest Results Summary:")
    all_passed = True
    for component, passed in results.items():
        status = "✅ PASSED" if passed else "❌ FAILED"
        log(f"{component}: {status}")
        if not passed:
            all_passed = False
    
    if all_passed:
        log("\n🎉 All tests passed! The MRJBot system is working properly.")
        return 0
    else:
        log("\n⚠️ Some tests failed. Please check the components and try again.")
        return 1

if __name__ == "__main__":
    sys.exit(main()) 