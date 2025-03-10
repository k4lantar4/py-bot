#!/bin/bash

# Setup script for 3X-UI Management System
set -e

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[0;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
NC='\033[0m'

echo -e "${BLUE}┌────────────────────────────────────────┐${NC}"
echo -e "${BLUE}│     3X-UI Management System Setup      │${NC}"
echo -e "${BLUE}└────────────────────────────────────────┘${NC}"

# Check if running as root
if [ "$(id -u)" -ne 0 ]; then
    echo -e "${RED}❌ This script must be run as root${NC}"
    exit 1
fi

# System dependencies
apt_packages=(
    python3-pip
    python3-venv
    redis-server
    supervisor
    git
    build-essential
    libssl-dev
    libffi-dev
    python3-dev
    postgresql
    postgresql-contrib
    nginx
    nodejs
    npm
    curl
)

# Install system dependencies
echo -e "\n${YELLOW}📦 Installing system packages...${NC}"
apt update
apt install -y "${apt_packages[@]}"

# Make sure Node.js and npm are installed and up to date
echo -e "\n${YELLOW}📦 Setting up Node.js and npm...${NC}"
if ! command -v node &> /dev/null; then
    curl -fsSL https://deb.nodesource.com/setup_16.x | bash -
    apt install -y nodejs
fi

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo -e "\n${YELLOW}🐍 Creating new Python virtual environment...${NC}"
    python3 -m venv venv
else
    echo -e "\n${GREEN}✅ Using existing virtual environment${NC}"
fi

# Activate virtual environment
echo -e "\n${YELLOW}🔌 Activating virtual environment...${NC}"
source venv/bin/activate

# Install Python dependencies
echo -e "\n${YELLOW}📚 Installing Python packages...${NC}"
pip install --upgrade pip
pip install -r requirements.txt

# Create necessary directories
echo -e "\n${YELLOW}📁 Creating necessary directories...${NC}"
mkdir -p logs
mkdir -p data
mkdir -p backups

# Create .env file if it doesn't exist
if [ ! -f ".env" ]; then
    echo -e "\n${YELLOW}⚙️ Creating initial .env configuration...${NC}"
    cp .env.example .env
    
    # Generate a random secret key
    SECRET_KEY=$(openssl rand -hex 32)
    sed -i "s/your_secret_key_here/$SECRET_KEY/g" .env
    
    echo -e "${GREEN}✅ Created .env file${NC}"
    echo -e "${YELLOW}⚠️ Please update the .env file with your actual configuration values${NC}"
fi

# Setup PostgreSQL
echo -e "\n${YELLOW}🐘 Setting up PostgreSQL...${NC}"
if sudo -u postgres psql -lqt | cut -d \| -f 1 | grep -qw "3xui"; then
    echo -e "${GREEN}✅ PostgreSQL database already exists${NC}"
else
    echo -e "${YELLOW}Creating PostgreSQL user and database...${NC}"
    sudo -u postgres psql -c "CREATE USER 3xui WITH PASSWORD 'password';" || true
    sudo -u postgres psql -c "CREATE DATABASE 3xui OWNER 3xui;" || true
    sudo -u postgres psql -c "GRANT ALL PRIVILEGES ON DATABASE 3xui TO 3xui;" || true
    echo -e "${GREEN}✅ PostgreSQL database created${NC}"
fi

# Setup supervisor configs
echo -e "\n${YELLOW}👮 Setting up Supervisor configurations...${NC}"
cp supervisor/*.conf /etc/supervisor/conf.d/
supervisorctl reread
supervisorctl update

# Setup Nginx if it's installed
if command -v nginx &> /dev/null; then
    echo -e "\n${YELLOW}🌐 Setting up Nginx...${NC}"
    cat > /etc/nginx/sites-available/3xui << 'NGINXEOF'
server {
    listen 80;
    server_name _;

    # API
    location /api {
        proxy_pass http://localhost:8000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    }

    # Frontend
    location / {
        proxy_pass http://localhost:3000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    }
}
NGINXEOF

    ln -sf /etc/nginx/sites-available/3xui /etc/nginx/sites-enabled/
    rm -f /etc/nginx/sites-enabled/default
    nginx -t && systemctl restart nginx
    echo -e "${GREEN}✅ Nginx configured${NC}"
fi

# Setup frontend if it exists
if [ -d "frontend" ]; then
    echo -e "\n${YELLOW}🌐 Setting up frontend...${NC}"
    cd frontend
    npm install
    cd ..
    echo -e "${GREEN}✅ Frontend dependencies installed${NC}"
fi

# Initialize the database
echo -e "\n${YELLOW}🗄️ Initializing database...${NC}"
cd backend
source ../venv/bin/activate
python -m scripts.init_db
cd ..

echo -e "\n${GREEN}✅ Setup completed successfully!${NC}"
echo -e "\n${YELLOW}ℹ️ Next steps:${NC}"
echo -e "1. Update the .env file with your actual configuration: ${BLUE}nano .env${NC}"
echo -e "2. Start all services: ${BLUE}./start_services.sh${NC}"
echo -e "3. Check status of all services: ${BLUE}supervisorctl status${NC}"
echo -e "4. Access the API at: ${BLUE}http://your_server_ip/api${NC}"
echo -e "5. Access the frontend at: ${BLUE}http://your_server_ip${NC}" 