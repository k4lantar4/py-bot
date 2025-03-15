#!/bin/bash

# تنظیم رنگ‌ها برای خروجی
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${YELLOW}===================================================${NC}"
echo -e "${YELLOW}🔍 MRJBot - بررسی فایل‌های entrypoint${NC}"
echo -e "${YELLOW}===================================================${NC}"

# بررسی وجود و دسترسی فایل entrypoint.sh در پوشه بات
if [ -f "bot/entrypoint.sh" ]; then
    echo -e "${GREEN}✅ فایل bot/entrypoint.sh یافت شد.${NC}"
    
    # بررسی مجوز اجرایی
    if [ -x "bot/entrypoint.sh" ]; then
        echo -e "${GREEN}✅ فایل bot/entrypoint.sh مجوز اجرایی دارد.${NC}"
    else
        echo -e "${RED}❌ فایل bot/entrypoint.sh مجوز اجرایی ندارد!${NC}"
        echo -e "${YELLOW}🔧 در حال اعطای مجوز اجرایی...${NC}"
        chmod +x bot/entrypoint.sh
        echo -e "${GREEN}✅ مجوز اجرایی اعطا شد.${NC}"
    fi
    
    # بررسی محتوای فایل
    if grep -q "exec \"\$@\"" bot/entrypoint.sh; then
        echo -e "${GREEN}✅ محتوای فایل bot/entrypoint.sh صحیح است.${NC}"
    else
        echo -e "${RED}❌ فایل bot/entrypoint.sh فاقد دستور exec است!${NC}"
        echo -e "${YELLOW}🔧 لطفا محتوای فایل را بررسی کنید.${NC}"
    fi
else
    echo -e "${RED}❌ فایل bot/entrypoint.sh یافت نشد!${NC}"
    echo -e "${YELLOW}🔧 در حال ایجاد فایل entrypoint.sh...${NC}"
    
    # ایجاد فایل entrypoint.sh
    cat > bot/entrypoint.sh << 'EOF'
#!/bin/bash
set -e

echo "🚀 Starting MRJBot Telegram Bot..."

# بررسی محیط و پایگاه داده
echo "🔍 Checking environment..."
python -c "import os; print(f'Working directory: {os.getcwd()}')"
python -c "import sys; print(f'Python path: {sys.path}')"

# صبر برای آماده شدن پایگاه داده
echo "⏳ Waiting for database to be ready..."
if [ -f "/app/wait_for_db.py" ]; then
    python /app/wait_for_db.py
else
    echo "❌ Warning: wait_for_db.py not found!"
    # انتظار ساده برای پایگاه داده
    sleep 5
fi

echo "✅ Entrypoint completed successfully!"
echo "🤖 Running command: $@"

# اجرای دستور نهایی
exec "$@"
EOF
    
    chmod +x bot/entrypoint.sh
    echo -e "${GREEN}✅ فایل bot/entrypoint.sh ایجاد و مجوز اجرایی به آن اعطا شد.${NC}"
fi

# بررسی وجود و دسترسی فایل wait_for_db.py در پوشه بات
if [ -f "bot/wait_for_db.py" ]; then
    echo -e "${GREEN}✅ فایل bot/wait_for_db.py یافت شد.${NC}"
else
    echo -e "${RED}❌ فایل bot/wait_for_db.py یافت نشد!${NC}"
    echo -e "${YELLOW}🔧 در حال ایجاد فایل wait_for_db.py...${NC}"
    
    # ایجاد فایل wait_for_db.py
    cat > bot/wait_for_db.py << 'EOF'
#!/usr/bin/env python
"""
اسکریپت انتظار برای آماده شدن پایگاه داده
این اسکریپت تلاش می‌کند به پایگاه داده متصل شود و تا زمانی که اتصال موفقیت‌آمیز نباشد، منتظر می‌ماند
"""

import os
import time
import psycopg2
import logging

# تنظیم لاگینگ
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# پارامترهای اتصال به پایگاه داده
db_host = os.environ.get('DB_HOST', 'postgres')
db_port = os.environ.get('DB_PORT', '5432')
db_name = os.environ.get('DB_NAME', 'mrjbot')
db_user = os.environ.get('DB_USER', 'mrjbot')
db_password = os.environ.get('DB_PASSWORD', 'mrjbot')

# حداکثر تعداد تلاش‌ها
max_attempts = 60
attempts = 0

logger.info(f"Waiting for database {db_host}:{db_port} to be ready...")

while attempts < max_attempts:
    try:
        conn = psycopg2.connect(
            host=db_host,
            port=db_port,
            dbname=db_name,
            user=db_user,
            password=db_password
        )
        conn.close()
        logger.info("Database connection successful!")
        break
    except psycopg2.OperationalError as e:
        attempts += 1
        logger.warning(f"Database connection attempt {attempts}/{max_attempts} failed: {e}")
        time.sleep(1)
        
if attempts >= max_attempts:
    logger.error("Could not connect to database after maximum attempts. Exiting.")
    exit(1)
    
logger.info("Database is ready!")
EOF
    
    chmod +x bot/wait_for_db.py
    echo -e "${GREEN}✅ فایل bot/wait_for_db.py ایجاد شد.${NC}"
fi

# بررسی Dockerfile
if grep -q "RUN chmod +x /app/entrypoint.sh" bot/Dockerfile; then
    echo -e "${GREEN}✅ دستور chmod در Dockerfile وجود دارد.${NC}"
else
    echo -e "${YELLOW}⚠️ دستور chmod در Dockerfile نیاز به بررسی دارد.${NC}"
    echo -e "${YELLOW}🔧 لطفا اطمینان حاصل کنید که دستور زیر در Dockerfile وجود دارد:${NC}"
    echo -e "${YELLOW}   RUN chmod +x /app/entrypoint.sh${NC}"
fi

echo -e "${GREEN}✅ بررسی فایل‌ها با موفقیت انجام شد.${NC}"
echo -e "${YELLOW}💡 اکنون می‌توانید با دستور زیر سرویس‌ها را بازسازی کنید:${NC}"
echo -e "   docker-compose build --no-cache bot"
echo -e "${YELLOW}💡 و سپس با دستور زیر آن‌ها را راه‌اندازی کنید:${NC}"
echo -e "   docker-compose up -d" 