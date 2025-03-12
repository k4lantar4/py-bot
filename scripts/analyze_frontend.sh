#!/bin/bash

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

echo "🔍 Starting frontend bundle analysis..."

# Navigate to frontend directory
cd "$(dirname "$0")/../frontend"

# Install dependencies if needed
if [ ! -d "node_modules" ]; then
    echo "Installing dependencies..."
    npm install
fi

# Install analysis tools
npm install -D webpack-bundle-analyzer source-map-explorer

# Build with bundle analyzer
echo -e "\n${GREEN}Building production bundle with analyzer...${NC}"
ANALYZE=true npm run build

# Analyze bundle size with source-map-explorer
echo -e "\n${GREEN}Analyzing bundle with source-map-explorer...${NC}"
npx source-map-explorer 'dist/**/*.js' --html bundle-analysis.html

# Check for large dependencies
echo -e "\n${YELLOW}Checking for large dependencies...${NC}"
npm list --prod --json | jq -r '.dependencies | to_entries[] | select(.value.size > 500000) | .key + ": " + (.value.size/1024/1024|tostring) + "MB"'

# Suggest optimizations
echo -e "\n${GREEN}Optimization suggestions:${NC}"

# Check for duplicate dependencies
echo -e "\n${YELLOW}Checking for duplicate dependencies...${NC}"
npm dedupe

# Check for unused dependencies
echo -e "\n${YELLOW}Checking for unused dependencies...${NC}"
npx depcheck

# Generate report
echo -e "\n${GREEN}Generating optimization report...${NC}"
cat << EOF > ../docs/frontend_optimization.md
# Frontend Bundle Analysis Report

## Bundle Size Analysis
- Total bundle size can be found in bundle-analysis.html
- Check dist/stats.json for detailed module breakdown

## Large Dependencies
The following dependencies might need optimization:
\`\`\`
$(npm list --prod --json | jq -r '.dependencies | to_entries[] | select(.value.size > 500000) | "- " + .key + ": " + (.value.size/1024/1024|tostring) + "MB"')
\`\`\`

## Optimization Suggestions
1. Consider code splitting for routes and large components
2. Implement lazy loading for images and heavy components
3. Use dynamic imports for less frequently used features
4. Review and remove unused dependencies
5. Consider using smaller alternatives for large packages
6. Implement tree shaking for all imports

## Next Steps
1. Review bundle-analysis.html for detailed breakdown
2. Optimize identified large dependencies
3. Implement suggested performance improvements
4. Re-run analysis after optimizations
EOF

echo -e "\n${GREEN}Analysis complete!${NC}"
echo "Check bundle-analysis.html and docs/frontend_optimization.md for detailed reports" 