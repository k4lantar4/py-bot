#!/bin/bash

# Colors for output
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo "🔒 Starting security testing..."

# Navigate to project root
cd "$(dirname "$0")/.."

# Ensure virtual environment is active
if [ -z "$VIRTUAL_ENV" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
    source venv/bin/activate
fi

# Install security testing dependencies
echo "Installing security testing dependencies..."
pip install safety bandit pylint owasp-zap-api-python python-dotenv

# Create reports directory
mkdir -p reports/security

# Run static code analysis
echo -e "\n${GREEN}Running static code analysis...${NC}"
pylint backend/ --output-format=json > reports/security/pylint-report.json

# Run dependency vulnerability scanning
echo -e "\n${GREEN}Checking for known vulnerabilities in dependencies...${NC}"
safety check -r backend/requirements.txt --json > reports/security/safety-report.json

# Run Bandit for security issues
echo -e "\n${GREEN}Running Bandit security scanner...${NC}"
bandit -r backend/ -f json -o reports/security/bandit-report.json

# Run custom security checks
echo -e "\n${GREEN}Running custom security checks...${NC}"

# Check for sensitive data in configuration
echo "Checking for sensitive data in configuration files..."
find . -type f -name "*.py" -o -name "*.env*" -o -name "*.yml" | while read file; do
    grep -i "password\|secret\|key\|token" "$file" > reports/security/sensitive-data.txt
done

# Check file permissions
echo "Checking file permissions..."
find . -type f -perm /o+w -ls > reports/security/write-permissions.txt

# Check for debug configurations
echo "Checking for debug configurations..."
grep -r "DEBUG = True" backend/ > reports/security/debug-settings.txt

# Run npm audit for frontend
if [ -d "frontend" ]; then
    echo -e "\n${GREEN}Running npm audit for frontend dependencies...${NC}"
    cd frontend
    npm audit --json > ../reports/security/npm-audit.json
    cd ..
fi

# Generate summary report
echo -e "\n${GREEN}Generating security report summary...${NC}"
cat << EOF > reports/security/SUMMARY.md
# Security Test Results

## Overview
- Date: $(date)
- Project: V2Ray Bot
- Version: $(git describe --tags --always)

## Test Results
1. Static Code Analysis (Pylint)
   - See: pylint-report.json
2. Dependency Vulnerabilities
   - Backend: safety-report.json
   - Frontend: npm-audit.json
3. Security Issues (Bandit)
   - See: bandit-report.json
4. Custom Security Checks
   - Sensitive Data: sensitive-data.txt
   - File Permissions: write-permissions.txt
   - Debug Settings: debug-settings.txt

## Action Items
Please review the detailed reports in the reports/security directory.
Critical issues should be addressed immediately.
EOF

echo -e "\n${GREEN}Security testing completed!${NC}"
echo "Reports are available in reports/security/"
echo -e "${YELLOW}Please review the SUMMARY.md file for an overview of findings.${NC}" 