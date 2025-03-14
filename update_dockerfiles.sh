#!/bin/bash

# تنظیم رنگ‌ها برای خروجی
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}===================================================${NC}"
echo -e "${BLUE}🚀 MRJBot - اسکریپت بروزرسانی Dockerfile ها${NC}"
echo -e "${BLUE}===================================================${NC}"

# بروزرسانی Dockerfile بات
if [ -f "bot/Dockerfile" ]; then
    echo -e "${YELLOW}📝 بروزرسانی Dockerfile بات...${NC}"
    cat > bot/Dockerfile << 'EOF'
FROM python:3.11-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV PYTHONPATH=/app

# Set work directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    gcc \
    python3-dev \
    libpq-dev \
    curl && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Install dependencies
COPY requirements.txt /app/
RUN pip install --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copy bot code
COPY . /app/

# Make entrypoint executable
COPY entrypoint.sh /app/
RUN chmod +x /app/entrypoint.sh

ENTRYPOINT ["/app/entrypoint.sh"]

# Run bot
CMD ["python", "main.py"]
EOF
    echo -e "${GREEN}✅ Dockerfile بات بروزرسانی شد.${NC}"
fi

# بروزرسانی Dockerfile بک‌اند
if [ -f "backend/Dockerfile" ]; then
    echo -e "${YELLOW}📝 بروزرسانی Dockerfile بک‌اند...${NC}"
    cat > backend/Dockerfile << 'EOF'
FROM python:3.11-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV PYTHONPATH=/app

# Set work directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    gcc \
    python3-dev \
    libpq-dev \
    gettext \
    curl && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Create directories for media and static files
RUN mkdir -p /app/media /app/staticfiles

# Install dependencies
COPY requirements.txt /app/
RUN pip install --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copy project
COPY . /app/

# Make entrypoint executable
COPY entrypoint.sh /app/
RUN chmod +x /app/entrypoint.sh

# Create non-root user
RUN useradd -ms /bin/bash appuser && \
    chown -R appuser:appuser /app

# Change to non-root user
USER appuser

ENTRYPOINT ["/app/entrypoint.sh"]

# Run Django server
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
EOF
    echo -e "${GREEN}✅ Dockerfile بک‌اند بروزرسانی شد.${NC}"
fi

echo -e "${GREEN}✅ تمام فایل‌های Dockerfile با موفقیت بروزرسانی شدند.${NC}"
echo -e "${YELLOW}💡 اکنون می‌توانید با استفاده از دستور زیر سرویس‌ها را بازسازی کنید:${NC}"
echo -e "${BLUE}docker-compose build --no-cache${NC}"
echo -e "${YELLOW}💡 و سپس آنها را با دستور زیر راه‌اندازی کنید:${NC}"
echo -e "${BLUE}docker-compose up -d${NC}" 