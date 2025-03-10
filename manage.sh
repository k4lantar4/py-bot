#!/bin/bash

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[0;33m'
BLUE='\033[0;34m'
NC='\033[0m'

# Helper function
show_usage() {
    echo -e "${BLUE}Telegram Bot Management Script${NC}"
    echo ""
    echo "Usage: $0 [command]"
    echo ""
    echo "Commands:"
    echo "  start       - Start the bot service"
    echo "  stop        - Stop the bot service"
    echo "  restart     - Restart the bot service"
    echo "  status      - Check service status"
    echo "  logs        - View service logs"
    echo "  update      - Update dependencies and restart service"
    echo "  shell       - Open Python shell with environment activated"
    echo "  backup      - Create a backup of the database and configurations"
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
        echo -e "${YELLOW}🚀 Starting bot service...${NC}"
        supervisorctl start telegram_bot
        ;;
    stop)
        echo -e "${YELLOW}🛑 Stopping bot service...${NC}"
        supervisorctl stop telegram_bot
        ;;
    restart)
        echo -e "${YELLOW}🔄 Restarting bot service...${NC}"
        supervisorctl restart telegram_bot
        ;;
    status)
        echo -e "${YELLOW}ℹ️ Checking service status...${NC}"
        supervisorctl status telegram_bot
        ;;
    logs)
        echo -e "${YELLOW}📜 Showing logs...${NC}"
        tail -f logs/error.log logs/output.log
        ;;
    update)
        echo -e "${YELLOW}📦 Updating dependencies...${NC}"
        source venv/bin/activate
        pip install -r requirements.txt
        supervisorctl restart telegram_bot
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
        cp -r data "$BACKUP_DIR/"
        cp .env "$BACKUP_DIR/" 2>/dev/null || true
        echo -e "${GREEN}✅ Backup created in $BACKUP_DIR${NC}"
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