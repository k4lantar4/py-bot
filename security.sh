#!/bin/bash

# Colors
GREEN='\033[0;32m'
YELLOW='\033[0;33m'
NC='\033[0m'

echo -e "${YELLOW}🔒 Starting security hardening...${NC}"

# Update system packages
echo -e "${YELLOW}📦 Updating system packages...${NC}"
apt update && apt upgrade -y

# Set proper file permissions
echo -e "${YELLOW}🔑 Setting proper file permissions...${NC}"
chmod 750 /root/py_bot
chmod 640 /root/py_bot/.env
chmod 750 /root/py_bot/venv
chmod 750 /root/py_bot/*.sh
chmod 640 /root/py_bot/*.py

# Setup UFW firewall
echo -e "${YELLOW}🔥 Configuring firewall...${NC}"
apt install -y ufw
ufw default deny incoming
ufw default allow outgoing
ufw allow ssh
ufw allow 80/tcp
ufw allow 443/tcp
# Only enable if not already enabled to avoid locking yourself out
ufw status | grep -q "Status: active" || ufw --force enable

# Install fail2ban for SSH protection
echo -e "${YELLOW}🛡️ Installing fail2ban...${NC}"
apt install -y fail2ban
systemctl enable fail2ban
systemctl start fail2ban

echo -e "${GREEN}✅ Security hardening completed!${NC}" 