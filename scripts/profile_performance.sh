#!/bin/bash

# Colors for output
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo "📊 Starting performance profiling..."

# Navigate to project root
cd "$(dirname "$0")/.."

# Ensure virtual environment is active
if [ -z "$VIRTUAL_ENV" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
    source venv/bin/activate
fi

# Install profiling dependencies
echo "Installing profiling dependencies..."
pip install line_profiler memory_profiler psutil py-spy django-silk

# Create reports directory
mkdir -p reports/performance

# Backend Profiling
echo -e "\n${GREEN}Profiling backend performance...${NC}"

# CPU profiling with py-spy
echo "Running CPU profiling..."
py-spy record -o reports/performance/cpu_profile.svg -- python backend/manage.py runserver &
BACKEND_PID=$!
sleep 30
kill $BACKEND_PID

# Memory profiling
echo "Running memory profiling..."
mprof run backend/manage.py runserver &
BACKEND_PID=$!
sleep 30
kill $BACKEND_PID
mprof plot -o reports/performance/memory_profile.png

# Database query profiling
echo "Running database query profiling..."
python backend/manage.py shell << EOF
from django.db import connection
from django.test.utils import CaptureQueriesContext
from django.urls import reverse
from django.test import Client

client = Client()
with CaptureQueriesContext(connection) as context:
    # Test main API endpoints
    client.get(reverse('api:v1:users-list'))
    client.get(reverse('api:v1:servers-list'))
    client.get(reverse('api:v1:services-list'))

with open('reports/performance/db_queries.txt', 'w') as f:
    for query in context.captured_queries:
        f.write(f"Time: {query['time']}\nQuery: {query['sql']}\n\n")
EOF

# Frontend Profiling
if [ -d "frontend" ]; then
    echo -e "\n${GREEN}Profiling frontend performance...${NC}"
    cd frontend

    # Install frontend profiling dependencies
    npm install -D source-map-explorer webpack-bundle-analyzer

    # Build with source maps
    echo "Building frontend with source maps..."
    GENERATE_SOURCEMAP=true npm run build

    # Analyze bundle size
    echo "Analyzing bundle size..."
    npx source-map-explorer 'build/static/js/*.js' --html reports/performance/bundle-analysis.html

    # Run Lighthouse CI
    echo "Running Lighthouse analysis..."
    npm install -g @lhci/cli
    lhci autorun --collect.staticDistDir=./build \
                 --upload.target=filesystem \
                 --upload.outputDir=../reports/performance/lighthouse

    cd ..
fi

# Generate performance report
echo -e "\n${GREEN}Generating performance report...${NC}"
cat << EOF > reports/performance/SUMMARY.md
# Performance Analysis Results

## Overview
- Date: $(date)
- Project: V2Ray Bot
- Environment: Development

## Backend Performance
1. CPU Profiling
   - See: cpu_profile.svg
2. Memory Usage
   - See: memory_profile.png
3. Database Queries
   - See: db_queries.txt

## Frontend Performance
1. Bundle Analysis
   - See: bundle-analysis.html
2. Lighthouse Report
   - See: lighthouse/report.html

## Recommendations
1. Review the CPU profile for bottlenecks
2. Analyze memory usage patterns
3. Optimize slow database queries
4. Review bundle size and implement code splitting
5. Address Lighthouse performance suggestions

## Next Steps
1. Implement identified optimizations
2. Set up monitoring for production
3. Configure performance budgets
4. Implement caching strategies
EOF

echo -e "\n${GREEN}Performance profiling completed!${NC}"
echo "Reports are available in reports/performance/"
echo -e "${YELLOW}Please review the SUMMARY.md file for an overview of findings.${NC}" 