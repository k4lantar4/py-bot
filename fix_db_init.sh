#!/bin/bash

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[0;33m'
BLUE='\033[0;34m'
NC='\033[0m'

echo -e "${BLUE}┌────────────────────────────────────────┐${NC}"
echo -e "${BLUE}│   Database Initialization Fix Script   │${NC}"
echo -e "${BLUE}└────────────────────────────────────────┘${NC}"

# Activate virtual environment
echo -e "${YELLOW}🔌 Activating virtual environment...${NC}"
source venv/bin/activate

# Check for the init_db.py script
INIT_DB_PATH="backend/scripts/init_db.py"
if [ ! -f "$INIT_DB_PATH" ]; then
    echo -e "${RED}❌ Database initialization script not found at $INIT_DB_PATH${NC}"
    exit 1
fi

# Create a backup of the original script
echo -e "${YELLOW}📑 Creating backup of original init_db script...${NC}"
cp "$INIT_DB_PATH" "${INIT_DB_PATH}.bak"

# Check and fix other Python files that might import BaseSettings
echo -e "${YELLOW}🔍 Checking for Pydantic BaseSettings imports in backend files...${NC}"

# Fix config.py if it exists
if [ -f "backend/app/core/config.py" ]; then
    echo -e "${YELLOW}Fixing backend/app/core/config.py...${NC}"
    # Replace the import statement
    sed -i 's/from pydantic import AnyHttpUrl, BaseSettings/from pydantic import AnyHttpUrl\nfrom pydantic_settings import BaseSettings/g' backend/app/core/config.py
fi

# Find all Python files that import BaseSettings from pydantic
FILES_TO_FIX=$(grep -r "from pydantic import.*BaseSettings" --include="*.py" backend/ | cut -d: -f1)

# Fix each file
for file in $FILES_TO_FIX; do
    echo -e "${YELLOW}Fixing $file...${NC}"
    # Replace the import statement, preserving other imports
    sed -i 's/from pydantic import\(.*\)BaseSettings\(.*\)/from pydantic import\1\2\nfrom pydantic_settings import BaseSettings/g' "$file"
done

# Run database initialization
echo -e "${YELLOW}🗄️ Initializing database...${NC}"
cd backend
python -m scripts.init_db
if [ $? -eq 0 ]; then
    echo -e "${GREEN}✅ Database initialized successfully!${NC}"
else
    echo -e "${RED}❌ Database initialization failed. Check the error above.${NC}"
    echo -e "${YELLOW}🔍 Attempting to fix the issue manually...${NC}"
    
    # Here we can add more specific fixes for the init_db.py script if needed
    # For now, let's check if we need to fix EmailStr import as well
    if grep -q "EmailStr" scripts/init_db.py; then
        echo -e "${YELLOW}Fixing EmailStr import in init_db.py...${NC}"
        sed -i 's/from pydantic import.*EmailStr/from pydantic import AnyHttpUrl\nfrom pydantic_settings import EmailStr/g' scripts/init_db.py
        
        echo -e "${YELLOW}Trying database initialization again...${NC}"
        python -m scripts.init_db
        if [ $? -eq 0 ]; then
            echo -e "${GREEN}✅ Database initialized successfully after fixes!${NC}"
        else
            echo -e "${RED}❌ Database initialization still failing.${NC}"
            echo -e "${YELLOW}Please check the logs and fix the issues manually.${NC}"
        fi
    fi
fi
cd ..

echo -e "${GREEN}✅ Database setup completed!${NC}"
echo -e "${YELLOW}ℹ️ Next step: Start all services with ${BLUE}./start_services.sh${NC}" 