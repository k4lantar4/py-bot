#!/bin/bash

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[0;33m'
BLUE='\033[0;34m'
NC='\033[0m'

echo -e "${BLUE}┌────────────────────────────────────────┐${NC}"
echo -e "${BLUE}│    Service Error Diagnostics Script    │${NC}"
echo -e "${BLUE}└────────────────────────────────────────┘${NC}"

# Activate virtual environment
echo -e "${YELLOW}🔌 Activating virtual environment...${NC}"
source venv/bin/activate

# Check supervisor logs for errors
echo -e "${YELLOW}🔍 Checking supervisor logs for errors...${NC}"

# Function to fix a service
fix_service() {
    local service_name=$1
    echo -e "\n${BLUE}═════════════════════════════════════════${NC}"
    echo -e "${YELLOW}🔧 Diagnosing $service_name service...${NC}"
    
    # Check log files for this service
    if [ -f "logs/${service_name}_error.log" ]; then
        echo -e "${YELLOW}📋 Last error logs for $service_name:${NC}"
        tail -n 20 "logs/${service_name}_error.log"
    else
        echo -e "${RED}❌ No error log found for $service_name${NC}"
    fi
    
    case $service_name in
        backend)
            # Check for common backend errors
            if grep -q "EmailStr" logs/backend_error.log 2>/dev/null; then
                echo -e "${YELLOW}🔧 Fixing EmailStr import issue...${NC}"
                cd backend
                
                # Fix EmailStr import in config.py
                if [ -f "app/core/config.py" ]; then
                    echo -e "${YELLOW}Fixing app/core/config.py imports...${NC}"
                    # Make a backup
                    cp app/core/config.py app/core/config.py.bak
                    
                    # Ensure EmailStr is imported from pydantic, not pydantic_settings
                    sed -i 's/from pydantic_settings import BaseSettings, EmailStr/from pydantic_settings import BaseSettings\nfrom pydantic import EmailStr/g' app/core/config.py
                    sed -i 's/from pydantic_settings import BaseSettings, EmailStr, PostgresDsn, validator/from pydantic_settings import BaseSettings, PostgresDsn, validator\nfrom pydantic import EmailStr/g' app/core/config.py
                fi
                
                cd ..
            fi
            
            # Check for database connection errors
            if grep -q "database" logs/backend_error.log 2>/dev/null || grep -q "postgresql" logs/backend_error.log 2>/dev/null; then
                echo -e "${YELLOW}🔧 Checking database connection...${NC}"
                
                # Test PostgreSQL connection
                sudo -u postgres psql -c "SELECT 1 FROM pg_database WHERE datname='xui_db'" | grep -q 1
                if [ $? -eq 0 ]; then
                    echo -e "${GREEN}✅ Database xui_db exists${NC}"
                else
                    echo -e "${RED}❌ Database xui_db does not exist${NC}"
                    echo -e "${YELLOW}🔧 Creating database...${NC}"
                    sudo -u postgres psql -c "CREATE DATABASE xui_db OWNER xui_user;" || true
                fi
            fi
            ;;
            
        celery_worker|celery_beat)
            # Check for celery-specific errors
            echo -e "${YELLOW}🔧 Checking Celery dependencies...${NC}"
            pip install --upgrade celery redis
            
            # Check Redis connection
            echo -e "${YELLOW}🔧 Testing Redis connection...${NC}"
            redis-cli ping
            if [ $? -ne 0 ]; then
                echo -e "${RED}❌ Redis not responding. Restarting Redis...${NC}"
                systemctl restart redis-server
            else
                echo -e "${GREEN}✅ Redis is running${NC}"
            fi
            ;;
            
        frontend)
            # Check for missing node modules
            if grep -q "not found" logs/frontend_error.log 2>/dev/null; then
                echo -e "${YELLOW}🔧 Reinstalling frontend dependencies...${NC}"
                cd frontend
                npm install
                cd ..
                
                echo -e "${YELLOW}🔧 Running fix_frontend.sh script...${NC}"
                ./fix_frontend.sh
            fi
            ;;
    esac
    
    # Restart the service
    echo -e "${YELLOW}🔄 Restarting $service_name service...${NC}"
    supervisorctl restart $service_name
    
    # Check status after restart
    sleep 3
    supervisorctl status $service_name
}

# Check for failing services
failing_services=$(supervisorctl status | grep "FATAL" | awk '{print $1}')

if [ -z "$failing_services" ]; then
    echo -e "${GREEN}✅ No failing services found${NC}"
else
    echo -e "${RED}❌ Found failing services:${NC}"
    supervisorctl status | grep "FATAL"
    
    # Fix each failing service
    for service in $failing_services; do
        fix_service $service
    done
fi

# Fix specific services if requested
if [ "$1" = "backend" ] || [ "$1" = "all" ]; then
    fix_service "backend"
fi

if [ "$1" = "celery" ] || [ "$1" = "all" ]; then
    fix_service "celery_worker"
    fix_service "celery_beat"
fi

if [ "$1" = "frontend" ] || [ "$1" = "all" ]; then
    fix_service "frontend"
fi

# Final status check
echo -e "\n${YELLOW}📋 Current status of all services:${NC}"
supervisorctl status

echo -e "\n${YELLOW}ℹ️ Recommendation:${NC}"
echo -e "1. If services are still failing, check detailed logs: ${BLUE}cd logs && tail -f backend_error.log${NC}"
echo -e "2. You might need to fix specific code issues in the backend or frontend"
echo -e "3. Try running the fix_db_init.sh script again: ${BLUE}./fix_db_init.sh${NC}"
echo -e "4. Try running the fix_frontend.sh script: ${BLUE}./fix_frontend.sh${NC}" 