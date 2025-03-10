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
    # Replace the import statement - Ensure EmailStr is imported from pydantic, not pydantic_settings
    if grep -q "from pydantic_settings import BaseSettings, EmailStr" "backend/app/core/config.py"; then
        # Fix incorrect import if it exists
        sed -i 's/from pydantic_settings import BaseSettings, EmailStr/from pydantic_settings import BaseSettings\nfrom pydantic import EmailStr/g' "backend/app/core/config.py"
    elif grep -q "from pydantic import.*EmailStr" "backend/app/core/config.py" && grep -q "from pydantic_settings import BaseSettings" "backend/app/core/config.py"; then
        # Already fixed, do nothing
        echo "Config file already has correct imports"
    else
        # Standard fix
        sed -i 's/from pydantic import AnyHttpUrl, BaseSettings/from pydantic import AnyHttpUrl, EmailStr\nfrom pydantic_settings import BaseSettings/g' "backend/app/core/config.py"
    fi
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
    
    # Fix for EmailStr import issue
    if grep -q "EmailStr" app/core/config.py; then
        echo -e "${YELLOW}Fixing EmailStr import in config.py...${NC}"
        # Ensure EmailStr is imported from pydantic, not pydantic_settings
        sed -i 's/from pydantic_settings import BaseSettings, EmailStr/from pydantic_settings import BaseSettings\nfrom pydantic import EmailStr/g' app/core/config.py
        
        # Also check for EmailStr in validator import
        sed -i 's/from pydantic_settings import BaseSettings, EmailStr, PostgresDsn, validator/from pydantic_settings import BaseSettings, PostgresDsn, validator\nfrom pydantic import EmailStr/g' app/core/config.py
        
        echo -e "${YELLOW}Trying database initialization again...${NC}"
        python -m scripts.init_db
        if [ $? -eq 0 ]; then
            echo -e "${GREEN}✅ Database initialized successfully after fixes!${NC}"
        else
            echo -e "${RED}❌ Database initialization still failing.${NC}"
            echo -e "${YELLOW}Please check app/core/config.py and fix the EmailStr import manually.${NC}"
        fi
    fi
fi
cd ..

echo -e "${GREEN}✅ Database setup completed!${NC}"
echo -e "${YELLOW}ℹ️ Next step: Start all services with ${BLUE}./start_services.sh${NC}" 