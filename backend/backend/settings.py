import os

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    
    # Third-party apps
    'rest_framework',
    'rest_framework.authtoken',
    'django_filters',
    'corsheaders',
    
    # Local apps
    'main',
    'v2ray',
    'payments',
    'telegram',
    'api',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

# REST Framework settings
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework.authentication.TokenAuthentication',
        'rest_framework.authentication.SessionAuthentication',
    ],
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticated',
    ],
    'DEFAULT_FILTER_BACKENDS': [
        'django_filters.rest_framework.DjangoFilterBackend',
        'rest_framework.filters.SearchFilter',
        'rest_framework.filters.OrderingFilter',
    ],
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 20,
}

# CORS settings
CORS_ALLOWED_ORIGINS = [
    "http://localhost:3000",
    "http://127.0.0.1:3000",
]

CORS_ALLOW_CREDENTIALS = True

# Telegram Bot settings
TELEGRAM_BOT_TOKEN = os.environ.get('TELEGRAM_BOT_TOKEN', 'YOUR_TELEGRAM_BOT_TOKEN')
TELEGRAM_WEBHOOK_URL = os.environ.get('TELEGRAM_WEBHOOK_URL', 'https://yourdomain.com/webhook/telegram/')
TELEGRAM_ADMIN_USER_IDS = os.environ.get('TELEGRAM_ADMIN_USER_IDS', '').split(',')

# Payment settings
CARD_NUMBER = os.environ.get('CARD_NUMBER', '1234567890123456')
CARD_HOLDER = os.environ.get('CARD_HOLDER', 'Your Name')
CARD_PAYMENT_VERIFICATION_TIMEOUT_MINUTES = 60

# Zarinpal settings
ZARINPAL_MERCHANT = os.environ.get('ZARINPAL_MERCHANT', 'YOUR_ZARINPAL_MERCHANT_ID')
ZARINPAL_SANDBOX = os.environ.get('ZARINPAL_SANDBOX', 'True') == 'True'
ZARINPAL_CALLBACK_URL = os.environ.get('ZARINPAL_CALLBACK_URL', 'https://yourdomain.com/verify/zarinpal/') 