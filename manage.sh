#!/bin/bash

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[0;33m'
BLUE='\033[0;34m'
NC='\033[0m'

# Services
SERVICES=("backend" "telegram_bot" "frontend" "celery_worker" "celery_beat")

# Helper function
show_usage() {
    echo -e "${BLUE}3X-UI Management System - Management Script${NC}"
    echo ""
    echo "Usage: $0 [command]"
    echo ""
    echo "Commands:"
    echo "  start       - Start all services"
    echo "  stop        - Stop all services"
    echo "  restart     - Restart all services"
    echo "  status      - Check service status"
    echo "  logs        - View service logs"
    echo "  update      - Update dependencies and restart services"
    echo "  shell       - Open Python shell with environment activated"
    echo "  backup      - Create a backup of the database and configurations"
    echo "  db-shell    - Open PostgreSQL shell"
    echo "  redis-cli   - Open Redis CLI"
    echo "  help        - Show this help message"
    echo ""
}

# Check if command is provided
if [ $# -lt 1 ]; then
    show_usage
    exit 1
fi

# Process commands
case "$1" in
    start)
        echo -e "${YELLOW}🚀 Starting all services...${NC}"
        for service in "${SERVICES[@]}"; do
            echo -e "${YELLOW}Starting $service...${NC}"
            supervisorctl start $service
        done
        echo -e "${GREEN}✅ All services started!${NC}"
        ;;
    stop)
        echo -e "${YELLOW}🛑 Stopping all services...${NC}"
        for service in "${SERVICES[@]}"; do
            echo -e "${YELLOW}Stopping $service...${NC}"
            supervisorctl stop $service
        done
        echo -e "${GREEN}✅ All services stopped!${NC}"
        ;;
    restart)
        echo -e "${YELLOW}🔄 Restarting all services...${NC}"
        for service in "${SERVICES[@]}"; do
            echo -e "${YELLOW}Restarting $service...${NC}"
            supervisorctl restart $service
        done
        echo -e "${GREEN}✅ All services restarted!${NC}"
        ;;
    status)
        echo -e "${YELLOW}ℹ️ Checking service status...${NC}"
        supervisorctl status
        ;;
    logs)
        echo -e "${YELLOW}📜 Showing logs...${NC}"
        echo -e "${YELLOW}Available log files:${NC}"
        echo -e "1. Backend logs"
        echo -e "2. Telegram bot logs"
        echo -e "3. Frontend logs"
        echo -e "4. Celery worker logs"
        echo -e "5. Celery beat logs"
        echo -e "6. All logs"
        echo -e "Enter your choice (1-6): "
        read choice
        
        case $choice in
            1) tail -f logs/backend_*.log ;;
            2) tail -f logs/telegram_bot.*.log ;;
            3) tail -f logs/frontend_*.log ;;
            4) tail -f logs/celery_error.log logs/celery_output.log ;;
            5) tail -f logs/celery_beat_*.log ;;
            6) tail -f logs/*.log ;;
            *) echo -e "${RED}Invalid choice!${NC}" ;;
        esac
        ;;
    update)
        echo -e "${YELLOW}📦 Updating dependencies...${NC}"
        source venv/bin/activate
        pip install -r requirements.txt
        
        # Update backend dependencies
        if [ -f "backend/requirements.txt" ]; then
            echo -e "${YELLOW}Updating backend dependencies...${NC}"
            pip install -r backend/requirements.txt
        fi
        
        # Update frontend dependencies
        if [ -d "frontend" ]; then
            echo -e "${YELLOW}Updating frontend dependencies...${NC}"
            cd frontend
            npm install
            cd ..
        fi
        
        # Restart services
        echo -e "${YELLOW}Restarting services...${NC}"
        for service in "${SERVICES[@]}"; do
            supervisorctl restart $service
        done
        
        echo -e "${GREEN}✅ Update completed!${NC}"
        ;;
    shell)
        echo -e "${YELLOW}🐍 Opening Python shell...${NC}"
        source venv/bin/activate
        python
        ;;
    backup)
        echo -e "${YELLOW}💾 Creating backup...${NC}"
        BACKUP_DIR="backups/$(date +%Y%m%d_%H%M%S)"
        mkdir -p "$BACKUP_DIR"
        
        # Backup database
        echo -e "${YELLOW}Backing up PostgreSQL database...${NC}"
        source .env
        PGPASSWORD=$POSTGRES_PASSWORD pg_dump -h $POSTGRES_SERVER -U $POSTGRES_USER -d $POSTGRES_DB > "$BACKUP_DIR/database.sql"
        
        # Backup data directory
        echo -e "${YELLOW}Backing up data directory...${NC}"
        cp -r data "$BACKUP_DIR/" 2>/dev/null || true
        
        # Backup configuration
        echo -e "${YELLOW}Backing up configuration...${NC}"
        cp .env "$BACKUP_DIR/" 2>/dev/null || true
        
        echo -e "${GREEN}✅ Backup created in $BACKUP_DIR${NC}"
        ;;
    db-shell)
        echo -e "${YELLOW}🗄️ Opening PostgreSQL shell...${NC}"
        source .env
        PGPASSWORD=$POSTGRES_PASSWORD psql -h $POSTGRES_SERVER -U $POSTGRES_USER -d $POSTGRES_DB
        ;;
    redis-cli)
        echo -e "${YELLOW}🔄 Opening Redis CLI...${NC}"
        redis-cli
        ;;
    help)
        show_usage
        ;;
    *)
        echo -e "${RED}❌ Unknown command: $1${NC}"
        show_usage
        exit 1
        ;;
esac 