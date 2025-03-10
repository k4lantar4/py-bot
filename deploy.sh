#!/bin/bash
set -e

# Configuration
APP_DIR="/root/py_bot"
VENV_DIR="$APP_DIR/venv"
LOG_DIR="/var/log/telegram_bot"

# Colors for output
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[0;33m'
NC='\033[0m'

echo -e "${YELLOW}🚀 Starting deployment process...${NC}"

# Create necessary directories
sudo mkdir -p $LOG_DIR
sudo chown -R www-data:www-data $LOG_DIR

# Update application code
echo -e "${YELLOW}📥 Pulling latest changes...${NC}"
git pull origin main

# Activate virtual environment
echo -e "${YELLOW}🔌 Activating virtual environment...${NC}"
source $VENV_DIR/bin/activate

# Update dependencies
echo -e "${YELLOW}📚 Updating dependencies...${NC}"
pip install -r requirements.txt

# Apply database migrations
echo -e "${YELLOW}🔄 Applying database migrations...${NC}"
alembic upgrade head

# Restart services
echo -e "${YELLOW}🔄 Restarting services...${NC}"
sudo supervisorctl restart telegram_bot

echo -e "${GREEN}✅ Deployment completed successfully!${NC}" 