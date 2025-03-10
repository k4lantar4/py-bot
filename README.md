# 3X-UI Management System

سیستم مدیریتی جامع برای پنل‌های 3X-UI با امکان مدیریت کاربران، کنترل دسترسی بر اساس نقش، و یکپارچه‌سازی API.

## ویژگی‌ها

- **مدیریت کاربران**: ایجاد، به‌روزرسانی و حذف کاربران با کنترل دسترسی مبتنی بر نقش
- **احراز هویت**: احراز هویت مبتنی بر JWT با توکن‌های بازنشانی
- **مدیریت نقش**: تخصیص نقش‌ها به کاربران با دسترسی‌های متفاوت
- **یکپارچه‌سازی API**: API مبتنی بر REST برای یکپارچه‌سازی با سایر سیستم‌ها
- **کش Redis**: کشینگ کارآمد برای بهبود عملکرد
- **ثبت وقایع**: ثبت وقایع جامع برای نظارت و اشکال‌زدایی

## قابلیت‌های نصب محلی جدید

- **نصب بدون نیاز به دامنه و SSL**: نصب با استفاده از IP سرور بدون نیاز به دامنه
- **پیگیری پیشرفت نصب**: هر بار اجرای اسکریپت، وضعیت مراحل نصب را بررسی و فقط مراحل ناتمام را انجام می‌دهد
- **نصب خودکار پیش‌نیازها**: تمام پیش‌نیازهای نصب بصورت خودکار بررسی و نصب می‌شوند
- **ایجاد محیط مجازی پایتون**: بصورت خودکار محیط مجازی پایتون ایجاد می‌شود
- **ایجاد خودکار فایل .env**: فایل تنظیمات محیطی به صورت خودکار با مقادیر ورودی کاربر یا مقادیر پیش‌فرض ایجاد می‌شود
- **پیکربندی خودکار سرویس‌ها**: سرویس‌های systemd و Nginx بطور خودکار پیکربندی می‌شوند
- **انعطاف‌پذیری در نصب**: امکان نصب بدون نیاز به ربات تلگرام یا فرانت‌اند

## فناوری‌های استفاده شده در بک‌اند

- **فریم‌ورک**: FastAPI
- **پایگاه داده**: MySQL با SQLAlchemy ORM
- **احراز هویت**: توکن‌های JWT با قابلیت بازنشانی
- **کشینگ**: Redis
- **صف کار**: Celery (برای کارهای پس‌زمینه)

## فناوری‌های استفاده شده در فرانت‌اند

- **فریم‌ورک**: React
- **کتابخانه UI**: Material-UI (MUI)
- **مدیریت وضعیت**: Redux
- **مسیریابی**: React Router
- **بین‌المللی‌سازی**: i18next
- **نمودارها**: Chart.js

## شروع به کار

### پیش‌نیازها

- Ubuntu 22.04+ (تست شده روی Ubuntu 22.04 و 24.04)
- دسترسی root یا sudo
- حداقل 1GB RAM
- حداقل 10GB فضای دیسک

### نصب آسان با یک دستور

فقط کافیست مخزن را کلون کرده و اسکریپت نصب را اجرا کنید:

```bash
# نصب git اگر نصب نیست
sudo apt-get update && sudo apt-get install -y git

# کلون کردن مخزن
git clone https://github.com/k4lantar4/py_bot.git
cd py_bot

# اجرای اسکریپت نصب
python3 install.py
```

این اسکریپت بطور خودکار:
1. محیط مجازی پایتون را ایجاد می‌کند
2. تمام پیش‌نیازها مانند Python، MySQL، Redis و Nginx را نصب می‌کند
3. فایل‌های محیطی `.env` را با دریافت اطلاعات از کاربر یا استفاده از مقادیر پیش‌فرض ایجاد می‌کند
4. پایگاه داده را راه‌اندازی می‌کند
5. سرویس‌های سیستمی را پیکربندی می‌کند
6. وضعیت نصب را گزارش می‌دهد

هر بار که اسکریپت را اجرا می‌کنید، فقط مراحلی که هنوز کامل نشده‌اند اجرا می‌شوند.

### رفع مشکلات رایج

#### مشکلات PHP

اگر با خطای نصب PHP مواجه شدید:

```bash
# حذف کامل PHP
sudo apt-get purge 'php*'
sudo apt-get autoremove
sudo apt-get autoclean

# نصب مجدد PHP 8.2
sudo add-apt-repository -y ppa:ondrej/php
sudo apt-get update
sudo apt-get install -y php8.2 php8.2-fpm php8.2-mysql php8.2-common
```

#### مشکلات MySQL

اگر MySQL به درستی نصب نمی‌شود:

```bash
# حذف کامل MySQL
sudo systemctl stop mysql
sudo killall -9 mysql
sudo killall -9 mysqld
sudo apt-get purge 'mysql*'
sudo rm -rf /var/lib/mysql /etc/mysql /var/run/mysqld
sudo deluser mysql
sudo delgroup mysql

# نصب مجدد MySQL
sudo apt-get update
sudo apt-get install -y mysql-server mysql-client
sudo mysql_secure_installation
```

#### مشکلات دسترسی به phpMyAdmin

اگر نمی‌توانید به phpMyAdmin دسترسی پیدا کنید:

1. بررسی کنید که Apache2 روی پورت 8080 در حال اجراست:
```bash
sudo netstat -tlpn | grep apache2
```

2. بررسی کنید که Nginx روی پورت 80 در حال اجراست:
```bash
sudo netstat -tlpn | grep nginx
```

3. بررسی لاگ‌های خطا:
```bash
sudo tail -f /var/log/nginx/error.log
sudo tail -f /var/log/apache2/error.log
```

### نصب دستی (برای توسعه‌دهندگان)

1. کلون کردن مخزن:
   ```bash
   git clone https://github.com/k4lantar4/py_bot.git
   cd py_bot
   ```

2. راه‌اندازی بک‌اند:
   ```bash
   cd backend
   python -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   ```

3. فایل `.env` به صورت خودکار توسط اسکریپت نصب ایجاد می‌شود، اما برای توسعه می‌توانید آن را به صورت دستی ایجاد کنید:
   ```
   # تنظیمات API
   SECRET_KEY=your-secret-key
   
   # تنظیمات پایگاه داده
   DATABASE_URL=mysql+pymysql://user:password@localhost/threexui
   
   # تنظیمات Redis
   REDIS_URL=redis://localhost:6379/0
   
   # تنظیمات دسترسی
   ACCESS_TOKEN_EXPIRE_MINUTES=30
   REFRESH_TOKEN_EXPIRE_DAYS=7
   ALGORITHM=HS256
   
   # تنظیمات CORS
   BACKEND_CORS_ORIGINS=["http://localhost:3000", "http://localhost:8080"]
   
   # محیط
   ENVIRONMENT=development
   SERVER_IP=localhost
   USE_SSL=false
   ENABLE_BOT=false
   ENABLE_FRONTEND=false
   ```

4. راه‌اندازی فرانت‌اند (اختیاری):
   ```bash
   cd ../frontend
   npm install
   ```

### اجرای برنامه

#### اجرای نسخه نصب شده با اسکریپت نصب

پس از نصب با اسکریپت، سرویس‌ها به صورت خودکار راه‌اندازی می‌شوند و می‌توانید با مراجعه به آدرس‌های زیر به برنامه دسترسی داشته باشید:
- API بک‌اند: http://YOUR_SERVER_IP/api
- مستندات API: http://YOUR_SERVER_IP/api/docs
- phpMyAdmin: http://YOUR_SERVER_IP/phpmyadmin

برای مدیریت سرویس‌ها:
```bash
# مدیریت بک‌اند
sudo systemctl status 3xui-backend.service
sudo systemctl restart 3xui-backend.service
sudo systemctl stop 3xui-backend.service
sudo systemctl start 3xui-backend.service

# مدیریت MySQL
sudo systemctl status mysql
sudo systemctl restart mysql

# مدیریت Apache2
sudo systemctl status apache2
sudo systemctl restart apache2

# مدیریت Nginx
sudo systemctl status nginx
sudo systemctl restart nginx
```

#### اجرای دستی (برای توسعه‌دهندگان)

1. شروع بک‌اند:
   ```bash
   cd backend
   uvicorn app.main:app --reload
   ```

2. شروع فرانت‌اند (اختیاری):
   ```bash
   cd frontend
   npm start
   ```

3. دسترسی به برنامه:
   - API بک‌اند: http://localhost:8000
   - مستندات API: http://localhost:8000/api/docs
   - فرانت‌اند: http://localhost:3000

## مستندات API

مستندات API در آدرس `/api/docs` هنگامی که بک‌اند در حال اجراست در دسترس است. این مستندات اطلاعات دقیقی در مورد تمام نقاط پایانی موجود، الگوهای درخواست/پاسخ و نیازهای احراز هویت ارائه می‌دهد.

## مجوز

این پروژه تحت مجوز MIT منتشر شده است - برای جزئیات بیشتر به فایل LICENSE مراجعه کنید. 