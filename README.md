# V2Ray Account Management System

A comprehensive system for managing V2Ray accounts through a Telegram bot and web dashboard, with multi-panel 3x-UI integration.

## Features

### Telegram Bot
- 🤖 User-friendly Telegram bot interface
- 🌐 Multi-language support (Persian and English)
- 💳 Multiple payment methods (Card-to-Card, Zarinpal)
- 🔄 Automatic account creation and renewal
- 📊 Usage statistics and notifications
- 🎫 Support ticket system

### Web Dashboard
- 🔐 Secure authentication system
- 🖥️ Admin panel for accounts, payments, and settings
- 📱 Responsive design with RTL support
- 🌙 Dark mode with modern UI (Dark gray, Deep blue color scheme)
- 📈 Detailed analytics and reporting

### Server Management
- 🔌 Integration with multiple 3x-UI panels
- 🔄 Real-time account data synchronization
- 📊 Traffic monitoring and management
- 🔔 Automatic notifications for expiring accounts
- 🛡️ Server health monitoring

### Payment Processing
- 💳 Card-to-Card payment with verification
- 🔄 Zarinpal payment gateway integration
- 💰 User wallet system
- 🏷️ Discount code support
- 📜 Transaction history and reporting

## Technology Stack

- **Backend**: Django 5.1+ with Django REST Framework
- **Frontend**: React with Material-UI
- **Bot**: python-telegram-bot (v20+)
- **Database**: PostgreSQL
- **Cache**: Redis
- **Task Queue**: Celery
- **Deployment**: Docker, Nginx

## Prerequisites

- Docker and Docker Compose
- Git

## Quick Start

1. Clone the repository:
```bash
git clone https://github.com/yourusername/v2ray_bot.git
cd v2ray_bot
```

2. Configure environment variables:
```bash
cp .env.example .env
# Edit .env with your settings
```

3. Start the application:
```bash
./install.sh
```

## Development Setup

### Backend
```bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
python manage.py migrate
python manage.py runserver
```

### Frontend
```bash
cd frontend
npm install
npm start
```

### Bot
```bash
cd bot
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
python main.py
```

## Testing

Run the test suite:
```bash
# Backend tests
cd backend
pytest

# Frontend tests
cd frontend
npm test
```

## Security Features

- 🔒 JWT authentication
- 🛡️ CSRF protection
- 🚫 Rate limiting
- 🔐 Content Security Policy (CSP)
- 🛑 DDoS protection
- 📝 Security headers
- 🔑 Password validation
- 🚦 IP blacklisting

## API Documentation

API documentation is available at `/api/docs/` when running in development mode.

## Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Support

For support, please open an issue or contact us through the support channels listed in the documentation. 