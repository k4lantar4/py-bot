#!/bin/bash

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[0;33m'
BLUE='\033[0;34m'
NC='\033[0m'

# Server details
SERVER_IP="65.109.207.182"
SERVER_USER="root"
REMOTE_DIR="/root/py_bot"

echo -e "${YELLOW}🚚 Transferring files to server...${NC}"

# Ensure all scripts are executable locally before transfer
chmod +x *.sh

# Files to transfer (add/remove as needed)
files_to_transfer=(
    "requirements.txt"
    "setup.sh"
    "manage.sh"
    "deploy.sh"
    "security.sh"
    "start_services.sh"
    "fix_dependencies.sh"
    "SERVER_SETUP.md"
    ".env.example"
)

# Transfer each file
for file in "${files_to_transfer[@]}"; do
    if [ -f "$file" ]; then
        echo -e "${BLUE}📄 Transferring ${file}...${NC}"
        scp "$file" "${SERVER_USER}@${SERVER_IP}:${REMOTE_DIR}/"
        if [ $? -eq 0 ]; then
            echo -e "${GREEN}✅ Successfully transferred ${file}${NC}"
        else
            echo -e "${RED}❌ Failed to transfer ${file}${NC}"
        fi
    else
        echo -e "${RED}❌ File not found: ${file}${NC}"
    fi
done

# Transfer directories
echo -e "${BLUE}📁 Transferring supervisor directory...${NC}"
ssh ${SERVER_USER}@${SERVER_IP} "mkdir -p ${REMOTE_DIR}/supervisor"
scp supervisor/* "${SERVER_USER}@${SERVER_IP}:${REMOTE_DIR}/supervisor/"

# Transfer bot, backend, and frontend directories if they exist
if [ -d "bot" ]; then
    echo -e "${BLUE}📁 Transferring bot directory...${NC}"
    ssh ${SERVER_USER}@${SERVER_IP} "mkdir -p ${REMOTE_DIR}/bot"
    scp -r bot/* "${SERVER_USER}@${SERVER_IP}:${REMOTE_DIR}/bot/"
fi

if [ -d "backend" ]; then
    echo -e "${BLUE}📁 Transferring backend directory...${NC}"
    ssh ${SERVER_USER}@${SERVER_IP} "mkdir -p ${REMOTE_DIR}/backend"
    scp -r backend/* "${SERVER_USER}@${SERVER_IP}:${REMOTE_DIR}/backend/"
fi

if [ -d "frontend" ]; then
    echo -e "${BLUE}📁 Transferring frontend directory...${NC}"
    ssh ${SERVER_USER}@${SERVER_IP} "mkdir -p ${REMOTE_DIR}/frontend"
    scp -r frontend/* "${SERVER_USER}@${SERVER_IP}:${REMOTE_DIR}/frontend/"
fi

echo -e "${GREEN}🎉 Transfer completed!${NC}"
echo -e "${YELLOW}ℹ️ Next steps:${NC}"
echo -e "1. SSH into your server: ${BLUE}ssh ${SERVER_USER}@${SERVER_IP}${NC}"
echo -e "2. Navigate to the project: ${BLUE}cd ${REMOTE_DIR}${NC}"
echo -e "3. Fix dependencies: ${BLUE}./fix_dependencies.sh${NC}"
echo -e "4. Check and edit .env file if needed: ${BLUE}nano .env${NC}"
echo -e "5. Start all services: ${BLUE}./start_services.sh${NC}" 