#!/bin/bash

# رنگ‌ها برای خروجی
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[0;33m'
RED='\033[0;31m'
NC='\033[0m' # بدون رنگ

# مسیر نصب
INSTALL_DIR="/opt/mrjbot"
BACKUP_DIR="$INSTALL_DIR/backups"

# بررسی دسترسی روت
if [ "$(id -u)" -ne 0 ]; then
    echo -e "${RED}این اسکریپت باید با دسترسی روت اجرا شود.${NC}"
    echo -e "${YELLOW}لطفاً با دستور sudo اجرا کنید.${NC}"
    exit 1
fi

# بررسی وجود دایرکتوری نصب
if [ ! -d "$INSTALL_DIR" ]; then
    echo -e "${RED}دایرکتوری نصب $INSTALL_DIR یافت نشد.${NC}"
    echo -e "${YELLOW}لطفاً ابتدا MRJBot را نصب کنید.${NC}"
    exit 1
fi

# تهیه پشتیبان قبل از بروزرسانی
echo -e "${BLUE}در حال تهیه پشتیبان قبل از بروزرسانی...${NC}"
TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
BACKUP_FILE="$BACKUP_DIR/pre_update_${TIMESTAMP}.tar.gz"

# ایجاد دایرکتوری پشتیبان اگر وجود نداشته باشد
mkdir -p $BACKUP_DIR

# توقف سرویس‌ها
echo -e "${BLUE}در حال توقف سرویس‌ها...${NC}"
cd $INSTALL_DIR && docker-compose stop

# تهیه پشتیبان از فایل‌های پیکربندی و دیتابیس
echo -e "${BLUE}در حال تهیه پشتیبان از فایل‌های پیکربندی و دیتابیس...${NC}"
tar -czf $BACKUP_FILE -C $INSTALL_DIR .env docker-compose.yml backend/config/settings.py \
    $(docker volume ls -q | grep mrjbot)

echo -e "${GREEN}پشتیبان با موفقیت در $BACKUP_FILE ذخیره شد.${NC}"

# بروزرسانی کد از مخزن
echo -e "${BLUE}در حال بروزرسانی کد از مخزن...${NC}"
cd $INSTALL_DIR

# ذخیره نسخه فعلی
CURRENT_VERSION=$(git rev-parse HEAD)
echo "نسخه قبلی: $CURRENT_VERSION" > $INSTALL_DIR/update_log.txt

# بروزرسانی کد
git pull

# ذخیره نسخه جدید
NEW_VERSION=$(git rev-parse HEAD)
echo "نسخه جدید: $NEW_VERSION" >> $INSTALL_DIR/update_log.txt

# بررسی تغییرات
if [ "$CURRENT_VERSION" == "$NEW_VERSION" ]; then
    echo -e "${YELLOW}هیچ بروزرسانی جدیدی یافت نشد.${NC}"
    echo -e "${BLUE}در حال راه‌اندازی مجدد سرویس‌ها...${NC}"
    cd $INSTALL_DIR && docker-compose start
    echo -e "${GREEN}سرویس‌ها با موفقیت راه‌اندازی مجدد شدند.${NC}"
    exit 0
fi

# بازسازی و راه‌اندازی مجدد کانتینرها
echo -e "${BLUE}در حال بازسازی و راه‌اندازی مجدد کانتینرها...${NC}"
cd $INSTALL_DIR
docker-compose down
docker-compose build
docker-compose up -d

# بررسی وضعیت سرویس‌ها
echo -e "${BLUE}در حال بررسی وضعیت سرویس‌ها...${NC}"
sleep 10
SERVICES_STATUS=$(docker-compose ps)
echo "$SERVICES_STATUS" >> $INSTALL_DIR/update_log.txt

# بررسی خطاها
if docker-compose ps | grep -q "Exit"; then
    echo -e "${RED}برخی از سرویس‌ها با خطا مواجه شدند.${NC}"
    echo -e "${YELLOW}در حال بازیابی پشتیبان...${NC}"
    
    # توقف سرویس‌ها
    docker-compose down
    
    # بازیابی پشتیبان
    tar -xzf $BACKUP_FILE -C $INSTALL_DIR
    
    # راه‌اندازی مجدد سرویس‌ها
    docker-compose up -d
    
    echo -e "${GREEN}پشتیبان با موفقیت بازیابی شد.${NC}"
    
    # ارسال اعلان به گروه ادمین تلگرام
    if [ -f "$INSTALL_DIR/.env" ]; then
        ADMIN_CHAT_ID=$(grep TELEGRAM_ADMIN_CHAT_ID $INSTALL_DIR/.env | cut -d '=' -f2)
        BOT_TOKEN=$(grep TELEGRAM_BOT_TOKEN $INSTALL_DIR/.env | cut -d '=' -f2)
        
        if [ ! -z "$ADMIN_CHAT_ID" ] && [ ! -z "$BOT_TOKEN" ]; then
            curl -s -X POST "https://api.telegram.org/bot$BOT_TOKEN/sendMessage" \
                -d chat_id="$ADMIN_CHAT_ID" \
                -d text="❌ بروزرسانی با خطا مواجه شد. سیستم به نسخه قبلی بازگردانده شد." > /dev/null
        fi
    fi
    
    exit 1
else
    echo -e "${GREEN}بروزرسانی با موفقیت انجام شد.${NC}"
    
    # ارسال اعلان به گروه ادمین تلگرام
    if [ -f "$INSTALL_DIR/.env" ]; then
        ADMIN_CHAT_ID=$(grep TELEGRAM_ADMIN_CHAT_ID $INSTALL_DIR/.env | cut -d '=' -f2)
        BOT_TOKEN=$(grep TELEGRAM_BOT_TOKEN $INSTALL_DIR/.env | cut -d '=' -f2)
        
        if [ ! -z "$ADMIN_CHAT_ID" ] && [ ! -z "$BOT_TOKEN" ]; then
            # تهیه لیست تغییرات
            CHANGES=$(git log --pretty=format:"%h - %s" $CURRENT_VERSION..$NEW_VERSION)
            
            # ارسال پیام به تلگرام
            curl -s -X POST "https://api.telegram.org/bot$BOT_TOKEN/sendMessage" \
                -d chat_id="$ADMIN_CHAT_ID" \
                -d text="🔥 نسخه جدید اومد، آپدیت شد! 🔥
                
تغییرات:
$CHANGES" > /dev/null
        fi
    fi
fi

echo -e "${GREEN}فرآیند بروزرسانی با موفقیت به پایان رسید.${NC}"
exit 0 