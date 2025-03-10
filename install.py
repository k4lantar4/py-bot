#!/usr/bin/env python3
"""
3X-UI Management System Installer
================================
This script automates the installation process for the 3X-UI Management System.
It performs prerequisite checks, sets up the environment, and installs all
necessary components including backend, frontend, MySQL database, and phpMyAdmin.

Features:
- Dynamic environment configuration input
- Step-by-step installation process
- Prerequisite checks and automatic installation
- Error handling with detailed checklist
- User-friendly output with emojis
- Python virtual environment setup
- MySQL database setup with phpMyAdmin
- Frontend installation
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
        self.mysql_installed = False
        self.phpmyadmin_installed = False
        self.database_initialized = False
        self.frontend_installed = False
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
            "mysql_installed": self.mysql_installed,
            "phpmyadmin_installed": self.phpmyadmin_installed,
            "database_initialized": self.database_initialized,
            "frontend_installed": self.frontend_installed,
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
                    self.mysql_installed = state_dict.get("mysql_installed", False)
                    self.phpmyadmin_installed = state_dict.get("phpmyadmin_installed", False)
                    self.database_initialized = state_dict.get("database_initialized", False)
                    self.frontend_installed = state_dict.get("frontend_installed", False)
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
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        local_ip = s.getsockname()[0]
        s.close()
        return local_ip
    except Exception:
        return socket.gethostbyname(socket.gethostname())

def run_command(command: List[str], error_message: str, success_message: Optional[str] = None, 
                env: Optional[Dict[str, str]] = None, shell: bool = False, input_data: Optional[bytes] = None) -> Tuple[bool, str, str]:
    """
    Run a shell command and handle its output
    
    Args:
        command: List of command arguments or string if shell=True
        error_message: Message to display on error
        success_message: Message to display on success
        env: Environment variables to set
        shell: Whether to use shell execution
        input_data: Optional input data to pass to the command
        
    Returns:
        Tuple of (success boolean, stdout, stderr)
    """
    try:
        # Prepare environment
        current_env = os.environ.copy()
        if env:
            current_env.update(env)
        
        # Handle shell commands
        if shell:
            if isinstance(command, list):
                cmd = " ".join(command)
            else:
                cmd = command
        else:
            cmd = command

        # Create process
        process = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            stdin=subprocess.PIPE if input_data else None,
            env=current_env,
            shell=shell,
            text=True
        )

        try:
            # Run command with timeout
            stdout, stderr = process.communicate(
                input=input_data.decode() if input_data else None,
                timeout=300  # 5 minute timeout
            )
        except subprocess.TimeoutExpired:
            process.kill()
            print_error(f"{error_message}: Command timed out after 5 minutes")
            return False, "", "Command timed out"

        # Check return code
        if process.returncode != 0:
            # Special handling for package manager errors
            if "apt-get" in str(cmd) and ("Could not get lock" in stderr or "Could not open lock file" in stderr):
                print_warning("Package manager is locked. Waiting for other processes to finish...")
                time.sleep(10)  # Wait 10 seconds
                return run_command(command, error_message, success_message, env, shell, input_data)
            
            # Handle common errors
            if "Could not resolve host" in stderr:
                print_error(f"{error_message}: Network connection issue. Please check your internet connection.")
            elif "Permission denied" in stderr:
                print_error(f"{error_message}: Permission denied. Make sure you have the right permissions.")
            else:
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
        
    print_step(1, 8, "Creating Python virtual environment")
    
    # Install Python venv package if not already installed
    print_info("Ensuring Python venv package is installed...")
    run_command(
        ["sudo", "apt-get", "install", "-y", "python3-venv"],
        "Failed to install python3-venv"
    )
    
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
        # Use system Python to create venv
        success, _, _ = run_command(
            ["python3", "-m", "venv", venv_path],
            "Failed to create virtual environment"
        )
        
        if not success:
            return False
        
        # Verify the venv was created correctly
        if platform.system() == "Windows":
            python_path = os.path.join(venv_path, "Scripts", "python.exe")
        else:
            python_path = os.path.join(venv_path, "bin", "python")
            
        if os.path.exists(python_path):
            # Upgrade pip in the virtual environment
            upgrade_cmd = f"{python_path} -m pip install --upgrade pip"
            run_command(upgrade_cmd, "Failed to upgrade pip", shell=True)
            
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
        
    print_step(2, 8, "Checking and installing prerequisites")
    
    # Check operating system
    if platform.system() != "Linux":
        print_error("This installer is designed for Linux systems only")
        return False
    
    # Check for apt package manager (Ubuntu/Debian)
    if not shutil.which("apt-get"):
        print_error("This installer requires apt-get package manager (Ubuntu/Debian)")
        return False
    
    # Wait for any existing apt processes to finish
    print_info("Checking for existing package manager processes...")
    while True:
        success, _, _ = run_command(
            "! pgrep -a apt-get && ! pgrep -a dpkg",
            "Checking package manager locks",
            shell=True
        )
        if success:
            break
        print_warning("Waiting for other package manager processes to finish...")
        time.sleep(5)
    
    # Fix any broken packages and clean up
    print_info("Fixing package manager state...")
    commands = [
        ["sudo", "dpkg", "--configure", "-a"],
        ["sudo", "apt-get", "clean"],
        ["sudo", "apt-get", "autoclean"],
        ["sudo", "apt-get", "update"],
        ["sudo", "apt-get", "install", "-f", "-y"]
    ]
    
    for cmd in commands:
        success, _, _ = run_command(cmd, f"Failed to run {' '.join(cmd)}")
        if not success:
            print_warning(f"Failed to run {' '.join(cmd)}. Continuing anyway...")

    # Add PHP repository
    print_info("Adding PHP repository...")
    php_commands = [
        ["sudo", "apt-get", "install", "-y", "software-properties-common"],
        ["sudo", "add-apt-repository", "-y", "ppa:ondrej/php"],
        ["sudo", "apt-get", "update"]
    ]
    
    for cmd in php_commands:
        success, _, _ = run_command(cmd, f"Failed to add PHP repository")
        if not success:
            print_warning(f"Failed to run {' '.join(cmd)}. Continuing anyway...")
    
    # Define required packages with their apt package names
    required_packages = {
        # Python packages
        "python3": "python3",
        "python3-pip": "python3-pip",
        "python3-venv": "python3-venv",
        "python3-dev": "python3-dev",
        
        # Web server packages
        "nginx": "nginx",
        "apache2": "apache2",
        
        # PHP and its extensions
        "php8.2": "php8.2",
        "php8.2-fpm": "php8.2-fpm",
        "php8.2-mysql": "php8.2-mysql",
        "php8.2-mbstring": "php8.2-mbstring",
        "php8.2-zip": "php8.2-zip",
        "php8.2-gd": "php8.2-gd",
        "php8.2-xml": "php8.2-xml",
        "php8.2-curl": "php8.2-curl",
        "libapache2-mod-php8.2": "libapache2-mod-php8.2",
        
        # MySQL packages
        "mysql-server": "mysql-server",
        "mysql-client": "mysql-client",
        "libmysqlclient-dev": "libmysqlclient-dev",
        
        # Build tools and utilities
        "build-essential": "build-essential",
        "curl": "curl",
        "gnupg": "gnupg",
        "ca-certificates": "ca-certificates",
        "software-properties-common": "software-properties-common",
        "git": "git"
    }
    
    # Install base packages first
    print_info("Installing base packages...")
    for package_name, apt_name in required_packages.items():
        print_info(f"Installing {package_name}...")
        success, _, _ = run_command(
            ["sudo", "apt-get", "install", "-y", "--no-install-recommends", apt_name],
            f"Failed to install {package_name}"
        )
        if not success:
            print_warning(f"Failed to install {package_name}. Continuing anyway...")
            
        # Special handling for PHP 8.2
        if apt_name.startswith("php8.2"):
            run_command(
                ["sudo", "update-alternatives", "--install", "/usr/bin/php", "php", f"/usr/bin/php8.2", "1"],
                f"Failed to set PHP alternative for {apt_name}"
            )
    
    # Install Node.js
    print_info("Setting up Node.js...")
    
    # Remove old nodejs if exists
    run_command(["sudo", "apt-get", "remove", "-y", "nodejs", "npm"], "Removing old Node.js")
    
    # Add NodeSource repository using the new method
    print_info("Adding Node.js repository...")
    
    # Create keyrings directory
    run_command(["sudo", "mkdir", "-p", "/etc/apt/keyrings"], "Creating keyrings directory")
    
    # Download and add GPG key
    curl_cmd = "curl -fsSL https://deb.nodesource.com/gpgkey/nodesource-repo.gpg.key | sudo gpg --dearmor -o /etc/apt/keyrings/nodesource.gpg"
    success, _, _ = run_command(curl_cmd, "Failed to add Node.js GPG key", shell=True)
    
    if success:
        # Add repository
        echo_cmd = 'echo "deb [signed-by=/etc/apt/keyrings/nodesource.gpg] https://deb.nodesource.com/node_20.x nodistro main" | sudo tee /etc/apt/sources.list.d/nodesource.list'
        run_command(echo_cmd, "Failed to add Node.js repository", shell=True)
        
        # Update and install Node.js
        run_command(["sudo", "apt-get", "update"], "Failed to update package lists")
        success, _, _ = run_command(["sudo", "apt-get", "install", "-y", "nodejs"], "Failed to install Node.js")
        
        if not success:
            print_error("Failed to install Node.js through repository. Please install manually:")
            print("1. curl -fsSL https://deb.nodesource.com/setup_20.x | sudo -E bash -")
            print("2. sudo apt-get install -y nodejs")
            return False
    
    # Configure PHP and Apache
    print_info("Configuring PHP and Apache...")
    apache_commands = [
        ["sudo", "a2dismod", "mpm_event"],
        ["sudo", "a2enmod", "mpm_prefork"],
        ["sudo", "a2enmod", "php8.2"],
        ["sudo", "a2enmod", "rewrite"],
        ["sudo", "phpenmod", "mbstring"],
        ["sudo", "systemctl", "restart", "apache2"]
    ]
    
    for cmd in apache_commands:
        success, _, _ = run_command(cmd, f"Failed to run {' '.join(cmd)}")
        if not success:
            print_warning(f"Failed to run {' '.join(cmd)}. Continuing anyway...")
    
    # Create Nginx directories if they don't exist
    nginx_dirs = [
        "/etc/nginx",
        "/etc/nginx/sites-available",
        "/etc/nginx/sites-enabled",
        "/var/log/nginx"
    ]
    
    for directory in nginx_dirs:
        run_command(["sudo", "mkdir", "-p", directory], f"Creating {directory}")
    
    # Verify installations
    verifications = [
        (["python3", "--version"], "Python"),
        (["node", "--version"], "Node.js"),
        (["npm", "--version"], "npm"),
        (["nginx", "-v"], "Nginx"),
        (["apache2", "-v"], "Apache2"),
        (["php8.2", "-v"], "PHP"),
        (["mysql", "--version"], "MySQL")
    ]
    
    print_info("Verifying installations...")
    for cmd, name in verifications:
        success, version, _ = run_command(cmd, f"Checking {name} version")
        if success:
            print_success(f"{name} {version.strip()} installed successfully!")
        else:
            print_warning(f"{name} verification failed, but continuing...")
    
    state.prerequisites_installed = True
    return True

def install_mysql() -> bool:
    """
    Install and configure MySQL server
    
    Returns:
        Boolean indicating if MySQL installation was successful
    """
    if state.mysql_installed:
        print_success("MySQL already installed.")
        return True
        
    print_step(4, 8, "Installing MySQL")
    
    # Set a default MySQL root password
    mysql_root_password = os.environ.get("MYSQL_ROOT_PASSWORD", "")
    if not mysql_root_password:
        mysql_root_password = get_user_input("Enter a password for MySQL root user", password=True)
        while not mysql_root_password:
            print_warning("Password cannot be empty!")
            mysql_root_password = get_user_input("Enter a password for MySQL root user", password=True)
        
        # Confirm password
        confirm_password = get_user_input("Confirm MySQL root password", password=True)
        while mysql_root_password != confirm_password:
            print_warning("Passwords do not match!")
            mysql_root_password = get_user_input("Enter a password for MySQL root user", password=True)
            confirm_password = get_user_input("Confirm MySQL root password", password=True)
    
    # Set environment variable for non-interactive installation
    os.environ["DEBIAN_FRONTEND"] = "noninteractive"
    
    # Prepare MySQL installation with preset root password
    print_info("Preparing MySQL installation...")
    debconf_settings = [
        f"mysql-server mysql-server/root_password password {mysql_root_password}",
        f"mysql-server mysql-server/root_password_again password {mysql_root_password}"
    ]
    
    for setting in debconf_settings:
        success, stdout, stderr = run_command(
            ["sudo", "debconf-set-selections"],
            "Failed to configure MySQL",
            input_data=setting.encode()
        )
        if not success:
            print_error(f"Failed to set MySQL configuration: {stderr}")
            return False
    
    # Install MySQL
    print_info("Installing MySQL server...")
    success, stdout, stderr = run_command(
        ["sudo", "apt-get", "install", "-y", "mysql-server"],
        "Failed to install MySQL",
        "MySQL installed successfully!"
    )
    
    if not success:
        print_error(f"Failed to install MySQL: {stderr}")
        return False
    
    # Start MySQL service
    print_info("Starting MySQL service...")
    success, stdout, stderr = run_command(
        ["sudo", "systemctl", "start", "mysql"],
        "Failed to start MySQL service",
        "MySQL service started successfully!"
    )
    
    if not success:
        print_error(f"Failed to start MySQL service: {stderr}")
        return False
    
    # Enable MySQL service to start on boot
    print_info("Enabling MySQL service to start on boot...")
    success, stdout, stderr = run_command(
        ["sudo", "systemctl", "enable", "mysql"],
        "Failed to enable MySQL service",
        "MySQL service enabled successfully!"
    )
    
    if not success:
        print_error(f"Failed to enable MySQL service: {stderr}")
        return False
    
    # Secure MySQL installation
    print_info("Securing MySQL installation...")
    
    # Check if MySQL is accessible without password (default in some installations)
    no_password_access = False
    password_check_cmd = ["mysql", "-u", "root", "-e", "SELECT 1"]
    password_check_success, _, _ = run_command(
        password_check_cmd, 
        "Testing MySQL root access without password", 
        "MySQL root has no password",
        shell=False
    )
    
    if password_check_success:
        no_password_access = True
        print_warning("MySQL root user has no password. Setting up password...")
    
    # Create secure MySQL script
    mysql_secure_script = """
    ALTER USER 'root'@'localhost' IDENTIFIED WITH mysql_native_password BY '{mysql_root_password}';
    DELETE FROM mysql.user WHERE User='';
    DELETE FROM mysql.user WHERE User='root' AND Host NOT IN ('localhost', '127.0.0.1', '::1');
    DROP DATABASE IF EXISTS test;
    DELETE FROM mysql.db WHERE Db='test' OR Db='test\\_%';
    FLUSH PRIVILEGES;
    """.format(mysql_root_password=mysql_root_password)
    
    # Write script to temporary file
    script_path = "/tmp/mysql_secure.sql"
    try:
        with open(script_path, "w") as f:
            f.write(mysql_secure_script)
    except Exception as e:
        print_error(f"Failed to create MySQL secure script: {str(e)}")
        return False
        
    # Execute script based on current authentication state
    if no_password_access:
        # No password set yet
        secure_cmd = f"sudo mysql < {script_path}"
        success, stdout, stderr = run_command(
            secure_cmd,
            "Failed to secure MySQL installation",
            "MySQL installation secured successfully!",
            shell=True
        )
    else:
        # Password already set
        secure_cmd = f"sudo mysql -u root -p'{mysql_root_password}' < {script_path}"
        success, stdout, stderr = run_command(
            secure_cmd,
            "Failed to secure MySQL installation",
            "MySQL installation secured successfully!",
            shell=True
        )
    
    # Remove temporary script file
    try:
        os.remove(script_path)
    except:
        pass
        
    if not success:
        print_warning(f"Failed to fully secure MySQL installation: {stderr}")
        print_warning("MySQL is installed but may not be properly secured.")
        # Continue anyway since MySQL is installed
    
    # Verify MySQL is working properly with the new password
    print_info("Verifying MySQL installation...")
    test_cmd = f"mysql -u root -p'{mysql_root_password}' -e 'SELECT VERSION()'"
    success, stdout, stderr = run_command(
        test_cmd,
        "Failed to verify MySQL installation",
        "MySQL is working properly!",
        shell=True
    )
    
    if not success:
        print_warning(f"Failed to verify MySQL installation: {stderr}")
        print_warning("MySQL is installed but may not be working properly.")
        # Continue anyway
    
    # Save MySQL password to environment for later use
    os.environ["MYSQL_ROOT_PASSWORD"] = mysql_root_password
    
    state.mysql_installed = True
    return True

def install_phpmyadmin() -> bool:
    """
    Install and configure phpMyAdmin
    
    Returns:
        Boolean indicating if phpMyAdmin installation was successful
    """
    if state.phpmyadmin_installed:
        print_success("phpMyAdmin already installed.")
        return True
        
    print_step(5, 8, "Installing phpMyAdmin")
    
    # Install phpMyAdmin package
    print_info("Installing phpMyAdmin...")
    
    # Debian/Ubuntu
    if platform.system() == "Linux" and os.path.exists("/etc/debian_version"):
        phpmyadmin_success, phpmyadmin_stdout, phpmyadmin_stderr = run_command(
            ["sudo", "apt-get", "install", "-y", "phpmyadmin"],
            "Failed to install phpMyAdmin",
            "phpMyAdmin installed successfully!",
            input_data=b"\n1\n\n\n"  # Automatically select Apache2 and say no to dbconfig-common
        )
        
        if not phpmyadmin_success:
            print_error(f"Failed to install phpMyAdmin: {phpmyadmin_stderr}")
            return False
            
        # Configure phpMyAdmin to work with Apache
        print_info("Configuring phpMyAdmin for Apache...")
        
        # Ensure the Apache configuration includes phpMyAdmin config
        apache_conf_file = "/etc/apache2/apache2.conf"
        phpmyadmin_include = "Include /etc/phpmyadmin/apache.conf"
        
        # Check if phpMyAdmin is already included in Apache config
        grep_success, grep_stdout, grep_stderr = run_command(
            ["grep", "-q", phpmyadmin_include, apache_conf_file],
            "Failed to check Apache configuration",
            shell=False
        )
        
        # If not included, add it
        if not grep_success:
            append_success, append_stdout, append_stderr = run_command(
                ["sudo", "bash", "-c", f'echo "{phpmyadmin_include}" >> {apache_conf_file}'],
                "Failed to update Apache configuration",
                "Apache configuration updated successfully!",
                shell=False
            )
            
            if not append_success:
                print_error(f"Failed to update Apache configuration: {append_stderr}")
                return False
                
        # Restart Apache with better error handling
        print_info("Restarting Apache service...")
        restart_success, restart_stdout, restart_stderr = run_command(
            ["sudo", "systemctl", "restart", "apache2"],
            "Failed to restart Apache service",
            "Apache service restarted successfully!",
            shell=False
        )
        
        if not restart_success:
            print_error(f"Failed to restart Apache service: {restart_stderr}")
            print_warning("Checking Apache configuration...")
            
            # Check Apache config
            apache_check_success, apache_check_stdout, apache_check_stderr = run_command(
                ["sudo", "apachectl", "configtest"],
                "Failed to check Apache configuration",
                shell=False
            )
            
            if not apache_check_success:
                print_error(f"Apache configuration error: {apache_check_stderr}")
                
                # Try to fix common configuration issues
                print_info("Attempting to fix Apache configuration...")
                
                # Enable required modules
                run_command(
                    ["sudo", "a2enmod", "rewrite"],
                    "Failed to enable rewrite module",
                    "Rewrite module enabled successfully!",
                    shell=False
                )
                
                run_command(
                    ["sudo", "a2enmod", "ssl"],
                    "Failed to enable SSL module",
                    "SSL module enabled successfully!",
                    shell=False
                )
                
                # Try restart again
                print_info("Trying to restart Apache again...")
                restart_again_success, restart_again_stdout, restart_again_stderr = run_command(
                    ["sudo", "systemctl", "restart", "apache2"],
                    "Failed to restart Apache service",
                    "Apache service restarted successfully!",
                    shell=False
                )
                
                if not restart_again_success:
                    print_warning("Apache could not be restarted. You may need to fix the configuration manually.")
                    print_info("Check '/var/log/apache2/error.log' for more details.")
                    # Continue with installation anyway
            else:
                print_info(f"Apache configuration seems correct, but service failed to restart: {restart_stderr}")
                print_info("Check '/var/log/apache2/error.log' for more details.")
                # Continue with installation anyway
    
    state.phpmyadmin_installed = True
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
        
    print_step(5, 8, "Configuring environment")
    
    # Get server's local IP address
    server_ip = get_local_ip()
    print_info(f"Detected server IP address: {server_ip}")
    
    # Get MySQL credentials
    mysql_user = get_user_input("MySQL username", "threexui_user")
    mysql_password = get_user_input("MySQL password", "threexui_pass", password=True)
    mysql_db = get_user_input("MySQL database name", "threexui")
    
    # Generate a secure random secret key
    secret_key = "".join(random.choice("abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789") for _ in range(64))
    
    # Backend environment variables
    backend_env = {
        "DATABASE_URL": f"mysql+pymysql://{mysql_user}:{mysql_password}@localhost/{mysql_db}",
        "REDIS_URL": "redis://localhost:6379/0",
        "SECRET_KEY": secret_key,
        "ACCESS_TOKEN_EXPIRE_MINUTES": "30",
        "REFRESH_TOKEN_EXPIRE_DAYS": "7",
        "ALGORITHM": "HS256",
        "BACKEND_CORS_ORIGINS": f'["http://{server_ip}", "http://{server_ip}:3000", "http://localhost:3000"]',
        "SMTP_SERVER": "",
        "SMTP_PORT": "587",
        "SMTP_USERNAME": "",
        "SMTP_PASSWORD": "",
        "SMTP_FROM": "noreply@example.com",
        "ENVIRONMENT": "development",
        "SERVER_IP": server_ip,
        "USE_SSL": "false",
        "ENABLE_BOT": "true",
        "ENABLE_FRONTEND": "true",
        "MYSQL_USER": mysql_user,
        "MYSQL_PASSWORD": mysql_password,
        "MYSQL_DATABASE": mysql_db,
        "MYSQL_ROOT_PASSWORD": os.environ.get("MYSQL_ROOT_PASSWORD", "")
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
        
        # Create a .env file for frontend
        frontend_dir = os.path.join(os.getcwd(), "frontend")
        if os.path.exists(frontend_dir):
            frontend_env_path = os.path.join(frontend_dir, ".env")
            with open(frontend_env_path, "w") as f:
                f.write(f"REACT_APP_API_URL=http://{server_ip}/api\n")
                f.write(f"REACT_APP_SERVER_IP={server_ip}\n")
            print_success("Environment file created for frontend.")
        
        state.env_configured = True
        return True
    except Exception as e:
        print_error(f"Failed to create environment file: {str(e)}")
        return False

def initialize_database() -> bool:
    """
    Initialize the MySQL database for the application
    
    Returns:
        Boolean indicating if database initialization was successful
    """
    if state.database_initialized:
        print_success("Database already initialized.")
        return True
        
    print_step(6, 8, "Initializing MySQL database")
    
    # Get MySQL credentials from .env file
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
    
    mysql_user = env_vars.get("MYSQL_USER", "")
    mysql_password = env_vars.get("MYSQL_PASSWORD", "")
    mysql_db = env_vars.get("MYSQL_DATABASE", "")
    mysql_root_password = env_vars.get("MYSQL_ROOT_PASSWORD", "")
    
    if not mysql_db or not mysql_user:
        print_error("MySQL credentials not found in .env file.")
        return False
    
    # Create database user and permissions
    print_info(f"Ensuring MySQL user '{mysql_user}' exists...")
    
    # Create a SQL script to create user and database
    sql_script = f"""
CREATE DATABASE IF NOT EXISTS `{mysql_db}` CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
CREATE USER IF NOT EXISTS '{mysql_user}'@'localhost' IDENTIFIED BY '{mysql_password}';
GRANT ALL PRIVILEGES ON `{mysql_db}`.* TO '{mysql_user}'@'localhost';
FLUSH PRIVILEGES;
"""
    
    script_path = "/tmp/create_db.sql"
    with open(script_path, "w") as f:
        f.write(sql_script)
    
    # Execute SQL script as root
    success, _, _ = run_command(
        f"sudo mysql -u root -p{mysql_root_password} < {script_path}",
        "Failed to create MySQL database and user",
        f"MySQL database '{mysql_db}' and user '{mysql_user}' created successfully!",
        shell=True
    )
    
    # Remove temporary SQL file
    if os.path.exists(script_path):
        os.remove(script_path)
    
    if not success:
        return False
    
    # Update backend/app/core/config.py if it exists to use MySQL
    backend_config_path = os.path.join(os.getcwd(), "backend", "app", "core", "config.py")
    if os.path.exists(backend_config_path):
        print_info("Updating backend configuration to use MySQL...")
        
        try:
            # Read existing config
            with open(backend_config_path, "r") as f:
                config_content = f.read()
            
            # Update database connection string if needed
            if "postgresql" in config_content.lower() and "mysql" not in config_content.lower():
                # Replace PostgreSQL connection with MySQL
                config_content = re.sub(
                    r"(SQLALCHEMY_DATABASE_URI|DATABASE_URL).*?=.*?['\"]postgresql.*?['\"]",
                    f"\\1 = \"mysql+pymysql://{mysql_user}:{mysql_password}@localhost/{mysql_db}\"",
                    config_content
                )
                
                # Write updated config
                with open(backend_config_path, "w") as f:
                    f.write(config_content)
                
                print_success("Backend configuration updated to use MySQL.")
            else:
                print_info("Backend already configured for MySQL or connection string not found.")
        except Exception as e:
            print_warning(f"Failed to update backend config: {str(e)}")
    
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
        # Update alembic.ini to use MySQL if needed
        try:
            with open(alembic_ini, "r") as f:
                alembic_content = f.read()
            
            if "postgresql" in alembic_content and "mysql" not in alembic_content:
                alembic_content = re.sub(
                    r"sqlalchemy.url = postgresql.*",
                    f"sqlalchemy.url = mysql+pymysql://{mysql_user}:{mysql_password}@localhost/{mysql_db}",
                    alembic_content
                )
                
                with open(alembic_ini, "w") as f:
                    f.write(alembic_content)
                
                print_success("Updated alembic.ini to use MySQL.")
        except Exception as e:
            print_warning(f"Failed to update alembic.ini: {str(e)}")
        
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
        
        # Create basic database structure if no migrations exist
        print_info("Creating basic database structure...")
        base_tables_sql = """
CREATE TABLE IF NOT EXISTS `users` (
  `id` INT AUTO_INCREMENT PRIMARY KEY,
  `username` VARCHAR(50) NOT NULL UNIQUE,
  `email` VARCHAR(100) NOT NULL UNIQUE,
  `hashed_password` VARCHAR(255) NOT NULL,
  `is_active` BOOLEAN NOT NULL DEFAULT TRUE,
  `is_superuser` BOOLEAN NOT NULL DEFAULT FALSE,
  `created_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  `updated_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS `roles` (
  `id` INT AUTO_INCREMENT PRIMARY KEY,
  `name` VARCHAR(50) NOT NULL UNIQUE,
  `description` TEXT,
  `created_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS `user_roles` (
  `user_id` INT NOT NULL,
  `role_id` INT NOT NULL,
  PRIMARY KEY (`user_id`, `role_id`),
  FOREIGN KEY (`user_id`) REFERENCES `users` (`id`) ON DELETE CASCADE,
  FOREIGN KEY (`role_id`) REFERENCES `roles` (`id`) ON DELETE CASCADE
);

INSERT INTO `roles` (`name`, `description`) 
VALUES ('admin', 'Administrator with full access')
ON DUPLICATE KEY UPDATE `description` = 'Administrator with full access';
"""
        
        # Create basic tables SQL script
        basic_tables_path = "/tmp/basic_tables.sql"
        with open(basic_tables_path, "w") as f:
            f.write(base_tables_sql)
        
        # Execute SQL script to create basic tables
        run_command(
            f"mysql -u {mysql_user} -p{mysql_password} {mysql_db} < {basic_tables_path}",
            "Failed to create basic database tables",
            "Basic database tables created successfully!",
            shell=True
        )
        
        # Remove temporary SQL file
        if os.path.exists(basic_tables_path):
            os.remove(basic_tables_path)
        
        success = True
    
    if not success:
        return False
    
    state.database_initialized = True
    return True

def install_backend() -> bool:
    """
    Install and configure the backend application
    
    Returns:
        Boolean indicating if backend installation was successful
    """
    if state.backend_installed:
        print_success("Backend already installed.")
        return True
        
    print_step(7, 8, "Installing backend")
    
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
    
    # Install required build dependencies first
    print_info("Installing build dependencies...")
    build_deps_cmd = f"{python_bin} -m pip install --upgrade pip setuptools wheel"
    success, stdout, stderr = run_command(
        build_deps_cmd,
        "Failed to install build dependencies",
        "Build dependencies installed successfully!",
        shell=True
    )
    
    if not success:
        print_error(f"Failed to install build dependencies: {stderr}")
        return False
        
    # Install distutils if Python 3.12
    if sys.version_info.major == 3 and sys.version_info.minor >= 12:
        print_info("Installing distutils for Python 3.12+...")
        distutils_cmd = f"{python_bin} -m pip install setuptools"
        success, stdout, stderr = run_command(
            distutils_cmd,
            "Failed to install distutils",
            "Distutils installed successfully!",
            shell=True
        )
        
        if not success:
            print_error(f"Failed to install distutils: {stderr}")
            return False
    
    # Install dependencies using direct paths to Python and pip in the virtual environment
    print_info("Installing backend dependencies...")
    cmd = f"{python_bin} -m pip install -r {requirements_path} --no-build-isolation"
    success, stdout, stderr = run_command(
        cmd,
        "Failed to install backend dependencies",
        "Backend dependencies installed successfully!",
        shell=True
    )
    
    if not success:
        print_error(f"Failed to install backend dependencies: {stderr}")
        # Try installing packages one by one
        print_info("Trying to install packages one by one...")
        with open(requirements_path, 'r') as f:
            requirements = [line.strip() for line in f if line.strip() and not line.startswith('#')]
        
        all_success = True
        for req in requirements:
            print_info(f"Installing {req}...")
            req_cmd = f"{python_bin} -m pip install {req} --no-build-isolation"
            req_success, req_stdout, req_stderr = run_command(
                req_cmd,
                f"Failed to install {req}",
                f"{req} installed successfully!",
                shell=True
            )
            if not req_success:
                print_warning(f"Could not install {req}: {req_stderr}")
                all_success = False
        
        if not all_success:
            print_warning("Some packages could not be installed. The application may not function correctly.")
            # Continue anyway to let the user decide whether to proceed
        
    state.backend_installed = True
    return True

def installation_summary() -> None:
    """Display a summary of the installation status"""
    print_header("3X-UI Installation Summary")
    
    steps = [
        ("Virtual Environment Setup", state.venv_created),
        ("Prerequisites Installation", state.prerequisites_installed),
        ("Environment Configuration", state.env_configured),
        ("Backend Installation", state.backend_installed),
        ("MySQL Installation", state.mysql_installed),
        ("phpMyAdmin Installation", state.phpmyadmin_installed),
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

class UpdateManager:
    def __init__(self):
        self.backup_dir = "backups"
        self.current_version = "1.0.0"
        
    def create_backup(self) -> bool:
        """Create backup of critical files and database"""
        try:
            timestamp = time.strftime("%Y%m%d_%H%M%S")
            backup_path = os.path.join(self.backup_dir, f"backup_{timestamp}")
            
            # Create backup directory if it doesn't exist
            os.makedirs(backup_path, exist_ok=True)
            
            # Backup .env file
            if os.path.exists(".env"):
                shutil.copy2(".env", os.path.join(backup_path, ".env"))
            
            # Backup database
            if state.mysql_installed:
                env_vars = {}
                with open(".env", "r") as f:
                    for line in f:
                        if "=" in line:
                            key, value = line.strip().split("=", 1)
                            env_vars[key] = value
                
                mysql_user = env_vars.get("MYSQL_USER", "")
                mysql_password = env_vars.get("MYSQL_PASSWORD", "")
                mysql_db = env_vars.get("MYSQL_DATABASE", "")
                
                if mysql_db and mysql_user and mysql_password:
                    backup_file = os.path.join(backup_path, f"{mysql_db}.sql")
                    cmd = f"mysqldump -u {mysql_user} -p{mysql_password} {mysql_db} > {backup_file}"
                    success, _, _ = run_command(cmd, "Failed to backup database", shell=True)
                    if not success:
                        return False
            
            print_success(f"Backup created successfully at {backup_path}")
            return True
        except Exception as e:
            print_error(f"Failed to create backup: {str(e)}")
            return False
    
    def check_for_updates(self) -> Tuple[bool, str]:
        """Check if updates are available"""
        try:
            # Here you would typically check against a remote version
            # For now, we'll just return the current version
            return True, self.current_version
        except Exception as e:
            print_error(f"Failed to check for updates: {str(e)}")
            return False, ""
    
    def update_system(self) -> bool:
        """Update the system to the latest version"""
        try:
            # Create backup before updating
            if not self.create_backup():
                return False
            
            # Update package lists
            print_info("Updating system packages...")
            run_command(["sudo", "apt-get", "update"], "Failed to update package lists")
            
            # Upgrade installed packages
            print_info("Upgrading installed packages...")
            run_command(["sudo", "apt-get", "upgrade", "-y"], "Failed to upgrade packages")
            
            # Update Python packages
            print_info("Updating Python packages...")
            venv_pip = os.path.join("venv", "bin", "pip") if platform.system() != "Windows" else os.path.join("venv", "Scripts", "pip.exe")
            run_command([venv_pip, "install", "--upgrade", "-r", "backend/requirements.txt"], "Failed to update Python packages")
            
            # Update Node.js packages if frontend exists
            if os.path.exists("frontend"):
                print_info("Updating frontend packages...")
                os.chdir("frontend")
                run_command(["npm", "install"], "Failed to update frontend packages")
                os.chdir("..")
            
            print_success("System updated successfully!")
            return True
        except Exception as e:
            print_error(f"Failed to update system: {str(e)}")
            return False

def update_command() -> None:
    """Handle the update command"""
    print_header("3X-UI Management System Updater")
    
    updater = UpdateManager()
    has_updates, version = updater.check_for_updates()
    
    if has_updates:
        print_info(f"Current version: {version}")
        response = get_user_input("Do you want to update the system? [y/N]", "N")
        
        if response.lower() == "y":
            if updater.update_system():
                print_success("Update completed successfully!")
            else:
                print_error("Update failed. Please check the logs for details.")
    else:
        print_success("System is already up to date!")

def main() -> None:
    """Main installation function"""
    # Check if running in update mode
    if len(sys.argv) > 1 and sys.argv[1] == "update":
        update_command()
        return
    
    print_header("3X-UI Management System Local Installer")
    
    # Load previous state if available
    state.load_from_file()
    
    # Installation steps
    steps = [
        create_virtual_environment,
        install_prerequisites,
        install_mysql,
        install_phpmyadmin,
        configure_environment,
        initialize_database,
        install_backend
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
        state.mysql_installed and state.phpmyadmin_installed and state.database_initialized and state.backend_installed):
        state.installation_completed = True
        state.save_to_file()

if __name__ == "__main__":
    main() 