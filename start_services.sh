#!/bin/bash

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[0;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
NC='\033[0m'

echo -e "${BLUE}┌────────────────────────────────────────┐${NC}"
echo -e "${BLUE}│     3X-UI Management System Starter    │${NC}"
echo -e "${BLUE}└────────────────────────────────────────┘${NC}"

# Check if running as root
if [ "$(id -u)" -ne 0 ]; then
    echo -e "${RED}❌ This script must be run as root${NC}"
    exit 1
fi

# Function to check service status
check_service() {
    service_name=$1
    if systemctl is-active --quiet $service_name; then
        echo -e "${GREEN}✅ $service_name is running${NC}"
        return 0
    else
        echo -e "${RED}❌ $service_name is not running${NC}"
        return 1
    fi
}

# Check and start Redis
echo -e "\n${YELLOW}📊 Checking Redis status...${NC}"
if check_service redis-server; then
    echo -e "${GREEN}Redis is already running${NC}"
else
    echo -e "${YELLOW}Starting Redis...${NC}"
    systemctl start redis-server
    if check_service redis-server; then
        echo -e "${GREEN}Redis started successfully${NC}"
    else
        echo -e "${RED}Failed to start Redis. Please check logs.${NC}"
        exit 1
    fi
fi

# Check and configure PostgreSQL
echo -e "\n${YELLOW}📊 Checking PostgreSQL status...${NC}"
if ! command -v psql &> /dev/null; then
    echo -e "${YELLOW}PostgreSQL not found. Installing...${NC}"
    apt update
    apt install -y postgresql postgresql-contrib
fi

if check_service postgresql; then
    echo -e "${GREEN}PostgreSQL is already running${NC}"
else
    echo -e "${YELLOW}Starting PostgreSQL...${NC}"
    systemctl start postgresql
    if check_service postgresql; then
        echo -e "${GREEN}PostgreSQL started successfully${NC}"
    else
        echo -e "${RED}Failed to start PostgreSQL. Please check logs.${NC}"
        exit 1
    fi
fi

# Initialize database if needed
echo -e "\n${YELLOW}🔍 Checking if database is initialized...${NC}"
if [ ! -f ".db_initialized" ]; then
    echo -e "${YELLOW}Initializing database...${NC}"
    
    # Create PostgreSQL user and database if they don't exist
    if sudo -u postgres psql -lqt | cut -d \| -f 1 | grep -qw "xui_db"; then
        echo -e "${GREEN}Database already exists${NC}"
    else
        echo -e "${YELLOW}Creating PostgreSQL user and database...${NC}"
        sudo -u postgres psql -c "CREATE USER xui_user WITH PASSWORD 'password';" || true
        sudo -u postgres psql -c "CREATE DATABASE xui_db OWNER xui_user;" || true
        sudo -u postgres psql -c "GRANT ALL PRIVILEGES ON DATABASE xui_db TO xui_user;" || true
        echo -e "${GREEN}Database created${NC}"
    fi
    
    # Run database initialization script
    echo -e "${YELLOW}Running database initialization scripts...${NC}"
    ./fix_db_init.sh
    
    # Mark database as initialized
    touch .db_initialized
    echo -e "${GREEN}Database initialized${NC}"
fi

# Start backend
echo -e "\n${YELLOW}🚀 Starting backend service...${NC}"

# Check if backend is already running through supervisor
if supervisorctl status backend | grep -q "RUNNING"; then
    echo -e "${GREEN}Backend is already running via supervisor${NC}"
else
    # Start backend with supervisor
    supervisorctl start backend
    echo -e "${GREEN}Backend started via supervisor${NC}"
fi

# Start bot
echo -e "\n${YELLOW}🤖 Starting Telegram bot...${NC}"
if supervisorctl status telegram_bot | grep -q "RUNNING"; then
    echo -e "${GREEN}Telegram bot is already running via supervisor${NC}"
else
    # Start bot with supervisor
    supervisorctl start telegram_bot
    echo -e "${GREEN}Telegram bot started via supervisor${NC}"
fi

# Start Celery services if configured
echo -e "\n${YELLOW}🔄 Checking Celery services...${NC}"
if [ -f "/etc/supervisor/conf.d/celery.conf" ]; then
    if supervisorctl status celery_worker | grep -q "RUNNING"; then
        echo -e "${GREEN}Celery worker is already running via supervisor${NC}"
    else
        supervisorctl start celery_worker
        echo -e "${GREEN}Celery worker started via supervisor${NC}"
    fi
    
    if supervisorctl status celery_beat | grep -q "RUNNING"; then
        echo -e "${GREEN}Celery beat is already running via supervisor${NC}"
    else
        supervisorctl start celery_beat
        echo -e "${GREEN}Celery beat started via supervisor${NC}"
    fi
fi

# Start frontend (if needed)
echo -e "\n${YELLOW}🌐 Checking frontend service...${NC}"
if [ -d "frontend" ]; then
    if supervisorctl status frontend | grep -q "RUNNING"; then
        echo -e "${GREEN}Frontend is already running via supervisor${NC}"
    else
        # Start frontend with supervisor
        supervisorctl start frontend
        echo -e "${GREEN}Frontend started via supervisor${NC}"
    fi
fi

echo -e "\n${GREEN}✅ All services started successfully!${NC}"
echo -e "\n${PURPLE}🌐 API: http://localhost:8000/api/v1${NC}"
echo -e "${PURPLE}📊 API Docs: http://localhost:8000/api/docs${NC}"
echo -e "${PURPLE}🖥️ Frontend: http://localhost:3000${NC}"
echo -e "${PURPLE}🤖 Telegram Bot: @your_bot_username${NC}"

echo -e "\n${YELLOW}ℹ️ To check status of all services:${NC}"
echo -e "  ${BLUE}supervisorctl status${NC}"
echo -e "\n${YELLOW}ℹ️ To view logs:${NC}"
echo -e "  ${BLUE}./manage.sh logs${NC}" 