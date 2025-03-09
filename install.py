#!/usr/bin/env python3
"""
3X-UI Management System Installer
================================
This script automates the installation process for the 3X-UI Management System.
It performs prerequisite checks, sets up the environment, and installs all
necessary components for a local installation without requiring domain, SSL,
telegram bot or frontend components.

Features:
- Dynamic environment configuration input
- Step-by-step installation process
- Prerequisite checks and automatic installation
- Error handling with detailed checklist
- User-friendly output with emojis
- Python virtual environment setup
- Stateful execution - tracks what's already installed
- Shell-independent execution

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
import venv
import urllib.request
from pathlib import Path
from typing import Dict, List, Tuple, Optional, Any, Callable
import random
import socket

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
        self.venv_created = False
        self.prerequisites_installed = False
        self.env_configured = False
        self.backend_installed = False
        self.database_initialized = False
        self.services_configured = False
        self.installation_completed = False
        self.errors = []
        self.warnings = []
        
    def save_to_file(self, filepath="install_state.json"):
        """Save the installation state to a file"""
        state_dict = {
            "venv_created": self.venv_created,
            "prerequisites_installed": self.prerequisites_installed,
            "env_configured": self.env_configured,
            "backend_installed": self.backend_installed,
            "database_initialized": self.database_initialized,
            "services_configured": self.services_configured,
            "installation_completed": self.installation_completed,
            "errors": self.errors,
            "warnings": self.warnings,
            "last_update": time.strftime("%Y-%m-%d %H:%M:%S")
        }
        with open(filepath, "w") as f:
            json.dump(state_dict, f, indent=2)
            
    def load_from_file(self, filepath="install_state.json"):
        """Load the installation state from a file"""
        if os.path.exists(filepath):
            try:
                with open(filepath, "r") as f:
                    state_dict = json.load(f)
                    self.venv_created = state_dict.get("venv_created", False)
                    self.prerequisites_installed = state_dict.get("prerequisites_installed", False)
                    self.env_configured = state_dict.get("env_configured", False)
                    self.backend_installed = state_dict.get("backend_installed", False)
                    self.database_initialized = state_dict.get("database_initialized", False)
                    self.services_configured = state_dict.get("services_configured", False)
                    self.installation_completed = state_dict.get("installation_completed", False)
                    self.errors = state_dict.get("errors", [])
                    self.warnings = state_dict.get("warnings", [])
                return True
            except Exception as e:
                print(f"Error loading state file: {e}")
                return False
        return False

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
    if text not in state.errors:
        state.errors.append(text)

def print_warning(text: str) -> None:
    """Print a warning message"""
    print(f"{Colors.WARNING}{Emojis.WARNING} {text}{Colors.ENDC}")
    if text not in state.warnings:
        state.warnings.append(text)

def print_info(text: str) -> None:
    """Print an informational message"""
    print(f"{Colors.BLUE}{Emojis.INFO} {text}{Colors.ENDC}")

def get_user_input(prompt: str, default: str = "", password: bool = False) -> str:
    """
    Get input from the user with a default value
    
    Args:
        prompt: The prompt to display to the user
        default: Default value if user enters nothing
        password: Whether this is a password field (mask input)
        
    Returns:
        User input or default value
    """
    if default:
        prompt = f"{prompt} [{default}]: "
    else:
        prompt = f"{prompt}: "
        
    if password:
        value = getpass.getpass(prompt)
    else:
        value = input(prompt)
        
    return value.strip() if value.strip() else default

def get_local_ip() -> str:
    """
    Get the local IP address of the server
    
    Returns:
        String containing the local IP address
    """
    try:
        # Create a socket connection to an external server to determine the local IP
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        local_ip = s.getsockname()[0]
        s.close()
        return local_ip
    except Exception:
        # Fallback to hostname if the above method fails
        return socket.gethostbyname(socket.gethostname())

def run_command(command: List[str], error_message: str, success_message: Optional[str] = None, 
                env: Optional[Dict[str, str]] = None, shell: bool = False) -> Tuple[bool, str, str]:
    """
    Run a shell command and handle its output
    
    Args:
        command: List of command arguments or string if shell=True
        error_message: Message to display on error
        success_message: Message to display on success
        env: Environment variables to set
        shell: Whether to use shell execution
        
    Returns:
        Tuple of (success boolean, stdout, stderr)
    """
    try:
        if shell:
            if isinstance(command, list):
                cmd = " ".join(command)
            else:
                cmd = command
            
            process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                universal_newlines=True,
                env=env,
                shell=True
            )
        else:
            process = subprocess.Popen(
                command,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                universal_newlines=True,
                env=env
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

def create_virtual_environment() -> bool:
    """
    Create a Python virtual environment for the project
    
    Returns:
        Boolean indicating if venv creation was successful
    """
    if state.venv_created:
        print_success("Virtual environment already created.")
        return True
        
    print_step(1, 6, "Creating Python virtual environment")
    
    venv_path = os.path.join(os.getcwd(), "venv")
    if os.path.exists(venv_path):
        print_info("Virtual environment directory already exists. Checking if it's valid...")
        
        # Check if it's a valid venv - check for python executable
        if platform.system() == "Windows":
            python_path = os.path.join(venv_path, "Scripts", "python.exe")
        else:
            python_path = os.path.join(venv_path, "bin", "python")
            
        if os.path.exists(python_path):
            print_success("Existing virtual environment looks valid.")
            state.venv_created = True
            return True
        else:
            print_warning("Existing directory is not a valid virtual environment. Removing and recreating...")
            shutil.rmtree(venv_path)
    
    try:
        print_info("Creating virtual environment...")
        venv.create(venv_path, with_pip=True)
        
        # Verify the venv was created correctly
        if platform.system() == "Windows":
            python_path = os.path.join(venv_path, "Scripts", "python.exe")
        else:
            python_path = os.path.join(venv_path, "bin", "python")
            
        if os.path.exists(python_path):
            print_success("Virtual environment created successfully!")
            state.venv_created = True
            return True
        else:
            print_error("Failed to create virtual environment: Python executable not found in the expected location")
            return False
    except Exception as e:
        print_error(f"Failed to create virtual environment: {str(e)}")
        return False

def install_prerequisites() -> bool:
    """
    Check and install all prerequisites for the application
    
    Returns:
        Boolean indicating if all prerequisites are installed
    """
    if state.prerequisites_installed:
        print_success("Prerequisites already installed.")
        return True
        
    print_step(2, 6, "Checking and installing prerequisites")
    
    # Check operating system
    if platform.system() != "Linux":
        print_error("This installer is designed for Linux systems only")
        return False
    
    # Check for apt package manager (Ubuntu/Debian)
    if not shutil.which("apt-get"):
        print_error("This installer requires apt-get package manager (Ubuntu/Debian)")
        return False
    
    print_info("Updating package lists...")
    run_command(["sudo", "apt-get", "update"], "Failed to update package lists")
    
    # Define required packages with their apt package names
    required_packages = {
        "python3": "python3",
        "python3-pip": "python3-pip",
        "python3-venv": "python3-venv",
        "postgresql": "postgresql",
        "postgresql-contrib": "postgresql-contrib",
        "libpq-dev": "libpq-dev",
        "redis-server": "redis-server",
        "nginx": "nginx",
        "build-essential": "build-essential",
    }
    
    # Install all packages at once to be more efficient
    packages_to_install = []
    for package_name, apt_name in required_packages.items():
        print_info(f"Checking {package_name}...")
        success, _, _ = run_command(["dpkg", "-s", apt_name], f"Checking {package_name}", shell=False)
        
        if not success:
            packages_to_install.append(apt_name)
    
    if packages_to_install:
        print_info(f"Installing packages: {', '.join(packages_to_install)}")
        install_cmd = ["sudo", "apt-get", "install", "-y"] + packages_to_install
        success, _, _ = run_command(
            install_cmd,
            "Failed to install required packages",
            "Packages installed successfully!"
        )
        if not success:
            print_error("Failed to install required packages. Installation may be incomplete.")
            return False
    else:
        print_success("All required packages are already installed.")
    
    # Start and enable PostgreSQL and Redis services
    for service in ["postgresql", "redis-server"]:
        print_info(f"Ensuring {service} is running...")
        run_command(
            ["sudo", "systemctl", "start", service],
            f"Failed to start {service}"
        )
        run_command(
            ["sudo", "systemctl", "enable", service],
            f"Failed to enable {service}"
        )
    
    print_success("All prerequisites installed successfully!")
    state.prerequisites_installed = True
    return True

def configure_environment() -> bool:
    """
    Configure environment variables for the application
    
    Returns:
        Boolean indicating if configuration was successful
    """
    if state.env_configured:
        print_success("Environment already configured.")
        return True
        
    print_step(3, 6, "Configuring environment")
    
    # Get server's local IP address
    server_ip = get_local_ip()
    print_info(f"Detected server IP address: {server_ip}")
    
    # Get PostgreSQL credentials
    pg_user = get_user_input("PostgreSQL username", "postgres")
    pg_password = get_user_input("PostgreSQL password", "postgres", password=True)
    pg_db = get_user_input("PostgreSQL database name", "threexui")
    
    # Generate a secure random secret key
    secret_key = "".join(random.choice("abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789") for _ in range(64))
    
    # Backend environment variables
    backend_env = {
        "DATABASE_URL": f"postgresql://{pg_user}:{pg_password}@localhost/{pg_db}",
        "REDIS_URL": "redis://localhost:6379/0",
        "SECRET_KEY": secret_key,
        "ACCESS_TOKEN_EXPIRE_MINUTES": "30",
        "REFRESH_TOKEN_EXPIRE_DAYS": "7",
        "ALGORITHM": "HS256",
        "BACKEND_CORS_ORIGINS": f'["http://{server_ip}:3000", "http://localhost:3000", "http://localhost:8080"]',
        "SMTP_SERVER": "",
        "SMTP_PORT": "587",
        "SMTP_USERNAME": "",
        "SMTP_PASSWORD": "",
        "SMTP_FROM": "noreply@example.com",
        "ENVIRONMENT": "development",
        "SERVER_IP": server_ip,
        "USE_SSL": "false",
        "ENABLE_BOT": "false",
        "ENABLE_FRONTEND": "false"
    }
    
    # Create .env file for backend
    env_file_path = os.path.join(os.getcwd(), ".env")
    try:
        with open(env_file_path, "w") as f:
            for key, value in backend_env.items():
                f.write(f"{key}={value}\n")
        print_success("Environment file (.env) created successfully!")
        
        # Create a copy in the backend directory if it exists
        backend_dir = os.path.join(os.getcwd(), "backend")
        if os.path.exists(backend_dir):
            backend_env_path = os.path.join(backend_dir, ".env")
            shutil.copy(env_file_path, backend_env_path)
            print_success("Environment file copied to backend directory.")
        
        state.env_configured = True
        return True
    except Exception as e:
        print_error(f"Failed to create environment file: {str(e)}")
        return False

def install_backend() -> bool:
    """
    Install and configure the backend application
    
    Returns:
        Boolean indicating if backend installation was successful
    """
    if state.backend_installed:
        print_success("Backend already installed.")
        return True
        
    print_step(4, 6, "Installing backend")
    
    backend_dir = os.path.join(os.getcwd(), "backend")
    if not os.path.exists(backend_dir):
        print_error("Backend directory not found. Please ensure the repository is properly cloned.")
        return False
    
    # Get paths to Python and pip executables in the virtual environment
    venv_path = os.path.join(os.getcwd(), "venv")
    if platform.system() == "Windows":
        python_bin = os.path.join(venv_path, "Scripts", "python.exe")
        pip_bin = os.path.join(venv_path, "Scripts", "pip.exe")
    else:
        python_bin = os.path.join(venv_path, "bin", "python")
        pip_bin = os.path.join(venv_path, "bin", "pip")
    
    # Verify Python and pip executables exist
    if not os.path.exists(python_bin):
        print_error(f"Python executable not found at {python_bin}. Virtual environment may be corrupted.")
        return False
    
    if not os.path.exists(pip_bin):
        print_error(f"Pip executable not found at {pip_bin}. Virtual environment may be corrupted.")
        return False
    
    # Check for requirements.txt
    requirements_path = os.path.join(backend_dir, "requirements.txt")
    if not os.path.exists(requirements_path):
        print_error("requirements.txt not found in backend directory.")
        return False
    
    # Install dependencies using direct paths to Python and pip in the virtual environment
    print_info("Installing backend dependencies...")
    cmd = f"{python_bin} -m pip install -r {requirements_path}"
    success, stdout, stderr = run_command(
        cmd,
        "Failed to install backend dependencies",
        "Backend dependencies installed successfully!",
        shell=True
    )
    
    if not success:
        print_error(f"Failed to install backend dependencies: {stderr}")
        return False
    
    state.backend_installed = True
    return True

def initialize_database() -> bool:
    """
    Initialize the database for the application
    
    Returns:
        Boolean indicating if database initialization was successful
    """
    if state.database_initialized:
        print_success("Database already initialized.")
        return True
        
    print_step(5, 6, "Initializing database")
    
    # Get PostgreSQL credentials from .env file
    env_file_path = os.path.join(os.getcwd(), ".env")
    if not os.path.exists(env_file_path):
        print_error("Environment file (.env) not found. Please run configuration step first.")
        return False
    
    env_vars = {}
    with open(env_file_path, "r") as f:
        for line in f:
            if "=" in line:
                key, value = line.strip().split("=", 1)
                env_vars[key] = value
    
    database_url = env_vars.get("DATABASE_URL", "")
    if not database_url:
        print_error("DATABASE_URL not found in .env file.")
        return False
    
    # Parse database connection parameters
    match = re.match(r"postgresql://([^:]+):([^@]+)@([^/]+)/(.+)", database_url)
    if not match:
        print_error(f"Failed to parse DATABASE_URL: {database_url}")
        return False
    
    pg_user, pg_password, pg_host, pg_db = match.groups()
    
    # First create the PostgreSQL user if it doesn't exist
    print_info(f"Ensuring PostgreSQL user '{pg_user}' exists...")
    create_user_cmd = f"sudo -u postgres psql -c \"SELECT 1 FROM pg_roles WHERE rolname='{pg_user}'\" | grep -q 1 || sudo -u postgres psql -c \"CREATE USER {pg_user} WITH PASSWORD '{pg_password}' CREATEDB;\""
    success, _, _ = run_command(
        create_user_cmd,
        f"Failed to create PostgreSQL user '{pg_user}'",
        f"PostgreSQL user '{pg_user}' is ready",
        shell=True
    )
    
    if not success:
        return False
    
    # Check if database exists, create if not
    print_info(f"Checking if database '{pg_db}' exists...")
    
    # Use a simpler, more reliable approach to check and create database
    check_db_cmd = f"sudo -u postgres psql -lqt | cut -d \\| -f 1 | grep -qw {pg_db}"
    db_exists, _, _ = run_command(check_db_cmd, "Failed to check database", shell=True)
    
    if not db_exists:
        print_info(f"Creating database '{pg_db}'...")
        # Create database directly as postgres user, avoiding directory permission issues
        create_db_cmd = f"sudo -u postgres psql -c \"CREATE DATABASE {pg_db} OWNER {pg_user};\""
        success, _, _ = run_command(
            create_db_cmd,
            f"Failed to create database '{pg_db}'",
            f"Database '{pg_db}' created successfully!",
            shell=True
        )
        
        if not success:
            return False
    else:
        print_success(f"Database '{pg_db}' already exists.")
    
    # Run database migrations
    backend_dir = os.path.join(os.getcwd(), "backend")
    if not os.path.exists(backend_dir):
        print_error("Backend directory not found.")
        return False
    
    # Get path to Python in virtual environment
    venv_path = os.path.join(os.getcwd(), "venv")
    if platform.system() == "Windows":
        python_bin = os.path.join(venv_path, "Scripts", "python.exe")
    else:
        python_bin = os.path.join(venv_path, "bin", "python")
    
    print_info("Running database migrations...")
    
    # Check if there's an alembic.ini file or a migrations script
    alembic_ini = os.path.join(backend_dir, "alembic.ini")
    migrations_script = os.path.join(backend_dir, "migrations.py")
    
    if os.path.exists(alembic_ini):
        cmd = f"cd {backend_dir} && {python_bin} -m alembic upgrade head"
        success, _, _ = run_command(
            cmd,
            "Failed to run database migrations",
            "Database migrations completed successfully!",
            shell=True
        )
    elif os.path.exists(migrations_script):
        cmd = f"cd {backend_dir} && {python_bin} migrations.py"
        success, _, _ = run_command(
            cmd,
            "Failed to run database migrations",
            "Database migrations completed successfully!",
            shell=True
        )
    else:
        print_warning("No migration files found. Skipping database migration step.")
        success = True
    
    if not success:
        return False
    
    state.database_initialized = True
    return True

def configure_services() -> bool:
    """
    Configure system services for the application
    
    Returns:
        Boolean indicating if service configuration was successful
    """
    if state.services_configured:
        print_success("Services already configured.")
        return True
        
    print_step(6, 6, "Configuring services")
    
    # Get the current username and project path
    current_user = getpass.getuser()
    project_path = os.getcwd()
    venv_path = os.path.join(project_path, "venv")
    
    # Get path to Python and uvicorn in virtual environment
    if platform.system() == "Windows":
        python_bin = os.path.join(venv_path, "Scripts", "python.exe")
        uvicorn_bin = os.path.join(venv_path, "Scripts", "uvicorn.exe")
    else:
        python_bin = os.path.join(venv_path, "bin", "python")
        uvicorn_bin = os.path.join(venv_path, "bin", "uvicorn")
    
    # Create systemd service file for backend
    backend_service = f"""[Unit]
Description=3X-UI Backend Service
After=network.target postgresql.service redis-server.service

[Service]
User={current_user}
Group={current_user}
WorkingDirectory={os.path.join(project_path, "backend")}
Environment="PATH={os.path.dirname(python_bin)}:$PATH"
ExecStart={uvicorn_bin} app.main:app --host 0.0.0.0 --port 8000

[Install]
WantedBy=multi-user.target
"""
    
    # Configure Nginx for backend
    server_ip = get_local_ip()
    nginx_config = f"""server {{
    listen 80;
    server_name {server_ip};

    location /api {{
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }}

    location /api/docs {{
        proxy_pass http://127.0.0.1:8000/docs;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }}
}}
"""
    
    # Write service files
    try:
        # Backend service
        backend_service_path = "/tmp/3xui-backend.service"
        with open(backend_service_path, "w") as f:
            f.write(backend_service)
        
        print_info("Installing backend service...")
        success, _, _ = run_command(
            ["sudo", "mv", backend_service_path, "/etc/systemd/system/3xui-backend.service"],
            "Failed to install backend service"
        )
        
        if not success:
            return False
        
        # Nginx config
        nginx_config_path = "/tmp/3xui.conf"
        with open(nginx_config_path, "w") as f:
            f.write(nginx_config)
        
        print_info("Installing Nginx configuration...")
        success, _, _ = run_command(
            ["sudo", "mv", nginx_config_path, "/etc/nginx/sites-available/3xui.conf"],
            "Failed to install Nginx configuration"
        )
        
        if not success:
            return False
        
        # Enable Nginx site
        if not os.path.exists("/etc/nginx/sites-enabled/3xui.conf"):
            success, _, _ = run_command(
                ["sudo", "ln", "-s", "/etc/nginx/sites-available/3xui.conf", "/etc/nginx/sites-enabled/"],
                "Failed to enable Nginx site"
            )
            
            if not success:
                return False
        
        # Reload systemd and enable services
        print_info("Reloading systemd daemon...")
        run_command(
            ["sudo", "systemctl", "daemon-reload"],
            "Failed to reload systemd daemon"
        )
        
        print_info("Enabling backend service...")
        run_command(
            ["sudo", "systemctl", "enable", "3xui-backend.service"],
            "Failed to enable backend service"
        )
        
        print_info("Restarting Nginx...")
        run_command(
            ["sudo", "systemctl", "reload", "nginx"],
            "Failed to restart Nginx"
        )
        
        print_info("Starting backend service...")
        run_command(
            ["sudo", "systemctl", "start", "3xui-backend.service"],
            "Failed to start backend service"
        )
        
        state.services_configured = True
        print_success("Services configured successfully!")
        return True
    except Exception as e:
        print_error(f"Failed to configure services: {str(e)}")
        return False

def installation_summary() -> None:
    """Display a summary of the installation status"""
    print_header("3X-UI Installation Summary")
    
    steps = [
        ("Virtual Environment Setup", state.venv_created),
        ("Prerequisites Installation", state.prerequisites_installed),
        ("Environment Configuration", state.env_configured),
        ("Backend Installation", state.backend_installed),
        ("Database Initialization", state.database_initialized),
        ("Services Configuration", state.services_configured)
    ]
    
    all_completed = True
    for step_name, completed in steps:
        status = f"{Colors.GREEN}{Emojis.SUCCESS} Completed{Colors.ENDC}" if completed else f"{Colors.RED}{Emojis.CROSS} Pending{Colors.ENDC}"
        print(f"{step_name}: {status}")
        all_completed = all_completed and completed
    
    if all_completed:
        server_ip = get_local_ip()
        print_header("Installation Completed Successfully!")
        print_success(f"The 3X-UI Management System has been installed in local mode.")
        print_info(f"Backend API is accessible at: http://{server_ip}/api")
        print_info(f"API Documentation is accessible at: http://{server_ip}/api/docs")
        print_info("To manage the backend service:")
        print(f"  - Start: {Colors.CYAN}sudo systemctl start 3xui-backend.service{Colors.ENDC}")
        print(f"  - Stop: {Colors.CYAN}sudo systemctl stop 3xui-backend.service{Colors.ENDC}")
        print(f"  - Restart: {Colors.CYAN}sudo systemctl restart 3xui-backend.service{Colors.ENDC}")
        print(f"  - Status: {Colors.CYAN}sudo systemctl status 3xui-backend.service{Colors.ENDC}")
        
        if state.warnings:
            print_header("Warnings")
            for warning in state.warnings:
                print_warning(warning)
    else:
        print_header("Installation Incomplete")
        print_info("Some installation steps are pending. Run the script again to continue installation.")
        
        if state.errors:
            print_header("Errors")
            for error in state.errors:
                print_error(error)

def main() -> None:
    """Main installation function"""
    print_header("3X-UI Management System Local Installer")
    
    # Load previous state if available
    state.load_from_file()
    
    # Installation steps
    steps = [
        create_virtual_environment,
        install_prerequisites,
        configure_environment,
        install_backend,
        initialize_database,
        configure_services
    ]
    
    # Run installation steps
    try:
        for step_function in steps:
            if not step_function():
                print_error("Installation failed at step: " + step_function.__name__)
                break
            # Save state after each successful step
            state.save_to_file()
    except KeyboardInterrupt:
        print_warning("\nInstallation interrupted by user. Progress has been saved.")
    except Exception as e:
        print_error(f"An unexpected error occurred: {str(e)}")
    
    # Display installation summary
    installation_summary()
    
    # Mark installation as completed if all steps were successful
    if (state.venv_created and state.prerequisites_installed and state.env_configured and 
        state.backend_installed and state.database_initialized and state.services_configured):
        state.installation_completed = True
        state.save_to_file()

if __name__ == "__main__":
    main() 