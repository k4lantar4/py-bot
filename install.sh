#!/bin/bash

# رنگ‌ها برای خروجی
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[0;33m'
RED='\033[0;31m'
NC='\033[0m' # بدون رنگ

echo -e "${BLUE}===================================================${NC}"
echo -e "${BLUE}MRJBot - اسکریپت نصب برای اوبونتو${NC}"
echo -e "${BLUE}===================================================${NC}"

# بررسی اینکه آیا اسکریپت با دسترسی روت اجرا شده است
if [ "$EUID" -ne 0 ]; then
  echo -e "${RED}خطا: این اسکریپت باید با دسترسی روت اجرا شود.${NC}"
  echo -e "${YELLOW}لطفاً با دستور 'sudo ./install.sh' دوباره اجرا کنید.${NC}"
  exit 1
fi

# بررسی سیستم عامل
if [ -f /etc/os-release ]; then
    . /etc/os-release
    if [ "$ID" != "ubuntu" ]; then
        echo -e "${RED}خطا: این اسکریپت فقط برای اوبونتو طراحی شده است.${NC}"
        exit 1
    fi
    
    if [ "${VERSION_ID}" != "22.04" ] && [ "${VERSION_ID}" != "20.04" ]; then
        echo -e "${YELLOW}هشدار: این اسکریپت برای اوبونتو 22.04 یا 20.04 بهینه شده است.${NC}"
        echo -e "${YELLOW}ممکن است در نسخه ${VERSION_ID} به درستی کار نکند.${NC}"
        read -p "آیا می‌خواهید ادامه دهید؟ (y/n) " -n 1 -r
        echo
        if [[ ! $REPLY =~ ^[Yy]$ ]]; then
            exit 1
        fi
    fi
else
    echo -e "${RED}خطا: سیستم عامل شناسایی نشد.${NC}"
    exit 1
fi

echo -e "${GREEN}بررسی پیش‌نیازها...${NC}"

# بروزرسانی لیست بسته‌ها
echo -e "${BLUE}بروزرسانی لیست بسته‌ها...${NC}"
apt update

# نصب پیش‌نیازها
echo -e "${BLUE}نصب پیش‌نیازها...${NC}"
apt install -y curl git nano wget apt-transport-https ca-certificates gnupg lsb-release

# نصب Docker اگر نصب نشده باشد
if ! command -v docker &> /dev/null; then
    echo -e "${BLUE}نصب Docker...${NC}"
    curl -fsSL https://get.docker.com -o get-docker.sh
    sh get-docker.sh
    rm get-docker.sh
    systemctl enable docker
    systemctl start docker
else
    echo -e "${GREEN}Docker قبلاً نصب شده است.${NC}"
fi

# نصب Docker Compose اگر نصب نشده باشد
if ! command -v docker-compose &> /dev/null; then
    echo -e "${BLUE}نصب Docker Compose...${NC}"
    apt install -y docker-compose-plugin
else
    echo -e "${GREEN}Docker Compose قبلاً نصب شده است.${NC}"
fi

# ایجاد دایرکتوری نصب
INSTALL_DIR="/root/py-bot"
echo -e "${BLUE}ایجاد دایرکتوری نصب در ${INSTALL_DIR}...${NC}"
mkdir -p $INSTALL_DIR

# کپی فایل‌های پروژه
echo -e "${BLUE}کپی فایل‌های پروژه...${NC}"
cp -r * $INSTALL_DIR/

# تنظیم مجوزها
echo -e "${BLUE}تنظیم مجوزها...${NC}"
chmod +x $INSTALL_DIR/*.sh
chmod +x $INSTALL_DIR/mrjbot

# ایجاد لینک سیمبولیک برای دستور mrjbot
echo -e "${BLUE}ایجاد لینک سیمبولیک برای دستور mrjbot...${NC}"
ln -sf $INSTALL_DIR/mrjbot /usr/local/bin/mrjbot

# ایجاد فایل .env اگر وجود نداشته باشد
if [ ! -f $INSTALL_DIR/.env ]; then
    echo -e "${BLUE}ایجاد فایل .env...${NC}"
    cp $INSTALL_DIR/.env.example $INSTALL_DIR/.env
    echo -e "${YELLOW}لطفاً فایل .env را در مسیر ${INSTALL_DIR}/.env ویرایش کنید.${NC}"
fi

echo -e "${GREEN}نصب با موفقیت انجام شد!${NC}"
echo -e "${YELLOW}برای شروع سرویس‌ها، دستور زیر را اجرا کنید:${NC}"
echo -e "${BLUE}mrjbot start${NC}"
echo -e "${YELLOW}برای مشاهده وضعیت سرویس‌ها، دستور زیر را اجرا کنید:${NC}"
echo -e "${BLUE}mrjbot status${NC}"
echo -e "${YELLOW}برای مشاهده راهنما، دستور زیر را اجرا کنید:${NC}"
echo -e "${BLUE}mrjbot help${NC}" 