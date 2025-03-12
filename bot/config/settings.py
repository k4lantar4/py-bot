import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Bot token
BOT_TOKEN = os.getenv('BOT_TOKEN')

# Base directory
BASE_DIR = Path(__file__).resolve().parent.parent

# API settings
API_URL = os.getenv('API_URL', 'http://backend:8000')
API_TIMEOUT = int(os.getenv('API_TIMEOUT', '30'))

# Redis settings
REDIS_URL = os.getenv('REDIS_URL', 'redis://redis:6379/0')

# Payment settings
ZARINPAL_MERCHANT = os.getenv('ZARINPAL_MERCHANT')
ZARINPAL_SANDBOX = os.getenv('ZARINPAL_SANDBOX', 'true').lower() == 'true'

# Admin settings
ADMIN_IDS = list(map(int, os.getenv('ADMIN_IDS', '').split(','))) 