#!/bin/bash

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[0;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${BLUE}===================================================${NC}"
echo -e "${BLUE}MRJBot Test Runner - Unix/Linux${NC}"
echo -e "${BLUE}===================================================${NC}"

echo -e "${YELLOW}Running simple component tests...${NC}"
docker-compose -f docker-compose-simple-test.yml up --abort-on-container-exit
docker-compose -f docker-compose-simple-test.yml down

echo
echo -e "${YELLOW}Running comprehensive tests...${NC}"
docker-compose -f docker-compose-test-all.yml up --abort-on-container-exit
docker-compose -f docker-compose-test-all.yml down

echo
echo -e "${GREEN}Testing complete! Check the output above for results.${NC}"
echo 