#!/bin/bash

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[0;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Print header
echo -e "${BLUE}======================================================${NC}"
echo -e "${BLUE}       V2Ray Account Management System Installer      ${NC}"
echo -e "${BLUE}======================================================${NC}"
echo ""

# Check if Docker is installed
echo -e "${YELLOW}Checking if Docker is installed...${NC}"
if ! command -v docker &> /dev/null; then
    echo -e "${RED}Docker is not installed. Please install Docker first.${NC}"
    echo -e "${YELLOW}You can install Docker by running:${NC}"
    echo -e "curl -fsSL https://get.docker.com -o get-docker.sh"
    echo -e "sudo sh get-docker.sh"
    exit 1
fi
echo -e "${GREEN}Docker is installed.${NC}"

# Check if Docker Compose is installed
echo -e "${YELLOW}Checking if Docker Compose is installed...${NC}"
if ! command -v docker-compose &> /dev/null; then
    echo -e "${RED}Docker Compose is not installed. Please install Docker Compose first.${NC}"
    echo -e "${YELLOW}You can install Docker Compose by running:${NC}"
    echo -e "sudo curl -L \"https://github.com/docker/compose/releases/download/v2.18.1/docker-compose-\$(uname -s)-\$(uname -m)\" -o /usr/local/bin/docker-compose"
    echo -e "sudo chmod +x /usr/local/bin/docker-compose"
    exit 1
fi
echo -e "${GREEN}Docker Compose is installed.${NC}"

# Check if .env file exists
echo -e "${YELLOW}Checking if .env file exists...${NC}"
if [ ! -f .env ]; then
    echo -e "${YELLOW}Creating .env file from .env.example...${NC}"
    cp .env.example .env
    echo -e "${GREEN}.env file created. Please edit it with your settings.${NC}"
    echo -e "${YELLOW}Do you want to edit the .env file now? (y/n)${NC}"
    read -r answer
    if [ "$answer" = "y" ]; then
        if command -v nano &> /dev/null; then
            nano .env
        elif command -v vim &> /dev/null; then
            vim .env
        else
            echo -e "${RED}No editor found. Please edit the .env file manually.${NC}"
        fi
    fi
else
    echo -e "${GREEN}.env file already exists.${NC}"
fi

# Create SSL directory if it doesn't exist
echo -e "${YELLOW}Creating SSL directory...${NC}"
mkdir -p nginx/ssl
echo -e "${GREEN}SSL directory created.${NC}"

# Generate self-signed SSL certificate if it doesn't exist
echo -e "${YELLOW}Checking if SSL certificate exists...${NC}"
if [ ! -f nginx/ssl/cert.pem ] || [ ! -f nginx/ssl/key.pem ]; then
    echo -e "${YELLOW}Generating self-signed SSL certificate...${NC}"
    openssl req -x509 -nodes -days 365 -newkey rsa:2048 -keyout nginx/ssl/key.pem -out nginx/ssl/cert.pem -subj "/CN=localhost"
    echo -e "${GREEN}Self-signed SSL certificate generated.${NC}"
else
    echo -e "${GREEN}SSL certificate already exists.${NC}"
fi

# Pull Docker images
echo -e "${YELLOW}Pulling Docker images...${NC}"
docker-compose pull
echo -e "${GREEN}Docker images pulled.${NC}"

# Build Docker images
echo -e "${YELLOW}Building Docker images...${NC}"
docker-compose build
echo -e "${GREEN}Docker images built.${NC}"

# Start Docker containers
echo -e "${YELLOW}Starting Docker containers...${NC}"
docker-compose up -d
echo -e "${GREEN}Docker containers started.${NC}"

# Print success message
echo ""
echo -e "${GREEN}======================================================${NC}"
echo -e "${GREEN}       V2Ray Account Management System Installed      ${NC}"
echo -e "${GREEN}======================================================${NC}"
echo ""
echo -e "${YELLOW}You can access the web dashboard at:${NC}"
echo -e "${BLUE}http://localhost${NC}"
echo ""
echo -e "${YELLOW}You can access the admin panel at:${NC}"
echo -e "${BLUE}http://localhost/admin${NC}"
echo ""
echo -e "${YELLOW}To stop the application, run:${NC}"
echo -e "${BLUE}docker-compose down${NC}"
echo ""
echo -e "${YELLOW}To view logs, run:${NC}"
echo -e "${BLUE}docker-compose logs -f${NC}"
echo ""
echo -e "${YELLOW}For more information, please refer to the documentation.${NC}"
echo "" 