#!/bin/bash

# تنظیم رنگ‌ها برای خروجی
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[0;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}=== شروع راه‌اندازی محیط داکر برای پروژه 3X-UI Management System ===${NC}"

# بررسی سیستم عامل
if [[ "$OSTYPE" == "msys" || "$OSTYPE" == "win32" ]]; then
    echo -e "${YELLOW}تشخیص سیستم عامل Windows...${NC}"
    # در Windows با Git Bash، دستورات را متناسب با محیط تنظیم می‌کنیم
    DOCKER_CMD="docker"
    DOCKER_COMPOSE_CMD="docker-compose"
else
    echo -e "${YELLOW}تشخیص سیستم عامل Linux/Unix...${NC}"
    # در لینوکس ممکن است به sudo نیاز داشته باشیم
    DOCKER_CMD="sudo docker"
    DOCKER_COMPOSE_CMD="sudo docker-compose"
    
    # بررسی نصب داکر در لینوکس
    if ! command -v docker &> /dev/null; then
        echo -e "${RED}داکر نصب نشده است. در حال نصب داکر...${NC}"
        
        # نصب داکر
        sudo apt-get update
        sudo apt-get install -y apt-transport-https ca-certificates curl software-properties-common
        curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo apt-key add -
        sudo add-apt-repository "deb [arch=amd64] https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable"
        sudo apt-get update
        sudo apt-get install -y docker-ce
        
        # نصب داکر کامپوز
        sudo curl -L "https://github.com/docker/compose/releases/download/v2.21.0/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
        sudo chmod +x /usr/local/bin/docker-compose
        
        echo -e "${GREEN}داکر و داکر کامپوز با موفقیت نصب شدند.${NC}"
    else
        echo -e "${GREEN}داکر قبلاً نصب شده است.${NC}"
    fi
fi

# بررسی نصب داکر در ویندوز
if [[ "$OSTYPE" == "msys" || "$OSTYPE" == "win32" ]]; then
    if ! command -v docker &> /dev/null; then
        echo -e "${RED}داکر در ویندوز نصب نشده است یا در PATH قرار ندارد.${NC}"
        echo -e "${YELLOW}لطفاً Docker Desktop را از آدرس زیر دانلود و نصب کنید:${NC}"
        echo -e "${BLUE}https://www.docker.com/products/docker-desktop/${NC}"
        exit 1
    else
        echo -e "${GREEN}داکر در ویندوز نصب شده است.${NC}"
    fi
fi

# کپی فایل .env.docker به .env اگر وجود نداشته باشد
if [ ! -f .env ]; then
    echo -e "${YELLOW}فایل .env یافت نشد. کپی کردن .env.docker به .env...${NC}"
    cp .env.docker .env
    echo -e "${GREEN}فایل .env ایجاد شد. لطفاً آن را با مقادیر مناسب خود ویرایش کنید.${NC}"
else
    echo -e "${GREEN}فایل .env موجود است.${NC}"
fi

# بیلد و اجرای کانتینرها
echo -e "${BLUE}در حال بیلد و اجرای کانتینرهای داکر...${NC}"
${DOCKER_COMPOSE_CMD} up -d --build

# بررسی وضعیت کانتینرها
echo -e "${BLUE}بررسی وضعیت کانتینرها:${NC}"
${DOCKER_COMPOSE_CMD} ps

echo -e "${GREEN}=== راه‌اندازی محیط داکر با موفقیت انجام شد ===${NC}"
echo -e "${YELLOW}شما می‌توانید به سرویس‌های زیر دسترسی داشته باشید:${NC}"
echo -e "${BLUE}- بک‌اند API: ${GREEN}http://localhost:8000/api${NC}"
echo -e "${BLUE}- مستندات API: ${GREEN}http://localhost:8000/api/docs${NC}"
echo -e "${BLUE}- فرانت‌اند: ${GREEN}http://localhost:3000${NC}"
echo -e "${BLUE}- phpMyAdmin: ${GREEN}http://localhost:8080${NC}"
echo -e "${BLUE}  نام کاربری: ${GREEN}root${NC}"
echo -e "${BLUE}  رمز عبور: ${GREEN}rootpassword${NC}"

echo -e "\n${YELLOW}دستورات مفید:${NC}"
echo -e "${BLUE}- مشاهده لاگ‌ها: ${GREEN}${DOCKER_COMPOSE_CMD} logs -f${NC}"
echo -e "${BLUE}- توقف سرویس‌ها: ${GREEN}${DOCKER_COMPOSE_CMD} down${NC}"
echo -e "${BLUE}- راه‌اندازی مجدد سرویس‌ها: ${GREEN}${DOCKER_COMPOSE_CMD} restart${NC}"
echo -e "${BLUE}- حذف کامل سرویس‌ها و حجم‌ها: ${GREEN}${DOCKER_COMPOSE_CMD} down -v${NC}" 