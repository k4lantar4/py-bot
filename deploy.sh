#!/bin/bash
set -e

# Colors for output
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[0;33m'
NC='\033[0m'

echo -e "${YELLOW}🚀 Starting deployment process...${NC}"

# Pull latest code (if using git)
# if [ -d ".git" ]; then
#    echo -e "${YELLOW}📥 Pulling latest changes...${NC}"
#    git pull origin main
# fi

# Activate virtual environment
echo -e "${YELLOW}🔌 Activating virtual environment...${NC}"
source venv/bin/activate

# Update dependencies
echo -e "${YELLOW}📚 Updating dependencies...${NC}"
pip install -r requirements.txt

# Apply database migrations if needed
# echo -e "${YELLOW}🔄 Applying database migrations...${NC}"
# alembic upgrade head

# Restart services
echo -e "${YELLOW}🔄 Restarting services...${NC}"
supervisorctl restart telegram_bot

echo -e "${GREEN}✅ Deployment completed successfully!${NC}" 