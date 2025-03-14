#!/bin/bash

# Colors for output
GREEN='\033[0;32m'
RED='\033[0;31m'
NC='\033[0m'

echo "🚀 Starting test automation..."

# Navigate to project root
cd "$(dirname "$0")/.."

# Ensure virtual environment is active
if [ -z "$VIRTUAL_ENV" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
    source venv/bin/activate
fi

# Install test dependencies
echo "Installing test dependencies..."
pip install -r backend/requirements.txt
pip install pytest pytest-django pytest-cov pytest-xdist pytest-html

# Run backend tests
echo -e "\n${GREEN}Running backend tests...${NC}"
cd backend
pytest \
    --cov=. \
    --cov-report=html \
    --cov-report=term \
    --html=reports/test_report.html \
    --self-contained-html \
    -v \
    --maxfail=10 \
    -n auto

# Check test status
if [ $? -eq 0 ]; then
    echo -e "\n${GREEN}✅ All tests passed!${NC}"
else
    echo -e "\n${RED}❌ Some tests failed. Check the reports for details.${NC}"
fi

# Run frontend tests
echo -e "\n${GREEN}Running frontend tests...${NC}"
cd ../frontend
npm test -- --coverage --watchAll=false

# Generate combined report
echo -e "\n${GREEN}Generating test reports...${NC}"
mkdir -p ../docs/test_reports
cp -r coverage/* ../docs/test_reports/frontend
cp -r ../backend/htmlcov/* ../docs/test_reports/backend
cp ../backend/reports/test_report.html ../docs/test_reports/

echo -e "\n${GREEN}Test automation completed!${NC}"
echo "Test reports are available in docs/test_reports/" 