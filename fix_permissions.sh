#!/bin/bash

# تنظیم رنگ‌ها برای خروجی
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# چک کردن اجرا به عنوان روت
if [ "$EUID" -ne 0 ]; then
  echo -e "${RED}لطفا این اسکریپت را با دسترسی روت اجرا کنید (sudo).${NC}"
  exit 1
fi

echo -e "${YELLOW}🛠️ درحال رفع مشکل دسترسی‌های فایل‌ها...${NC}"

# مسیر نصب MRJBot
INSTALL_DIR="/root/py-bot"

# ساخت temp_dir
TEMP_DIR=$(mktemp -d)
cd $TEMP_DIR

# ایجاد Dockerfile موقت برای تنظیم دسترسی‌ها
cat > dockerfile_permissions_fix << EOF
FROM busybox
WORKDIR /target
COPY --from=python:3.11-slim /bin/chmod /bin/chmod
COPY --from=python:3.11-slim /bin/sh /bin/sh
ENTRYPOINT ["/bin/sh", "-c", "chmod +x /target/entrypoint.sh && echo 'Permissions fixed!'"]
EOF

cd $INSTALL_DIR

# تنظیم دسترسی‌های فایل‌های اسکریپت
echo -e "${YELLOW}🔧 تنظیم دسترسی اسکریپت‌های شل...${NC}"
chmod +x *.sh

# تنظیم دسترسی entrypoint.sh در دایرکتوری‌های مختلف
if [ -f "$INSTALL_DIR/bot/entrypoint.sh" ]; then
  echo -e "${YELLOW}🔧 تنظیم دسترسی entrypoint.sh بات...${NC}"
  chmod +x $INSTALL_DIR/bot/entrypoint.sh
fi

if [ -f "$INSTALL_DIR/backend/entrypoint.sh" ]; then
  echo -e "${YELLOW}🔧 تنظیم دسترسی entrypoint.sh بک‌اند...${NC}"
  chmod +x $INSTALL_DIR/backend/entrypoint.sh
fi

if [ -f "$INSTALL_DIR/frontend/entrypoint.sh" ]; then
  echo -e "${YELLOW}🔧 تنظیم دسترسی entrypoint.sh فرانت‌اند...${NC}"
  chmod +x $INSTALL_DIR/frontend/entrypoint.sh
fi

# اصلاح دسترسی‌ها در فایل‌های Docker
if [ -f "$INSTALL_DIR/bot/Dockerfile" ]; then
  echo -e "${YELLOW}📝 بروزرسانی Dockerfile بات...${NC}"
  # ساخت کانتینر موقت برای تنظیم دسترسی‌ها در بات
  docker build -t mrjbot_fix_bot_permissions -f $TEMP_DIR/dockerfile_permissions_fix .
  docker run --rm -v $INSTALL_DIR/bot:/target mrjbot_fix_bot_permissions
fi

if [ -f "$INSTALL_DIR/backend/Dockerfile" ]; then
  echo -e "${YELLOW}📝 بروزرسانی Dockerfile بک‌اند...${NC}"
  # ساخت کانتینر موقت برای تنظیم دسترسی‌ها در بک‌اند
  docker run --rm -v $INSTALL_DIR/backend:/target mrjbot_fix_bot_permissions
fi

# بازسازی و راه‌اندازی مجدد سرویس‌ها
echo -e "${YELLOW}🔄 بازسازی و راه‌اندازی مجدد سرویس‌ها...${NC}"
cd $INSTALL_DIR
docker-compose down
docker-compose build --no-cache bot backend
docker-compose up -d

# پاکسازی
rm -rf $TEMP_DIR

echo -e "${GREEN}✅ عملیات با موفقیت انجام شد! سرویس‌ها درحال راه‌اندازی مجدد هستند.${NC}"
echo -e "${YELLOW}💡 برای بررسی وضعیت سرویس‌ها، می‌توانید از دستور زیر استفاده کنید:${NC}"
echo -e "${GREEN}   mrjbot status${NC}" 