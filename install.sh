#!/bin/bash

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Print with color
print_status() {
    echo -e "${GREEN}[✓] $1${NC}"
}

print_error() {
    echo -e "${RED}[✗] $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}[!] $1${NC}"
}

# Check if running as root
if [ "$EUID" -ne 0 ]; then 
    print_error "Please run as root (use sudo)"
    exit 1
fi

# Update system
print_status "Updating system..."
apt-get update && apt-get upgrade -y

# Install required packages
print_status "Installing required packages..."
apt-get install -y \
    apt-transport-https \
    ca-certificates \
    curl \
    gnupg \
    lsb-release \
    git \
    python3-pip \
    python3-venv \
    nginx \
    certbot \
    python3-certbot-nginx

# Install Docker
print_status "Installing Docker..."
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | gpg --dearmor -o /usr/share/keyrings/docker-archive-keyring.gpg

echo \
  "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/docker-archive-keyring.gpg] https://download.docker.com/linux/ubuntu \
  $(lsb_release -cs) stable" | tee /etc/apt/sources.list.d/docker.list > /dev/null

apt-get update
apt-get install -y docker-ce docker-ce-cli containerd.io docker-compose-plugin

# Start and enable Docker
print_status "Starting Docker service..."
systemctl start docker
systemctl enable docker

# Create project directory
print_status "Creating project directory..."
mkdir -p /opt/v2ray-bot
cd /opt/v2ray-bot

# Clone repository if not already cloned
if [ ! -d ".git" ]; then
    print_status "Cloning repository..."
    git clone https://github.com/yourusername/v2ray-bot.git .
fi

# Create and configure environment file
print_status "Setting up environment variables..."
if [ ! -f ".env" ]; then
    cp .env.example .env
    print_warning "Please edit .env file with your configuration"
    nano .env
fi

# Set up SSL certificate
print_status "Setting up SSL certificate..."
read -p "Enter your domain name: " domain_name
certbot --nginx -d $domain_name --non-interactive --agree-tos --email admin@$domain_name

# Build and start Docker containers
print_status "Building and starting Docker containers..."
docker compose build
docker compose up -d

# Check if services are running
print_status "Checking services..."
if docker compose ps | grep -q "Up"; then
    print_status "All services are running successfully!"
else
    print_error "Some services failed to start. Check logs with: docker compose logs"
    exit 1
fi

# Print final instructions
print_status "Installation completed successfully!"
echo -e "\n${GREEN}Next steps:${NC}"
echo "1. Configure your Telegram bot webhook:"
echo "   https://api.telegram.org/bot<YOUR_BOT_TOKEN>/setWebhook?url=https://$domain_name/webhook"
echo "2. Access the admin dashboard at: https://$domain_name/admin"
echo "3. Check logs if needed: docker compose logs -f"
echo -e "\n${YELLOW}Important:${NC}"
echo "- Make sure to set up your payment gateway credentials in the .env file"
echo "- Configure your 3x-UI panel credentials in the .env file"
echo "- Set up proper firewall rules for your domain" 