#!/bin/bash

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

# Print banner
echo -e "${GREEN}"
echo "Virtual Account Bot & Dashboard Setup"
echo "==================================="
echo -e "${NC}"

# Check if running as root
if [ "$EUID" -ne 0 ]; then 
  echo -e "${RED}Please run as root${NC}"
  exit 1
fi

# Update system
echo -e "${YELLOW}Updating system...${NC}"
apt-get update
apt-get upgrade -y

# Install dependencies
echo -e "${YELLOW}Installing dependencies...${NC}"
apt-get install -y \
    apt-transport-https \
    ca-certificates \
    curl \
    gnupg \
    lsb-release \
    git

# Install Docker
echo -e "${YELLOW}Installing Docker...${NC}"
if ! command -v docker &> /dev/null; then
    curl -fsSL https://get.docker.com -o get-docker.sh
    sh get-docker.sh
    systemctl enable docker
    systemctl start docker
else
    echo -e "${GREEN}Docker already installed${NC}"
fi

# Install Docker Compose
echo -e "${YELLOW}Installing Docker Compose...${NC}"
if ! command -v docker-compose &> /dev/null; then
    curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
    chmod +x /usr/local/bin/docker-compose
else
    echo -e "${GREEN}Docker Compose already installed${NC}"
fi

# Clone repository if not exists
echo -e "${YELLOW}Setting up project...${NC}"
if [ ! -d "virtual-account-bot" ]; then
    git clone https://github.com/yourusername/virtual-account-bot.git
    cd virtual-account-bot
else
    cd virtual-account-bot
    git pull
fi

# Create .env file
echo -e "${YELLOW}Creating environment file...${NC}"
if [ ! -f ".env" ]; then
    cp .env.example .env
    echo -e "${GREEN}Created .env file. Please edit it with your settings${NC}"
    echo -e "${YELLOW}Press any key to edit .env file...${NC}"
    read -n 1 -s
    nano .env
fi

# Setup SSL with Certbot
echo -e "${YELLOW}Do you want to setup SSL with Let's Encrypt? (y/n)${NC}"
read -r setup_ssl
if [ "$setup_ssl" = "y" ]; then
    echo -e "${YELLOW}Installing Certbot...${NC}"
    apt-get install -y certbot python3-certbot-nginx
    
    echo -e "${YELLOW}Enter your domain name:${NC}"
    read -r domain_name
    
    certbot --nginx -d "$domain_name"
fi

# Start services
echo -e "${YELLOW}Starting services...${NC}"
docker-compose up -d

# Print success message
echo -e "${GREEN}"
echo "Setup completed successfully!"
echo "============================"
echo "Your services are now running:"
echo "- Dashboard: http://localhost:3000"
echo "- API: http://localhost:8000"
if [ "$setup_ssl" = "y" ]; then
    echo "- Dashboard: https://$domain_name"
    echo "- API: https://$domain_name/api"
fi
echo -e "${NC}"

# Print next steps
echo -e "${YELLOW}"
echo "Next steps:"
echo "1. Configure your Telegram bot token in .env file"
echo "2. Set up your Zarinpal merchant ID"
echo "3. Configure your admin Telegram IDs"
echo "4. Update your domain settings if using SSL"
echo -e "${NC}"

# Print maintenance commands
echo -e "${YELLOW}"
echo "Useful commands:"
echo "- View logs: docker-compose logs -f"
echo "- Restart services: docker-compose restart"
echo "- Stop services: docker-compose down"
echo "- Update services: ./update.sh"
echo -e "${NC}" 