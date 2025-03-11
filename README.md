# Virtual Account Sales Bot & Dashboard

A comprehensive solution for selling virtual accounts through Telegram with an integrated web dashboard.

## Features

- 🤖 Telegram Bot Interface
  - Multi-language support (Persian/English)
  - Automated account delivery
  - Order tracking
  - Support ticket system
  - User profile management

- 💼 Admin Dashboard
  - Modern React-based UI
  - Real-time statistics
  - Order management
  - Inventory control
  - User management
  - Payment tracking

- 💳 Payment Integration
  - Card-to-card payment support
  - Zarinpal integration
  - Payment verification system
  - Transaction history

- 🔐 Security Features
  - JWT authentication
  - Role-based access control
  - Rate limiting
  - Input validation
  - SQL injection protection

- 📱 Responsive Design
  - Mobile-first approach
  - RTL support
  - Dark/Light themes
  - Customizable UI

## Tech Stack

- Backend: FastAPI (Python 3.11+)
- Frontend: React + TypeScript
- Database: PostgreSQL
- Cache: Redis
- Task Queue: Celery
- Bot Framework: python-telegram-bot v20
- Container: Docker + Docker Compose

## Quick Start

1. Clone the repository:
```bash
git clone https://github.com/k4lantar4/py_bot.git
cd py_bot
```

2. Copy environment files:
```bash
cp .env.example .env
```

3. Start with Docker:
```bash
docker-compose up -d
```

4. Access services:
- Dashboard: http://localhost:3000
- API Docs: http://localhost:8000/docs
- Admin: http://localhost:3000/admin

## Development Setup

### Prerequisites
- Docker and Docker Compose
- Python 3.11+
- Node.js 18+
- PostgreSQL 15+
- Redis 7+

### Local Development
1. Backend:
```bash
cd backend
python -m venv venv
source venv/bin/activate  # or venv\Scripts\activate on Windows
pip install -r requirements.txt
uvicorn app.main:app --reload
```

2. Frontend:
```bash
cd frontend
npm install
npm run dev
```

3. Bot:
```bash
cd bot
python -m venv venv
source venv/bin/activate  # or venv\Scripts\activate on Windows
pip install -r requirements.txt
python bot.py
```

## Deployment

### VPS Requirements
- Ubuntu 22.04 LTS
- 2GB RAM minimum
- 20GB SSD
- Docker and Docker Compose

### Production Deployment
1. SSH into your server
2. Clone the repository
3. Run the setup script:
```bash
./setup.sh
```

## Documentation
- [API Documentation](docs/API.md)
- [Bot Commands](docs/BOT.md)
- [Admin Guide](docs/ADMIN.md)
- [Development Guide](docs/DEVELOPMENT.md)

## Support
For support, please open an issue or contact us through the bot's support system.

---

<div dir="rtl">

# ربات فروش اکانت مجازی و داشبورد مدیریت

راهکار جامع فروش اکانت‌های مجازی از طریق تلگرام با داشبورد وب یکپارچه

## ویژگی‌ها

- 🤖 رابط ربات تلگرام
  - پشتیبانی چند زبانه (فارسی/انگلیسی)
  - تحویل خودکار اکانت
  - پیگیری سفارش
  - سیستم تیکت پشتیبانی
  - مدیریت پروفایل کاربر

- 💼 داشبورد مدیریت
  - رابط کاربری مدرن مبتنی بر React
  - آمار لحظه‌ای
  - مدیریت سفارش‌ها
  - کنترل موجودی
  - مدیریت کاربران
  - پیگیری پرداخت‌ها

- 💳 درگاه پرداخت
  - پشتیبانی از پرداخت کارت به کارت
  - یکپارچه‌سازی با زرین‌پال
  - سیستم تأیید پرداخت
  - تاریخچه تراکنش‌ها

## نصب سریع

1. کلون کردن مخزن:
```bash
git clone https://github.com/yourusername/virtual-account-bot.git
cd virtual-account-bot
```

2. کپی فایل‌های محیطی:
```bash
cp .env.example .env
```

3. اجرا با داکر:
```bash
docker-compose up -d
```

برای اطلاعات بیشتر به بخش انگلیسی مراجعه کنید.

</div> 