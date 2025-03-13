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

# Check if running in WSL
if grep -qi microsoft /proc/version; then
    print_warning "Running in WSL environment"
    WSL=true
else
    WSL=false
fi

# Check if running as root
if [ "$EUID" -ne 0 ]; then 
    print_error "Please run as root (use sudo)"
    exit 1
fi

# Function to check if a command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Get public IP
print_status "Getting public IP..."
PUBLIC_IP=$(curl -s ifconfig.me)
if [ -z "$PUBLIC_IP" ]; then
    print_error "Failed to get public IP"
    exit 1
fi
print_status "Public IP: $PUBLIC_IP"

# Update system
print_status "Updating system..."
if ! apt-get update && apt-get upgrade -y; then
    print_error "Failed to update system"
    exit 1
fi

# Install required packages
print_status "Installing required packages..."
REQUIRED_PACKAGES=(
    "apt-transport-https"
    "ca-certificates"
    "curl"
    "gnupg"
    "lsb-release"
    "git"
    "python3-pip"
    "python3-venv"
    "nginx"
    "build-essential"
    "python3-dev"
    "libpq-dev"
    "redis-server"
    "postgresql"
    "postgresql-contrib"
)

for package in "${REQUIRED_PACKAGES[@]}"; do
    if ! dpkg -l | grep -q "^ii  $package "; then
        print_status "Installing $package..."
        if ! apt-get install -y "$package"; then
            print_error "Failed to install $package"
            exit 1
        fi
    else
        print_status "$package is already installed"
    fi
done

# Install Docker if not installed
if ! command_exists docker; then
    print_status "Installing Docker..."
    curl -fsSL https://download.docker.com/linux/ubuntu/gpg | gpg --dearmor -o /usr/share/keyrings/docker-archive-keyring.gpg

    echo \
      "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/docker-archive-keyring.gpg] https://download.docker.com/linux/ubuntu \
      $(lsb_release -cs) stable" | tee /etc/apt/sources.list.d/docker.list > /dev/null

    if ! apt-get update && apt-get install -y docker-ce docker-ce-cli containerd.io docker-compose-plugin; then
        print_error "Failed to install Docker"
        exit 1
    fi
else
    print_status "Docker is already installed"
fi

# Start and enable Docker
print_status "Starting Docker service..."
if [ "$WSL" = false ]; then
    systemctl start docker
    systemctl enable docker
else
    print_warning "Running in WSL - Docker service management skipped"
fi

# Create project directory
print_status "Creating project directory..."
mkdir -p /opt/v2ray-bot
cd /opt/v2ray-bot

# Clone repository if not already cloned
if [ ! -d ".git" ]; then
    print_status "Cloning repository..."
    if ! git clone https://github.com/k4lantar4/py-bot.git .; then
        print_error "Failed to clone repository"
        exit 1
    fi
else
    print_status "Repository already exists"
fi

# Create and configure environment file
print_status "Setting up environment variables..."
if [ ! -f ".env" ]; then
    cp .env.example .env
    # Update environment variables for public IP
    sed -i "s/ALLOWED_HOSTS=.*/ALLOWED_HOSTS=$PUBLIC_IP,localhost,127.0.0.1/" .env
    sed -i "s/DOMAIN=.*/DOMAIN=$PUBLIC_IP/" .env
    print_warning "Please edit .env file with your configuration"
    if command_exists nano; then
        nano .env
    elif command_exists vim; then
        vim .env
    else
        print_warning "No text editor found. Please edit .env file manually"
    fi
else
    print_status ".env file already exists"
fi

# Set up PostgreSQL
print_status "Setting up PostgreSQL..."
if [ "$WSL" = false ]; then
    systemctl start postgresql
    systemctl enable postgresql
else
    print_warning "Running in WSL - PostgreSQL service management skipped"
fi

# Set up Redis
print_status "Setting up Redis..."
if [ "$WSL" = false ]; then
    systemctl start redis-server
    systemctl enable redis-server
else
    print_warning "Running in WSL - Redis service management skipped"
fi

# Configure Nginx for HTTP
print_status "Configuring Nginx..."
cat > /etc/nginx/sites-available/v2ray-bot << EOF
server {
    listen 80;
    server_name $PUBLIC_IP;

    location / {
        proxy_pass http://localhost:8000;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
    }

    location /webhook {
        proxy_pass http://localhost:8000;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
    }
}
EOF

ln -sf /etc/nginx/sites-available/v2ray-bot /etc/nginx/sites-enabled/
rm -f /etc/nginx/sites-enabled/default

# Test and reload Nginx
if ! nginx -t; then
    print_error "Nginx configuration test failed"
    exit 1
fi

if [ "$WSL" = false ]; then
    systemctl reload nginx
else
    print_warning "Running in WSL - Nginx reload skipped"
fi

# Build and start Docker containers
print_status "Building and starting Docker containers..."
if ! docker compose build; then
    print_error "Failed to build Docker containers"
    exit 1
fi

if ! docker compose up -d; then
    print_error "Failed to start Docker containers"
    exit 1
fi

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
echo "   https://api.telegram.org/bot<YOUR_BOT_TOKEN>/setWebhook?url=http://$PUBLIC_IP/webhook"
echo "2. Access the admin dashboard at: http://$PUBLIC_IP/admin"
echo "3. Check logs if needed: docker compose logs -f"
echo -e "\n${YELLOW}Important:${NC}"
echo "- Make sure to set up your payment gateway credentials in the .env file"
echo "- Configure your 3x-UI panel credentials in the .env file"
echo "- Set up proper firewall rules for your server"
echo "- For WSL users: Make sure to forward the necessary ports to Windows"
echo -e "\n${YELLOW}Firewall Setup:${NC}"
echo "Run these commands to open required ports:"
echo "sudo ufw allow 80/tcp"
echo "sudo ufw allow 443/tcp"
echo "sudo ufw allow 8000/tcp"
echo "sudo ufw enable" 