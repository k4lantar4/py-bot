FROM python:3.11-slim

WORKDIR /app

# نصب پکیج‌های مورد نیاز سیستم
RUN apt-get update && apt-get install -y \
    build-essential \
    gcc \
    python3-dev \
    default-libmysqlclient-dev \
    pkg-config \
    git \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# کپی فایل‌های وابستگی
COPY ./backend/requirements.txt .

# نصب وابستگی‌ها
RUN pip install --no-cache-dir -r requirements.txt
# نصب صریح pymysql
RUN pip install --no-cache-dir pymysql

# کپی کل پروژه بک‌اند
COPY ./backend /app

# تنظیم متغیرهای محیطی برای داکر
ENV PYTHONPATH=/app
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# اکسپوز کردن پورت
EXPOSE 8000

# کامند شروع برنامه
WORKDIR /app
CMD ["python", "-m", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"] 