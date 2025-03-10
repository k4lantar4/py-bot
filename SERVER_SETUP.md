# 🚀 3X-UI Management System - Server Setup Guide

## 📋 پیش‌نیازها
- Ubuntu 20.04 یا 22.04 LTS
- دسترسی root به سرور
- توکن بات تلگرام (از BotFather)

## 🔧 مرحله 1: آماده‌سازی اولیه سرور

1. **اتصال به سرور از طریق SSH**:
   ```bash
   ssh root@your_server_ip
   ```

2. **به‌روزرسانی بسته‌های سیستم**:
   ```bash
   apt update && apt upgrade -y
   ```

3. **نصب Git**:
   ```bash
   apt install -y git
   ```

## 🔧 مرحله 2: راه‌اندازی پروژه

1. **کلون یا آپلود پروژه به سرور**:
   
   کلون از مخزن:
   ```bash
   git clone https://your-repository-url.git /root/py_bot
   ```
   
   یا آپلود فایل‌ها با استفاده از SCP:
   ```bash
   # از سیستم محلی خود
   ./transfer.sh
   ```

2. **رفتن به دایرکتوری پروژه**:
   ```bash
   cd /root/py_bot
   ```

3. **اجرای اسکریپت راه‌اندازی**:
   ```bash
   chmod +x setup.sh
   ./setup.sh
   ```

4. **پیکربندی متغیرهای محیطی**:
   
   ویرایش فایل `.env`:
   ```bash
   nano .env
   ```
   
   پارامترهای زیر را به‌روزرسانی کنید:
   - `TELEGRAM_BOT_TOKEN`: توکن بات شما از BotFather
   - `ADMIN_USER_IDS`: لیست شناسه‌های کاربران ادمین تلگرام (با کاما جدا شده)
   - `API_USERNAME` و `API_PASSWORD`: اگر از API استفاده می‌کنید
   - `POSTGRES_PASSWORD`: رمز عبور دیتابیس PostgreSQL
   - سایر تنظیمات مورد نیاز

## 🔧 مرحله 3: راه‌اندازی سرویس‌ها

1. **راه‌اندازی تمام سرویس‌ها**:
   ```bash
   chmod +x start_services.sh
   ./start_services.sh
   ```

2. **بررسی وضعیت سرویس‌ها**:
   ```bash
   supervisorctl status
   ```

3. **مشاهده لاگ‌ها در صورت نیاز**:
   ```bash
   ./manage.sh logs
   ```

## 🔧 مرحله 4: امن‌سازی سرور (اختیاری)

اجرای اسکریپت امن‌سازی:
```bash
chmod +x security.sh
./security.sh
```

این اسکریپت:
- بسته‌های سیستم را به‌روزرسانی می‌کند
- مجوزهای فایل مناسب را تنظیم می‌کند
- فایروال UFW را پیکربندی می‌کند
- fail2ban را برای محافظت SSH نصب و پیکربندی می‌کند

## 🔧 دستورات مدیریتی

از اسکریپت مدیریتی برای عملیات رایج استفاده کنید:

```bash
./manage.sh start    # شروع سرویس‌ها
./manage.sh stop     # توقف سرویس‌ها
./manage.sh restart  # راه‌اندازی مجدد سرویس‌ها
./manage.sh status   # بررسی وضعیت سرویس‌ها
./manage.sh logs     # مشاهده لاگ‌ها
./manage.sh update   # به‌روزرسانی وابستگی‌ها
./manage.sh backup   # ایجاد پشتیبان
./manage.sh help     # نمایش راهنما
```

## 🔧 به‌روزرسانی‌های استقرار

برای استقرار به‌روزرسانی‌ها به سرور:

1. انتقال فایل‌های به‌روزرسانی شده به سرور
2. اجرای اسکریپت استقرار:
   ```bash
   ./deploy.sh
   ```

## 🔧 عیب‌یابی

اگر سرویس‌ها شروع به کار نمی‌کنند:

1. **بررسی لاگ‌ها**:
   ```bash
   tail -f logs/backend_error.log
   tail -f logs/telegram_bot.err.log
   ```

2. **بررسی متغیرهای محیطی**:
   ```bash
   cat .env
   ```

3. **بررسی وابستگی‌های پایتون**:
   ```bash
   source venv/bin/activate
   pip list
   ```

4. **راه‌اندازی مجدد سرویس‌ها**:
   ```bash
   supervisorctl restart all
   ```

### خطاهای رایج و راه‌حل آن‌ها

#### 1. خطای `email-validator is not installed`

**علائم خطا**:
```
ImportError: email-validator is not installed, run `pip install pydantic[email]`
```

**راه‌حل**:
```bash
# اجرای اسکریپت رفع وابستگی‌ها
./fix_dependencies.sh

# یا نصب دستی
source venv/bin/activate
pip install email-validator==2.0.0
supervisorctl restart backend
```

## 🔧 پشتیبان‌گیری و بازیابی

**ایجاد پشتیبان**:
```bash
./manage.sh backup
```

**بازیابی از پشتیبان**:
```bash
# ابتدا سرویس را متوقف کنید
supervisorctl stop all

# کپی داده‌ها از پشتیبان
cp -r backups/YYYYMMDD_HHMMSS/data/* data/
cp backups/YYYYMMDD_HHMMSS/.env .

# راه‌اندازی مجدد سرویس
supervisorctl start all
```

## 🔧 دسترسی به سرویس‌ها

پس از راه‌اندازی موفقیت‌آمیز، می‌توانید به سرویس‌های زیر دسترسی داشته باشید:

- **API**: `http://your_server_ip/api/v1`
- **مستندات API**: `http://your_server_ip/api/docs`
- **فرانت‌اند**: `http://your_server_ip`
- **بات تلگرام**: از طریق تلگرام با نام کاربری بات خود 