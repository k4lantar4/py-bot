#!/usr/bin/env python3
"""
3X-UI Management System Installer
================================
This script automates the installation process for the 3X-UI Management System.
It performs prerequisite checks, sets up the environment, and installs all
necessary components.

Features:
- Dynamic environment configuration input
- Step-by-step installation process
- Prerequisite checks
- Error handling with detailed checklist
- User-friendly output with emojis

Designed for Ubuntu 22.04+ systems
"""

import os
import sys
import subprocess
import shutil
import platform
import getpass
import json
import time
import re
from typing import Dict, List, Tuple, Optional, Any, Callable
import random

# ANSI color codes for terminal output
class Colors:
    HEADER = '\033[95m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    GREEN = '\033[92m'
    WARNING = '\033[93m'
    RED = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

# Emojis for user-friendly output
class Emojis:
    SUCCESS = "✅"
    ERROR = "❌"
    WARNING = "⚠️"
    INFO = "ℹ️"
    ROCKET = "🚀"
    GEAR = "⚙️"
    PACKAGE = "📦"
    DATABASE = "🗄️"
    SERVER = "🖥️"
    SECURITY = "🔒"
    CLOCK = "⏱️"
    CHECK = "✓"
    CROSS = "✗"
    SPARKLES = "✨"
    WRENCH = "🔧"
    LIGHT_BULB = "💡"

# Installation state to track progress
class InstallState:
    def __init__(self):
        self.prerequisites_met = False
        self.env_configured = False
        self.backend_installed = False
        self.database_initialized = False
        self.frontend_installed = False
        self.telegram_bot_installed = False
        self.services_configured = False
        self.installation_completed = False
        self.errors = []
        self.warnings = []

# Global state object
state = InstallState()

def print_header(text: str) -> None:
    """Print a formatted header text"""
    print(f"\n{Colors.HEADER}{Colors.BOLD}{'=' * 80}{Colors.ENDC}")
    print(f"{Colors.HEADER}{Colors.BOLD}{text.center(80)}{Colors.ENDC}")
    print(f"{Colors.HEADER}{Colors.BOLD}{'=' * 80}{Colors.ENDC}\n")

def print_step(step_number: int, total_steps: int, text: str) -> None:
    """Print a formatted step text"""
    print(f"\n{Colors.CYAN}{Colors.BOLD}[{step_number}/{total_steps}] {text} {Emojis.GEAR}{Colors.ENDC}")

def print_success(text: str) -> None:
    """Print a success message"""
    print(f"{Colors.GREEN}{Emojis.SUCCESS} {text}{Colors.ENDC}")

def print_error(text: str) -> None:
    """Print an error message"""
    print(f"{Colors.RED}{Emojis.ERROR} {text}{Colors.ENDC}")
    state.errors.append(text)

def print_warning(text: str) -> None:
    """Print a warning message"""
    print(f"{Colors.WARNING}{Emojis.WARNING} {text}{Colors.ENDC}")
    state.warnings.append(text)

def print_info(text: str) -> None:
    """Print an informational message"""
    print(f"{Colors.BLUE}{Emojis.INFO} {text}{Colors.ENDC}")

def run_command(command: List[str], error_message: str, success_message: Optional[str] = None) -> Tuple[bool, str, str]:
    """
    Run a shell command and handle its output
    
    Args:
        command: List of command arguments
        error_message: Message to display on error
        success_message: Message to display on success
        
    Returns:
        Tuple of (success boolean, stdout, stderr)
    """
    try:
        process = subprocess.Popen(
            command,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            universal_newlines=True
        )
        stdout, stderr = process.communicate()
        
        if process.returncode != 0:
            print_error(f"{error_message}: {stderr}")
            return False, stdout, stderr
        
        if success_message:
            print_success(success_message)
        return True, stdout, stderr
    except Exception as e:
        print_error(f"{error_message}: {str(e)}")
        return False, "", str(e)

def check_prerequisites() -> bool:
    """
    Check if all prerequisites are installed
    
    Returns:
        Boolean indicating if all prerequisites are met
    """
    print_step(1, 8, "Checking prerequisites")
    
    # Check operating system
    if platform.system() != "Linux":
        print_error("This installer is designed for Linux systems only")
        return False
    
    # Check Ubuntu version
    try:
        with open('/etc/os-release', 'r') as f:
            os_info = {}
            for line in f:
                k, v = line.rstrip().split('=', 1)
                os_info[k] = v.strip('"')
        
        if os_info.get('ID') != 'ubuntu' or float(os_info.get('VERSION_ID', '0')) < 22.04:
            print_warning("This installer is optimized for Ubuntu 22.04+. Some features may not work correctly.")
        else:
            print_success(f"Ubuntu {os_info.get('VERSION_ID')} detected")
    except Exception:
        print_warning("Could not determine OS version. Continuing anyway.")
    
    prerequisites = [
        ("python3", "--version", "Python 3.10+", lambda x: float(x.split()[1].split('.')[:2]) >= 3.10),
        ("pip3", "--version", "pip", lambda x: True),
        ("node", "--version", "Node.js 18+", lambda x: float(x.split('v')[1].split('.')[0]) >= 18),
        ("npm", "--version", "npm 8+", lambda x: float(x.split('.')[0]) >= 8),
        ("postgresql", "--version", "PostgreSQL 14+", lambda x: float(re.search(r'(\d+\.\d+)', x).group(1)) >= 14.0),
        ("redis-cli", "--version", "Redis 6+", lambda x: float(re.search(r'(\d+\.\d+)', x).group(1)) >= 6.0),
    ]
    
    all_passed = True
    
    for cmd, arg, name, version_check in prerequisites:
        success, stdout, stderr = run_command([cmd, arg], f"Failed to check {name}")
        
        if not success:
            print_error(f"{name} is not installed or not in PATH")
            all_passed = False
            continue
        
        try:
            if version_check(stdout):
                print_success(f"{name} is installed ({stdout.strip()})")
            else:
                print_warning(f"Installed {name} version may be too old: {stdout.strip()}")
                all_passed = all_passed and False
        except Exception as e:
            print_warning(f"Could not parse {name} version: {e}")
            all_passed = all_passed and False
    
    # Additional checks
    # Check if ports 3000, 8000, and 5432 are available
    ports_to_check = [3000, 8000, 5432, 6379]
    for port in ports_to_check:
        success, stdout, stderr = run_command(
            ["sudo", "lsof", "-i", f":{port}"],
            f"Failed to check if port {port} is available"
        )
        if stdout.strip():
            print_warning(f"Port {port} is already in use. This might cause conflicts during installation.")
            all_passed = False
        else:
            print_success(f"Port {port} is available")
    
    if all_passed:
        print_success("All prerequisites satisfied!")
        state.prerequisites_met = True
    else:
        print_warning("Some prerequisites are missing. Installation may fail or be incomplete.")
    
    return all_passed

def configure_environment() -> bool:
    """
    Configure environment variables for the application
    
    Returns:
        Boolean indicating if configuration was successful
    """
    print_step(2, 8, "Configuring environment")
    
    # Backend environment variables
    backend_env = {
        "DATABASE_URL": "postgresql://postgres:postgres@localhost/threexui",
        "REDIS_URL": "redis://localhost:6379/0",
        "SECRET_KEY": "".join(random.choice("abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789") for _ in range(64)),
        "ACCESS_TOKEN_EXPIRE_MINUTES": "30",
        "REFRESH_TOKEN_EXPIRE_DAYS": "7",
        "ALGORITHM": "HS256",
        "BACKEND_CORS_ORIGINS": '["http://localhost:3000", "http://localhost:8080"]',
        "SMTP_SERVER": "",
        "SMTP_PORT": "587",
        "SMTP_USERNAME": "",
        "SMTP_PASSWORD": "",
        "SMTP_FROM": "noreply@example.com",
        "ENVIRONMENT": "development"
    }
    
    # Telegram Bot environment variables
    bot_env = {
        "TELEGRAM_BOT_TOKEN": "",
        "ADMIN_USER_IDS": "[]"
    }
    
    # Get user input for database configuration
    print_info("Database Configuration:")
    backend_env["DATABASE_URL"] = input(f"PostgreSQL Connection URL [{backend_env['DATABASE_URL']}]: ") or backend_env["DATABASE_URL"]
    
    # Get user input for Redis configuration
    print_info("Redis Configuration:")
    backend_env["REDIS_URL"] = input(f"Redis Connection URL [{backend_env['REDIS_URL']}]: ") or backend_env["REDIS_URL"]
    
    # Get user input for email configuration
    print_info("Email Configuration (Optional):")
    backend_env["SMTP_SERVER"] = input(f"SMTP Server [{backend_env['SMTP_SERVER']}]: ") or backend_env["SMTP_SERVER"]
    if backend_env["SMTP_SERVER"]:
        backend_env["SMTP_PORT"] = input(f"SMTP Port [{backend_env['SMTP_PORT']}]: ") or backend_env["SMTP_PORT"]
        backend_env["SMTP_USERNAME"] = input(f"SMTP Username [{backend_env['SMTP_USERNAME']}]: ") or backend_env["SMTP_USERNAME"]
        backend_env["SMTP_PASSWORD"] = getpass.getpass(f"SMTP Password: ") or backend_env["SMTP_PASSWORD"]
        backend_env["SMTP_FROM"] = input(f"From Email [{backend_env['SMTP_FROM']}]: ") or backend_env["SMTP_FROM"]
    
    # Get user input for Telegram bot configuration
    print_info("Telegram Bot Configuration (Optional):")
    bot_env["TELEGRAM_BOT_TOKEN"] = input(f"Telegram Bot Token [{bot_env['TELEGRAM_BOT_TOKEN']}]: ") or bot_env["TELEGRAM_BOT_TOKEN"]
    
    if bot_env["TELEGRAM_BOT_TOKEN"]:
        admin_ids = input("Admin User IDs (comma-separated): ")
        if admin_ids:
            try:
                admin_id_list = [int(x.strip()) for x in admin_ids.split(',')]
                bot_env["ADMIN_USER_IDS"] = json.dumps(admin_id_list)
            except ValueError:
                print_warning("Invalid admin IDs format. Using empty list.")
    
    # Write backend .env file
    try:
        with open('backend/.env', 'w') as f:
            for key, value in backend_env.items():
                f.write(f"{key}={value}\n")
        print_success("Backend environment variables configured")
    except Exception as e:
        print_error(f"Failed to write backend environment variables: {str(e)}")
        return False
    
    # Write bot .env file
    try:
        with open('bot/.env', 'w') as f:
            # Include the database and Redis configuration from backend
            for key, value in {**backend_env, **bot_env}.items():
                f.write(f"{key}={value}\n")
        print_success("Telegram bot environment variables configured")
    except Exception as e:
        print_error(f"Failed to write bot environment variables: {str(e)}")
        return False
    
    # Create frontend .env file with API URL
    try:
        with open('frontend/.env', 'w') as f:
            f.write("REACT_APP_API_URL=http://localhost:8000/api\n")
        print_success("Frontend environment variables configured")
    except Exception as e:
        print_error(f"Failed to write frontend environment variables: {str(e)}")
        return False
    
    state.env_configured = True
    return True

def install_backend() -> bool:
    """
    Install backend dependencies and set up the backend
    
    Returns:
        Boolean indicating if installation was successful
    """
    print_step(3, 8, "Installing backend dependencies")
    
    # Create virtual environment if it doesn't exist
    if not os.path.exists('backend/venv'):
        success, stdout, stderr = run_command(
            ["python3", "-m", "venv", "backend/venv"],
            "Failed to create virtual environment",
            "Created virtual environment"
        )
        if not success:
            return False
    
    # Install dependencies
    pip_cmd = ["backend/venv/bin/pip", "install", "-r", "backend/requirements.txt"]
    success, stdout, stderr = run_command(
        pip_cmd,
        "Failed to install backend dependencies",
        "Installed backend dependencies"
    )
    if not success:
        return False
    
    state.backend_installed = True
    return True

def initialize_database() -> bool:
    """
    Initialize the database
    
    Returns:
        Boolean indicating if initialization was successful
    """
    print_step(4, 8, "Initializing database")
    
    # Run the database initialization script
    success, stdout, stderr = run_command(
        ["backend/venv/bin/python", "-m", "scripts.init_db"],
        "Failed to initialize database",
        "Database initialized successfully"
    )
    if not success:
        return False
    
    state.database_initialized = True
    return True

def install_frontend() -> bool:
    """
    Install frontend dependencies
    
    Returns:
        Boolean indicating if installation was successful
    """
    print_step(5, 8, "Installing frontend dependencies")
    
    # Change to frontend directory
    os.chdir('frontend')
    
    # Install dependencies
    success, stdout, stderr = run_command(
        ["npm", "install"],
        "Failed to install frontend dependencies",
        "Installed frontend dependencies"
    )
    
    # Change back to root directory
    os.chdir('..')
    
    if not success:
        return False
    
    # Build frontend for production
    os.chdir('frontend')
    success, stdout, stderr = run_command(
        ["npm", "run", "build"],
        "Failed to build frontend",
        "Frontend built successfully"
    )
    os.chdir('..')
    
    if not success:
        return False
    
    state.frontend_installed = True
    return True

def install_telegram_bot() -> bool:
    """
    Set up the Telegram bot
    
    Returns:
        Boolean indicating if setup was successful
    """
    print_step(6, 8, "Setting up Telegram bot")
    
    # The bot uses the same virtual environment as the backend
    # Check if bot token is configured
    with open('bot/.env', 'r') as f:
        bot_env = f.read()
    
    if "TELEGRAM_BOT_TOKEN=" in bot_env and "TELEGRAM_BOT_TOKEN=\n" not in bot_env:
        print_success("Telegram bot configured")
    else:
        print_warning("Telegram bot token not configured. Bot will not be functional.")
    
    state.telegram_bot_installed = True
    return True

def configure_services() -> bool:
    """
    Configure systemd services for backend, worker, and bot
    
    Returns:
        Boolean indicating if configuration was successful
    """
    print_step(7, 8, "Configuring services")
    
    # Get the current directory
    current_dir = os.path.abspath('.')
    
    # Backend service
    backend_service = f"""[Unit]
Description=3X-UI Management Backend
After=network.target

[Service]
User={getpass.getuser()}
Group={getpass.getuser()}
WorkingDirectory={current_dir}/backend
ExecStart={current_dir}/backend/venv/bin/uvicorn app.main:app --host 0.0.0.0 --port 8000
Restart=always
RestartSec=5
SyslogIdentifier=threexui-backend

[Install]
WantedBy=multi-user.target
"""

    # Celery worker service
    worker_service = f"""[Unit]
Description=3X-UI Management Celery Worker
After=network.target

[Service]
User={getpass.getuser()}
Group={getpass.getuser()}
WorkingDirectory={current_dir}/backend
ExecStart={current_dir}/backend/venv/bin/celery -A app.worker worker --loglevel=info
Restart=always
RestartSec=5
SyslogIdentifier=threexui-worker

[Install]
WantedBy=multi-user.target
"""

    # Telegram Bot service
    bot_service = f"""[Unit]
Description=3X-UI Management Telegram Bot
After=network.target

[Service]
User={getpass.getuser()}
Group={getpass.getuser()}
WorkingDirectory={current_dir}/bot
ExecStart={current_dir}/backend/venv/bin/python bot.py
Restart=always
RestartSec=5
SyslogIdentifier=threexui-bot

[Install]
WantedBy=multi-user.target
"""

    # Create service files in scripts/services
    os.makedirs('scripts/services', exist_ok=True)
    
    try:
        with open('scripts/services/threexui-backend.service', 'w') as f:
            f.write(backend_service)
        
        with open('scripts/services/threexui-worker.service', 'w') as f:
            f.write(worker_service)
        
        with open('scripts/services/threexui-bot.service', 'w') as f:
            f.write(bot_service)
        
        print_success("Service files created in scripts/services/")
        print_info("To install the services, run:")
        print_info("sudo cp scripts/services/*.service /etc/systemd/system/")
        print_info("sudo systemctl daemon-reload")
        print_info("sudo systemctl enable threexui-backend threexui-worker threexui-bot")
        print_info("sudo systemctl start threexui-backend threexui-worker threexui-bot")
    except Exception as e:
        print_error(f"Failed to create service files: {str(e)}")
        return False
    
    state.services_configured = True
    return True

def installation_summary() -> None:
    """Print a summary of the installation results"""
    print_step(8, 8, "Installation summary")
    
    summary = [
        ("Prerequisites", state.prerequisites_met),
        ("Environment Configuration", state.env_configured),
        ("Backend Installation", state.backend_installed),
        ("Database Initialization", state.database_initialized),
        ("Frontend Installation", state.frontend_installed),
        ("Telegram Bot Setup", state.telegram_bot_installed),
        ("Services Configuration", state.services_configured)
    ]
    
    print(f"\n{Colors.BOLD}Installation Summary:{Colors.ENDC}")
    for name, status in summary:
        status_icon = f"{Colors.GREEN}{Emojis.SUCCESS}{Colors.ENDC}" if status else f"{Colors.RED}{Emojis.ERROR}{Colors.ENDC}"
        print(f"  {status_icon} {name}")
    
    if state.warnings:
        print(f"\n{Colors.WARNING}{Emojis.WARNING} Warnings:{Colors.ENDC}")
        for warning in state.warnings:
            print(f"  - {warning}")
    
    if state.errors:
        print(f"\n{Colors.RED}{Emojis.ERROR} Errors:{Colors.ENDC}")
        for error in state.errors:
            print(f"  - {error}")
    
    if all(status for _, status in summary):
        print(f"\n{Colors.GREEN}{Emojis.SPARKLES} Installation completed successfully! {Emojis.ROCKET}{Colors.ENDC}")
        print(f"\n{Colors.BOLD}Next steps:{Colors.ENDC}")
        print(f"  1. Start the backend: {Colors.CYAN}cd backend && venv/bin/uvicorn app.main:app --reload{Colors.ENDC}")
        print(f"  2. Start the frontend: {Colors.CYAN}cd frontend && npm start{Colors.ENDC}")
        print(f"  3. Start the Telegram bot: {Colors.CYAN}cd bot && ../backend/venv/bin/python bot.py{Colors.ENDC}")
        print(f"\n{Colors.BOLD}Backend API docs:{Colors.ENDC} http://localhost:8000/docs")
        print(f"{Colors.BOLD}Frontend:{Colors.ENDC} http://localhost:3000")
        
        state.installation_completed = True
    else:
        print(f"\n{Colors.RED}{Emojis.ERROR} Installation completed with errors. Please fix the issues and try again.{Colors.ENDC}")

def main() -> None:
    """Main installer function"""
    print_header("3X-UI Management System Installer")
    
    print(f"{Colors.CYAN}{Emojis.ROCKET} Welcome to the 3X-UI Management System installer!{Colors.ENDC}")
    print(f"{Colors.CYAN}This script will guide you through the installation process.{Colors.ENDC}")
    print(f"{Colors.CYAN}Press Ctrl+C at any time to abort.{Colors.ENDC}\n")
    
    time.sleep(1)
    
    steps = [
        check_prerequisites,
        configure_environment,
        install_backend,
        initialize_database,
        install_frontend,
        install_telegram_bot,
        configure_services,
        installation_summary
    ]
    
    # Run each step, stop if a step fails
    for step_func in steps:
        if step_func == installation_summary:
            # Always run the summary
            step_func()
        else:
            # Confirm before continuing to the next step
            if step_func != check_prerequisites:  # Don't ask for the first step
                print()
                proceed = input(f"{Colors.BLUE}{Emojis.INFO} Continue to the next step? [Y/n]: {Colors.ENDC}").strip().lower()
                if proceed == 'n':
                    print_warning("Installation aborted by user")
                    installation_summary()
                    return
            
            if not step_func():
                print_error(f"Step failed: {step_func.__name__}")
                # Continue to the summary
                installation_summary()
                return

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nInstallation aborted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n\nUnexpected error: {str(e)}")
        sys.exit(1) 