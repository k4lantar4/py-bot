# 🤖 V2Ray Telegram Bot

## 📝 About
A comprehensive V2Ray account management system featuring:
- 🤖 Telegram bot with Persian language support
- 🌐 Modern web dashboard
- 💳 Payment system with Zarinpal and card-to-card support
- 🔄 Integration with 3x-UI panels
- 🔔 Telegram notifications
- 🌍 Multi-language support (Persian and English)

## 🚀 Key Features

### 👥 User Management
- ✅ User registration and authentication
- ✅ User profiles
- ✅ Role-based access (Admin, Seller, VIP)
- ✅ User management by admins

### 💳 Payment System
- ✅ Online payments via Zarinpal
- ✅ Card-to-card transfers
- ✅ User wallet
- ✅ Transaction history
- ✅ Discount system

### 🌐 Server Management
- ✅ Integration with 3x-UI panels
- ✅ Server monitoring
- ✅ Traffic management
- ✅ Automatic server rotation

### 📱 Telegram Bot
- ✅ Basic commands (/start, /help)
- ✅ Account management
- ✅ Payments and purchases
- ✅ User profiles
- ✅ Admin panel
- ✅ Support system

### 🎨 Web Dashboard
- ✅ Modern UI
- ✅ Dark theme
- ✅ RTL support
- ✅ Multi-language
- ✅ Account management
- ✅ Admin panel

## 🛠️ Technologies Used

### Backend
- Django 5.x
- Django REST framework
- PostgreSQL
- Redis
- Celery

### Frontend
- React 18.x
- TypeScript
- Tailwind CSS
- Redux Toolkit
- React Query

### Bot
- python-telegram-bot v20+
- aiohttp
- SQLAlchemy
- Pydantic

### Infrastructure
- Docker & Docker Compose
- Nginx
- Let's Encrypt SSL
- Ubuntu 22.04 LTS

## 📊 Project Status

### ✅ Completed
- Core project structure
- Authentication system
- User management
- Payment processing
- 3x-UI integration
- Telegram bot
- Web dashboard
- Multi-language support
- Notification system

### ⚠️ In Development
- Server monitoring
- Financial reporting
- Bulk messaging
- Performance optimization
- Backup system
- Monitoring dashboard

### 🔜 Planned
- OpenVPN support
- Apple ID account sales
- PUBG UC sales
- Advanced discount system
- Developer API

## 🚀 Installation

### Prerequisites
- Ubuntu 22.04 LTS
- Docker & Docker Compose
- Domain or public IP
- SSL certificate (optional)

### Setup
1. Clone the repository:
```bash
git clone https://github.com/yourusername/v2ray-telegram-bot.git
cd v2ray-telegram-bot
```

2. Configure environment files:
```bash
cp .env.example .env
# Edit .env with your settings
```

3. Start with Docker:
```bash
docker compose up -d
```

4. Run installation script:
```bash
./install.sh
```

## 📚 Documentation
- [Installation Guide](docs/installation.md)
- [User Guide](docs/user-guide.md)
- [Admin Guide](docs/admin-guide.md)
- [API Documentation](docs/api.md)

## 🤝 Contributing
To contribute to the project:
1. Fork the repository
2. Create a new branch
3. Make your changes
4. Submit a Pull Request

## 📝 License
This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

## 📞 Support
- Telegram: [@v2raybot](https://t.me/v2raybot)
- Email: support@example.com
- Website: https://example.com

## 🙏 Acknowledgments
- [3x-UI](https://github.com/MHSanaei/3x-ui) for V2Ray management panel
- [python-telegram-bot](https://github.com/python-telegram-bot/python-telegram-bot) for Telegram bot library
- [Django](https://www.djangoproject.com/) for backend framework
- [React](https://reactjs.org/) for frontend framework
