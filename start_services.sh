#!/bin/bash

# تنظیم رنگ‌ها برای خروجی
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${YELLOW}===================================================${NC}"
echo -e "${YELLOW}🚀 MRJBot - راه‌اندازی سرویس‌ها${NC}"
echo -e "${YELLOW}===================================================${NC}"

# بررسی دسترسی‌های فایل‌های اجرایی
echo -e "${YELLOW}🔍 بررسی دسترسی‌های فایل‌ها...${NC}"

# اجرای اسکریپت بررسی فایل‌ها
./check_entrypoint.sh

# توقف سرویس‌های فعلی (در صورت وجود)
echo -e "${YELLOW}🛑 متوقف کردن سرویس‌های قبلی...${NC}"
docker-compose down || true

# بازسازی تصاویر Docker
echo -e "${YELLOW}🔄 بازسازی تصاویر Docker...${NC}"
docker-compose build --no-cache

# راه‌اندازی سرویس‌ها
echo -e "${YELLOW}🚀 راه‌اندازی سرویس‌ها...${NC}"
docker-compose up -d

# بررسی وضعیت سرویس‌ها
echo -e "${YELLOW}📊 بررسی وضعیت سرویس‌ها...${NC}"
docker-compose ps

echo -e "${GREEN}✅ راه‌اندازی سرویس‌ها با موفقیت انجام شد.${NC}"
echo -e "${YELLOW}💡 برای مشاهده لاگ‌ها، دستور زیر را اجرا کنید:${NC}"
echo -e "   docker-compose logs -f" 