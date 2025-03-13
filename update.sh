#!/bin/bash

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

# Backup directory
BACKUP_DIR="backups"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)

# Function to print colored messages
print_message() {
    echo -e "${2}${1}${NC}"
}

# Function to check if Docker is running
check_docker() {
    if ! docker info > /dev/null 2>&1; then
        print_message "Docker is not running. Please start Docker first." "$RED"
        exit 1
    fi
}

# Function to check if Docker Compose is installed
check_docker_compose() {
    if ! command -v docker-compose &> /dev/null; then
        print_message "Docker Compose is not installed. Please install it first." "$RED"
        exit 1
    fi
}

# Function to create backup
create_backup() {
    print_message "Creating backup..." "$YELLOW"
    
    # Create backup directory if it doesn't exist
    mkdir -p "$BACKUP_DIR"
    
    # Backup database
    print_message "Backing up database..." "$YELLOW"
    docker-compose exec -T db pg_dump -U $DB_USER $DB_NAME > "$BACKUP_DIR/db_$TIMESTAMP.sql"
    
    # Backup media files
    print_message "Backing up media files..." "$YELLOW"
    tar -czf "$BACKUP_DIR/media_$TIMESTAMP.tar.gz" media/
    
    # Backup .env file
    print_message "Backing up .env file..." "$YELLOW"
    cp .env "$BACKUP_DIR/env_$TIMESTAMP"
    
    print_message "Backup completed successfully!" "$GREEN"
}

# Function to restore from backup
restore_backup() {
    if [ -z "$1" ]; then
        print_message "Please specify a backup timestamp to restore from." "$RED"
        print_message "Usage: $0 restore YYYYMMDD_HHMMSS" "$YELLOW"
        exit 1
    fi
    
    print_message "Restoring from backup $1..." "$YELLOW"
    
    # Check if backup files exist
    if [ ! -f "$BACKUP_DIR/db_$1.sql" ] || [ ! -f "$BACKUP_DIR/media_$1.tar.gz" ] || [ ! -f "$BACKUP_DIR/env_$1" ]; then
        print_message "Backup files not found!" "$RED"
        exit 1
    fi
    
    # Stop services
    print_message "Stopping services..." "$YELLOW"
    docker-compose down
    
    # Restore database
    print_message "Restoring database..." "$YELLOW"
    docker-compose up -d db
    sleep 5
    docker-compose exec -T db psql -U $DB_USER $DB_NAME < "$BACKUP_DIR/db_$1.sql"
    
    # Restore media files
    print_message "Restoring media files..." "$YELLOW"
    tar -xzf "$BACKUP_DIR/media_$1.tar.gz"
    
    # Restore .env file
    print_message "Restoring .env file..." "$YELLOW"
    cp "$BACKUP_DIR/env_$1" .env
    
    # Start services
    print_message "Starting services..." "$YELLOW"
    docker-compose up -d
    
    print_message "Restore completed successfully!" "$GREEN"
}

# Function to update the application
update_app() {
    print_message "Updating application..." "$YELLOW"
    
    # Pull latest changes
    print_message "Pulling latest changes..." "$YELLOW"
    git pull origin main
    
    # Update dependencies
    print_message "Updating dependencies..." "$YELLOW"
    docker-compose build
    
    # Apply database migrations
    print_message "Applying database migrations..." "$YELLOW"
    docker-compose exec web python manage.py migrate
    
    # Collect static files
    print_message "Collecting static files..." "$YELLOW"
    docker-compose exec web python manage.py collectstatic --noinput
    
    # Restart services
    print_message "Restarting services..." "$YELLOW"
    docker-compose restart
    
    print_message "Update completed successfully!" "$GREEN"
}

# Function to clean old backups
clean_backups() {
    print_message "Cleaning old backups..." "$YELLOW"
    
    # Keep only last 7 backups
    ls -t "$BACKUP_DIR" | tail -n +8 | while read file; do
        rm "$BACKUP_DIR/$file"
        print_message "Removed old backup: $file" "$YELLOW"
    done
    
    print_message "Cleanup completed successfully!" "$GREEN"
}

# Function to show help
show_help() {
    print_message "MRJ Bot Update Script" "$GREEN"
    print_message "Usage: $0 [command]" "$YELLOW"
    print_message "\nCommands:" "$YELLOW"
    print_message "  update    Update the application" "$GREEN"
    print_message "  backup    Create a backup" "$GREEN"
    print_message "  restore   Restore from a backup (requires timestamp)" "$GREEN"
    print_message "  clean     Clean old backups" "$GREEN"
    print_message "  help      Show this help message" "$GREEN"
    print_message "\nExamples:" "$YELLOW"
    print_message "  $0 update" "$GREEN"
    print_message "  $0 backup" "$GREEN"
    print_message "  $0 restore 20240313_123456" "$GREEN"
    print_message "  $0 clean" "$GREEN"
}

# Main script
check_docker
check_docker_compose

case "$1" in
    "update")
        update_app
        ;;
    "backup")
        create_backup
        ;;
    "restore")
        restore_backup "$2"
        ;;
    "clean")
        clean_backups
        ;;
    "help"|"")
        show_help
        ;;
    *)
        print_message "Unknown command: $1" "$RED"
        show_help
        exit 1
        ;;
esac 