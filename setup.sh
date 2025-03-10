#!/bin/bash

# Setup script for Python Telegram Bot
set -e

echo "🚀 Starting Python Telegram Bot setup..."

# System dependencies
apt_packages=(
    python3-pip
    python3-venv
    redis-server
    supervisor
    git
    build-essential
    libssl-dev
    libffi-dev
    python3-dev
)

# Install system dependencies
echo "📦 Installing system packages..."
apt update
apt install -y "${apt_packages[@]}"

# Create virtual environment if not exists
if [ ! -d "venv" ]; then
    echo "🐍 Creating new Python virtual environment..."
    python3 -m venv venv
else
    echo "✅ Using existing virtual environment"
fi

# Activate virtual environment
echo "🔌 Activating virtual environment..."
source venv/bin/activate

# Install Python dependencies
echo "📚 Installing Python packages..."
pip install --upgrade pip
pip install -r requirements.txt

# Create necessary directories
mkdir -p logs
mkdir -p data

# Create .env file if it doesn't exist
if [ ! -f ".env" ]; then
    echo "⚙️ Creating initial .env configuration..."
    cat > .env << 'ENVEOF'
# Bot Configuration
TELEGRAM_BOT_TOKEN=your_telegram_bot_token_here
ADMIN_USER_IDS=123456789,987654321

# API Configuration
API_BASE_URL=http://localhost:8000
API_USERNAME=admin
API_PASSWORD=changeme

# Database Configuration
DATABASE_URL=sqlite:///./data/bot.db

# Redis Configuration
REDIS_URL=redis://localhost:6379/0

# Logging
LOG_LEVEL=INFO
ENVEOF

    echo "⚠️ Please update the .env file with your actual configuration values"
fi

# Setup supervisor config
echo "👮 Setting up Supervisor config..."
cat > /etc/supervisor/conf.d/telegram_bot.conf << 'SUPEOF'
[program:telegram_bot]
directory=/root/py_bot
command=/root/py_bot/venv/bin/python bot/bot.py
user=root
autostart=true
autorestart=true
stderr_logfile=/root/py_bot/logs/error.log
stdout_logfile=/root/py_bot/logs/output.log
environment=PYTHONUNBUFFERED=1
SUPEOF

# Reload supervisor
supervisorctl reread
supervisorctl update

echo "✅ Setup completed successfully!"
echo "ℹ️ To start the bot, run: supervisorctl start telegram_bot" 