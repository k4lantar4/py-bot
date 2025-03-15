#!/bin/bash

# تنظیم رنگ‌ها برای خروجی
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${YELLOW}===================================================${NC}"
echo -e "${YELLOW}🔧 MRJBot - اصلاح مشکلات خاص Ubuntu${NC}"
echo -e "${YELLOW}===================================================${NC}"

# اصلاح دسترسی‌های فایل‌ها
echo -e "${YELLOW}🔒 تنظیم دسترسی‌های فایل‌ها...${NC}"

# اعطای دسترسی اجرایی به همه اسکریپت‌های شل
find . -name "*.sh" -exec chmod +x {} \;
echo -e "${GREEN}✅ دسترسی اجرایی به تمام اسکریپت‌های شل اعطا شد.${NC}"

# اعطای دسترسی اجرایی به فایل‌های خاص
chmod +x bot/entrypoint.sh
chmod +x bot/wait_for_db.py
echo -e "${GREEN}✅ دسترسی اجرایی به فایل‌های کلیدی اعطا شد.${NC}"

# تبدیل فرمت خط‌ها از DOS به UNIX
echo -e "${YELLOW}📝 تبدیل فرمت خط‌ها از DOS به UNIX...${NC}"
if command -v dos2unix &> /dev/null; then
    find . -name "*.sh" -exec dos2unix {} \;
    find . -name "*.py" -exec dos2unix {} \;
    echo -e "${GREEN}✅ فرمت خط‌ها با موفقیت تبدیل شد.${NC}"
else
    echo -e "${YELLOW}⚠️ dos2unix نصب نیست. در حال نصب...${NC}"
    apt-get update && apt-get install -y dos2unix
    find . -name "*.sh" -exec dos2unix {} \;
    find . -name "*.py" -exec dos2unix {} \;
    echo -e "${GREEN}✅ dos2unix نصب شد و فرمت خط‌ها تبدیل شد.${NC}"
fi

# پاکسازی و بازسازی تصاویر داکر
echo -e "${YELLOW}🔄 پاکسازی و بازسازی تصاویر داکر...${NC}"
docker-compose down || true
docker system prune -af
docker-compose build --no-cache
echo -e "${GREEN}✅ تصاویر داکر با موفقیت بازسازی شدند.${NC}"

# راه‌اندازی سرویس‌ها
echo -e "${YELLOW}🚀 راه‌اندازی سرویس‌ها...${NC}"
docker-compose up -d
echo -e "${GREEN}✅ سرویس‌ها با موفقیت راه‌اندازی شدند.${NC}"

# بررسی وضعیت سرویس‌ها
echo -e "${YELLOW}📊 بررسی وضعیت سرویس‌ها...${NC}"
docker-compose ps

echo -e "${GREEN}✅ تمام اصلاحات با موفقیت انجام شد.${NC}"
echo -e "${YELLOW}💡 برای مشاهده لاگ‌ها، دستور زیر را اجرا کنید:${NC}"
echo -e "   docker-compose logs -f"
echo -e "${YELLOW}💡 برای مشاهده لاگ سرویس بات، دستور زیر را اجرا کنید:${NC}"
echo -e "   docker-compose logs -f bot" 