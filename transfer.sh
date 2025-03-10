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
    "SERVER_SETUP.md"
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

# Transfer directories if needed
# echo -e "${BLUE}📁 Transferring bot directory...${NC}"
# scp -r bot "${SERVER_USER}@${SERVER_IP}:${REMOTE_DIR}/"

echo -e "${GREEN}🎉 Transfer completed!${NC}"
echo -e "${YELLOW}ℹ️ Next steps:${NC}"
echo -e "1. SSH into your server: ${BLUE}ssh ${SERVER_USER}@${SERVER_IP}${NC}"
echo -e "2. Navigate to the project: ${BLUE}cd ${REMOTE_DIR}${NC}"
echo -e "3. Run setup script: ${BLUE}./setup.sh${NC}"
echo -e "4. Edit .env file: ${BLUE}nano .env${NC}"
echo -e "5. Start the bot: ${BLUE}./manage.sh start${NC}" 