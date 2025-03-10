#!/bin/bash

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[0;33m'
BLUE='\033[0;34m'
NC='\033[0m'

echo -e "${BLUE}┌────────────────────────────────────────┐${NC}"
echo -e "${BLUE}│   3X-UI Dependencies Fix Script        │${NC}"
echo -e "${BLUE}└────────────────────────────────────────┘${NC}"

# Activate virtual environment
echo -e "${YELLOW}🔌 Activating virtual environment...${NC}"
source venv/bin/activate

# Install email-validator for Pydantic
echo -e "${YELLOW}📦 Installing missing dependencies...${NC}"
pip install email-validator==2.0.0

# Verify installation
echo -e "${YELLOW}🔍 Verifying installation...${NC}"
if pip show email-validator > /dev/null; then
    echo -e "${GREEN}✅ email-validator successfully installed!${NC}"
else
    echo -e "${RED}❌ Failed to install email-validator. Please check for errors above.${NC}"
    exit 1
fi

# Update requirements.txt file
echo -e "${YELLOW}📝 Updating requirements.txt...${NC}"
if ! grep -q "email-validator" requirements.txt; then
    # Add after pydantic or at the end if not found
    if grep -q "pydantic" requirements.txt; then
        sed -i '/pydantic-settings/a email-validator==2.0.0' requirements.txt
    else
        echo "email-validator==2.0.0" >> requirements.txt
    fi
    echo -e "${GREEN}✅ requirements.txt updated!${NC}"
else
    echo -e "${BLUE}ℹ️ email-validator already in requirements.txt${NC}"
fi

# Restart backend service
echo -e "${YELLOW}🔄 Restarting backend service...${NC}"
supervisorctl restart backend

# Restart celery services if they exist
if supervisorctl status celery_worker &>/dev/null; then
    echo -e "${YELLOW}🔄 Restarting Celery worker...${NC}"
    supervisorctl restart celery_worker
fi

if supervisorctl status celery_beat &>/dev/null; then
    echo -e "${YELLOW}🔄 Restarting Celery beat...${NC}"
    supervisorctl restart celery_beat
fi

echo -e "${GREEN}✅ All services restarted!${NC}"
echo -e "${YELLOW}ℹ️ Check the logs to confirm the backend is running without errors:${NC}"
echo -e "${BLUE}tail -f logs/backend_error.log${NC}" 