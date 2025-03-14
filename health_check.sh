#!/bin/bash

# رنگ‌ها برای خروجی
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[0;33m'
RED='\033[0;31m'
NC='\033[0m' # بدون رنگ

# مسیر نصب
INSTALL_DIR="/root/py-bot"
LOG_FILE="$INSTALL_DIR/health_check.log"

# تابع نمایش راهنما
show_help() {
    echo -e "${BLUE}===================================================${NC}"
    echo -e "${BLUE}MRJBot - ابزار بررسی سلامت سیستم${NC}"
    echo -e "${BLUE}===================================================${NC}"
    echo -e "استفاده: $0 [گزینه]"
    echo
    echo -e "گزینه‌ها:"
    echo -e "  ${GREEN}--all${NC}              بررسی تمام سرویس‌ها"
    echo -e "  ${GREEN}--db${NC}               بررسی دیتابیس"
    echo -e "  ${GREEN}--redis${NC}            بررسی ردیس"
    echo -e "  ${GREEN}--api${NC}              بررسی API"
    echo -e "  ${GREEN}--bot${NC}              بررسی بات تلگرام"
    echo -e "  ${GREEN}--frontend${NC}         بررسی فرانت‌اند"
    echo -e "  ${GREEN}--help${NC}             نمایش این راهنما"
    echo
}

# تابع ثبت لاگ
log_message() {
    local level=$1
    local message=$2
    local timestamp=$(date +"%Y-%m-%d %H:%M:%S")
    echo "[$timestamp] [$level] $message" >> $LOG_FILE
    
    case $level in
        "INFO")
            echo -e "${BLUE}[$timestamp] $message${NC}"
            ;;
        "SUCCESS")
            echo -e "${GREEN}[$timestamp] $message${NC}"
            ;;
        "WARNING")
            echo -e "${YELLOW}[$timestamp] $message${NC}"
            ;;
        "ERROR")
            echo -e "${RED}[$timestamp] $message${NC}"
            ;;
        *)
            echo -e "[$timestamp] $message"
            ;;
    esac
}

# تابع بررسی دیتابیس
check_database() {
    log_message "INFO" "در حال بررسی اتصال به دیتابیس..."
    
    # استخراج اطلاعات اتصال به دیتابیس از فایل .env
    if [ -f "$INSTALL_DIR/.env" ]; then
        DB_HOST=$(grep DB_HOST $INSTALL_DIR/.env | cut -d '=' -f2)
        DB_PORT=$(grep DB_PORT $INSTALL_DIR/.env | cut -d '=' -f2)
        DB_NAME=$(grep DB_NAME $INSTALL_DIR/.env | cut -d '=' -f2)
        DB_USER=$(grep DB_USER $INSTALL_DIR/.env | cut -d '=' -f2)
        DB_PASSWORD=$(grep DB_PASSWORD $INSTALL_DIR/.env | cut -d '=' -f2)
    else
        log_message "ERROR" "فایل .env یافت نشد."
        return 1
    fi
    
    # بررسی اتصال به دیتابیس
    if docker-compose exec -T postgres pg_isready -h $DB_HOST -p $DB_PORT -U $DB_USER > /dev/null 2>&1; then
        log_message "SUCCESS" "اتصال به دیتابیس برقرار است."
        
        # بررسی تعداد جداول
        TABLE_COUNT=$(docker-compose exec -T postgres psql -h $DB_HOST -p $DB_PORT -U $DB_USER -d $DB_NAME -t -c "SELECT COUNT(*) FROM information_schema.tables WHERE table_schema = 'public';" | tr -d ' ')
        log_message "INFO" "تعداد جداول دیتابیس: $TABLE_COUNT"
        
        return 0
    else
        log_message "ERROR" "اتصال به دیتابیس برقرار نیست."
        return 1
    fi
}

# تابع بررسی ردیس
check_redis() {
    log_message "INFO" "در حال بررسی اتصال به ردیس..."
    
    # استخراج اطلاعات اتصال به ردیس از فایل .env
    if [ -f "$INSTALL_DIR/.env" ]; then
        REDIS_HOST=$(grep REDIS_HOST $INSTALL_DIR/.env | cut -d '=' -f2)
        REDIS_PORT=$(grep REDIS_PORT $INSTALL_DIR/.env | cut -d '=' -f2)
    else
        log_message "ERROR" "فایل .env یافت نشد."
        return 1
    fi
    
    # بررسی اتصال به ردیس
    if docker-compose exec -T redis redis-cli -h $REDIS_HOST -p $REDIS_PORT ping | grep -q "PONG"; then
        log_message "SUCCESS" "اتصال به ردیس برقرار است."
        
        # بررسی تعداد کلیدها
        KEY_COUNT=$(docker-compose exec -T redis redis-cli -h $REDIS_HOST -p $REDIS_PORT dbsize | tr -d '\r')
        log_message "INFO" "تعداد کلیدهای ردیس: $KEY_COUNT"
        
        return 0
    else
        log_message "ERROR" "اتصال به ردیس برقرار نیست."
        return 1
    fi
}

# تابع بررسی API
check_api() {
    log_message "INFO" "در حال بررسی API..."
    
    # استخراج اطلاعات API از فایل .env
    if [ -f "$INSTALL_DIR/.env" ]; then
        API_HOST=$(grep API_HOST $INSTALL_DIR/.env | cut -d '=' -f2 || echo "backend")
        API_PORT=$(grep API_PORT $INSTALL_DIR/.env | cut -d '=' -f2 || echo "8000")
    else
        log_message "ERROR" "فایل .env یافت نشد."
        return 1
    fi
    
    # بررسی اتصال به API
    if curl -s "http://$API_HOST:$API_PORT/api/health/" | grep -q "status.*ok"; then
        log_message "SUCCESS" "API در حال اجرا است."
        return 0
    else
        log_message "ERROR" "API در دسترس نیست."
        return 1
    fi
}

# تابع بررسی بات تلگرام
check_bot() {
    log_message "INFO" "در حال بررسی بات تلگرام..."
    
    # بررسی وضعیت کانتینر بات
    if docker-compose ps | grep bot | grep -q "Up"; then
        log_message "SUCCESS" "کانتینر بات تلگرام در حال اجرا است."
        
        # بررسی لاگ‌های بات
        BOT_LOGS=$(docker-compose logs --tail=20 bot)
        if echo "$BOT_LOGS" | grep -q "error\|exception\|traceback"; then
            log_message "WARNING" "خطاهایی در لاگ‌های بات تلگرام یافت شد."
            return 1
        else
            log_message "SUCCESS" "لاگ‌های بات تلگرام بدون خطا هستند."
            return 0
        fi
    else
        log_message "ERROR" "کانتینر بات تلگرام در حال اجرا نیست."
        return 1
    fi
}

# تابع بررسی فرانت‌اند
check_frontend() {
    log_message "INFO" "در حال بررسی فرانت‌اند..."
    
    # بررسی وضعیت کانتینر فرانت‌اند
    if docker-compose ps | grep frontend | grep -q "Up"; then
        log_message "SUCCESS" "کانتینر فرانت‌اند در حال اجرا است."
        
        # بررسی دسترسی به صفحه اصلی
        if curl -s -I http://localhost | grep -q "200 OK"; then
            log_message "SUCCESS" "صفحه اصلی فرانت‌اند در دسترس است."
            return 0
        else
            log_message "ERROR" "صفحه اصلی فرانت‌اند در دسترس نیست."
            return 1
        fi
    else
        log_message "ERROR" "کانتینر فرانت‌اند در حال اجرا نیست."
        return 1
    fi
}

# تابع بررسی تمام سرویس‌ها
check_all() {
    log_message "INFO" "شروع بررسی سلامت تمام سرویس‌ها..."
    
    # بررسی وضعیت کانتینرها
    log_message "INFO" "بررسی وضعیت کانتینرها..."
    CONTAINERS_STATUS=$(docker-compose ps)
    echo "$CONTAINERS_STATUS" >> $LOG_FILE
    
    # بررسی فضای دیسک
    log_message "INFO" "بررسی فضای دیسک..."
    DISK_USAGE=$(df -h / | tail -n 1)
    DISK_USED_PERCENT=$(echo $DISK_USAGE | awk '{print $5}' | tr -d '%')
    echo "فضای دیسک: $DISK_USAGE" >> $LOG_FILE
    
    if [ $DISK_USED_PERCENT -gt 90 ]; then
        log_message "ERROR" "فضای دیسک کم است! $DISK_USED_PERCENT% استفاده شده."
    elif [ $DISK_USED_PERCENT -gt 80 ]; then
        log_message "WARNING" "فضای دیسک در حال پر شدن است. $DISK_USED_PERCENT% استفاده شده."
    else
        log_message "SUCCESS" "فضای دیسک کافی است. $DISK_USED_PERCENT% استفاده شده."
    fi
    
    # بررسی استفاده از حافظه
    log_message "INFO" "بررسی استفاده از حافظه..."
    MEMORY_USAGE=$(free -m | grep Mem)
    MEMORY_TOTAL=$(echo $MEMORY_USAGE | awk '{print $2}')
    MEMORY_USED=$(echo $MEMORY_USAGE | awk '{print $3}')
    MEMORY_USED_PERCENT=$((MEMORY_USED * 100 / MEMORY_TOTAL))
    echo "استفاده از حافظه: $MEMORY_USAGE" >> $LOG_FILE
    
    if [ $MEMORY_USED_PERCENT -gt 90 ]; then
        log_message "ERROR" "استفاده از حافظه بالاست! $MEMORY_USED_PERCENT% استفاده شده."
    elif [ $MEMORY_USED_PERCENT -gt 80 ]; then
        log_message "WARNING" "استفاده از حافظه در حال افزایش است. $MEMORY_USED_PERCENT% استفاده شده."
    else
        log_message "SUCCESS" "استفاده از حافظه در حد مجاز است. $MEMORY_USED_PERCENT% استفاده شده."
    fi
    
    # بررسی سرویس‌های اصلی
    DB_STATUS=0
    REDIS_STATUS=0
    API_STATUS=0
    BOT_STATUS=0
    FRONTEND_STATUS=0
    
    check_database
    DB_STATUS=$?
    
    check_redis
    REDIS_STATUS=$?
    
    check_api
    API_STATUS=$?
    
    check_bot
    BOT_STATUS=$?
    
    check_frontend
    FRONTEND_STATUS=$?
    
    # نمایش خلاصه وضعیت
    echo -e "${BLUE}===================================================${NC}"
    echo -e "${BLUE}خلاصه وضعیت سلامت سیستم${NC}"
    echo -e "${BLUE}===================================================${NC}"
    
    if [ $DB_STATUS -eq 0 ]; then
        echo -e "دیتابیس: ${GREEN}سالم${NC}"
    else
        echo -e "دیتابیس: ${RED}مشکل دارد${NC}"
    fi
    
    if [ $REDIS_STATUS -eq 0 ]; then
        echo -e "ردیس: ${GREEN}سالم${NC}"
    else
        echo -e "ردیس: ${RED}مشکل دارد${NC}"
    fi
    
    if [ $API_STATUS -eq 0 ]; then
        echo -e "API: ${GREEN}سالم${NC}"
    else
        echo -e "API: ${RED}مشکل دارد${NC}"
    fi
    
    if [ $BOT_STATUS -eq 0 ]; then
        echo -e "بات تلگرام: ${GREEN}سالم${NC}"
    else
        echo -e "بات تلگرام: ${RED}مشکل دارد${NC}"
    fi
    
    if [ $FRONTEND_STATUS -eq 0 ]; then
        echo -e "فرانت‌اند: ${GREEN}سالم${NC}"
    else
        echo -e "فرانت‌اند: ${RED}مشکل دارد${NC}"
    fi
    
    # بررسی وضعیت کلی
    TOTAL_STATUS=$((DB_STATUS + REDIS_STATUS + API_STATUS + BOT_STATUS + FRONTEND_STATUS))
    
    echo -e "${BLUE}===================================================${NC}"
    if [ $TOTAL_STATUS -eq 0 ]; then
        echo -e "${GREEN}تمام سرویس‌ها سالم هستند.${NC}"
    elif [ $TOTAL_STATUS -lt 3 ]; then
        echo -e "${YELLOW}برخی از سرویس‌ها با مشکل مواجه هستند.${NC}"
    else
        echo -e "${RED}سیستم با مشکلات جدی مواجه است.${NC}"
    fi
    
    log_message "INFO" "بررسی سلامت تمام سرویس‌ها به پایان رسید."
}

# ایجاد دایرکتوری لاگ اگر وجود نداشته باشد
mkdir -p $(dirname $LOG_FILE)

# پردازش گزینه‌ها
case "$1" in
    --all)
        check_all
        ;;
    --db)
        check_database
        ;;
    --redis)
        check_redis
        ;;
    --api)
        check_api
        ;;
    --bot)
        check_bot
        ;;
    --frontend)
        check_frontend
        ;;
    --help|-h)
        show_help
        ;;
    *)
        show_help
        exit 1
        ;;
esac

exit 0 