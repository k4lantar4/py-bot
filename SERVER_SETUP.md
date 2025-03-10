# 🚀 Server Setup Guide

## Prerequisites
- Ubuntu 20.04 or 22.04 LTS
- Root access to the server
- A Telegram Bot Token (from BotFather)

## Step 1: Initial Server Preparation

1. **Connect to your server via SSH**:
   ```bash
   ssh root@your_server_ip
   ```

2. **Update system packages**:
   ```bash
   apt update && apt upgrade -y
   ```

3. **Install Git**:
   ```bash
   apt install -y git
   ```

## Step 2: Project Setup

1. **Clone or upload the project to your server**:
   
   Either clone from a repository:
   ```bash
   git clone https://your-repository-url.git /root/py_bot
   ```
   
   Or upload files using SCP:
   ```bash
   # From your local machine
   scp -r /path/to/local/project/* root@your_server_ip:/root/py_bot/
   ```

2. **Navigate to the project directory**:
   ```bash
   cd /root/py_bot
   ```

3. **Run the setup script**:
   ```bash
   chmod +x setup.sh
   ./setup.sh
   ```

4. **Configure environment variables**:
   
   Edit the `.env` file:
   ```bash
   nano .env
   ```
   
   Update the following parameters:
   - `TELEGRAM_BOT_TOKEN`: Your bot token from BotFather
   - `ADMIN_USER_IDS`: Comma-separated list of admin Telegram user IDs
   - `API_USERNAME` and `API_PASSWORD`: If using the API
   - Other settings as needed

## Step 3: Start the Bot

1. **Start the bot service**:
   ```bash
   supervisorctl start telegram_bot
   ```

2. **Check service status**:
   ```bash
   supervisorctl status telegram_bot
   ```

3. **View logs if needed**:
   ```bash
   tail -f logs/output.log
   ```

## Step 4: Security Hardening (Optional)

Run the security hardening script:
```bash
chmod +x security.sh
./security.sh
```

This script:
- Updates system packages
- Sets proper file permissions
- Configures UFW firewall
- Installs and configures fail2ban for SSH protection

## Management Commands

Use the management script for common operations:

```bash
./manage.sh start    # Start the bot
./manage.sh stop     # Stop the bot
./manage.sh restart  # Restart the bot
./manage.sh status   # Check service status
./manage.sh logs     # View logs
./manage.sh update   # Update dependencies
./manage.sh backup   # Create a backup
./manage.sh help     # Show help
```

## Deployment Updates

To deploy updates to the server:

1. Transfer updated files to the server
2. Run the deployment script:
   ```bash
   ./deploy.sh
   ```

## Troubleshooting

If the bot fails to start:

1. **Check the logs**:
   ```bash
   tail -f logs/error.log
   ```

2. **Verify environment variables**:
   ```bash
   cat .env
   ```

3. **Check Python dependencies**:
   ```bash
   source venv/bin/activate
   pip list
   ```

4. **Restart the service**:
   ```bash
   supervisorctl restart telegram_bot
   ```

## Backup and Restore

**Create a backup**:
```bash
./manage.sh backup
```

**Restore from backup**:
```bash
# Stop the service first
supervisorctl stop telegram_bot

# Copy data from backup
cp -r backups/YYYYMMDD_HHMMSS/data/* data/
cp backups/YYYYMMDD_HHMMSS/.env .

# Restart the service
supervisorctl start telegram_bot
``` 