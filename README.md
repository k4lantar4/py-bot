# V2Ray Account Management System

A comprehensive Telegram bot and web dashboard for managing V2Ray accounts, integrated with multiple 3x-UI panels. Built with Python, Django, and React.

## Features

- 🤖 **Telegram Bot**
  - Sell and manage V2Ray accounts
  - Card-to-card and Zarinpal payment integration
  - Multi-language support (Persian/English)
  - Real-time notifications
  - User management and support

- 🌐 **Web Dashboard**
  - Modern, responsive UI with dark theme
  - RTL support for Persian language
  - Admin panel for system management
  - User dashboard for account management
  - Real-time traffic monitoring

- 🔄 **3x-UI Integration**
  - Multiple panel support
  - Real-time account synchronization
  - Traffic monitoring
  - Automatic account creation
  - Error handling and recovery

- 💳 **Payment System**
  - Card-to-card payment processing
  - Zarinpal gateway integration
  - Wallet system
  - Transaction history
  - Payment verification

## Prerequisites

- Ubuntu 22.04 LTS
- Docker and Docker Compose
- Domain name (for SSL)
- Telegram Bot Token
- 3x-UI panel credentials

## Quick Start

1. Clone the repository:
   ```bash
   git clone https://github.com/k4lantar4/py-bot.git
   cd py-bot
   ```

2. Run the installation script:
   ```bash
   sudo chmod +x install.sh
   sudo ./install.sh
   ```

3. Configure your environment:
   - Edit `.env` file with your settings
   - Set up your Telegram bot token
   - Configure 3x-UI panel credentials
   - Set up payment gateway details

4. Access the system:
   - Web Dashboard: `https://your-domain.com`
   - Admin Panel: `https://your-domain.com/admin`
   - Telegram Bot: Start with `/start` command

## Development Setup

1. Create virtual environment:
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   cd frontend && npm install
   ```

3. Run development servers:
   ```bash
   # Backend
   python manage.py runserver
   
   # Frontend
   cd frontend && npm start
   ```

## Docker Deployment

1. Build and start containers:
   ```bash
   docker compose build
   docker compose up -d
   ```

2. Check logs:
   ```bash
   docker compose logs -f
   ```

3. Stop services:
   ```bash
   docker compose down
   ```

## Project Structure

```
v2ray-bot/
├── backend/           # Django backend
├── frontend/         # React frontend
├── bot/             # Telegram bot
├── nginx/           # Nginx configuration
├── docs/            # Documentation
├── scripts/         # Utility scripts
└── docker/          # Docker configurations
```

## Contributing

1. Fork the repository
2. Create your feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Support

For support, please:
1. Check the [documentation](docs/)
2. Open an issue
3. Contact via Telegram: @your_support_username

## Acknowledgments

- [3x-UI](https://github.com/MHSanaei/3x-ui) for the panel integration
- [python-telegram-bot](https://github.com/python-telegram-bot/python-telegram-bot) for the bot framework
- [Django](https://www.djangoproject.com/) for the backend framework
- [React](https://reactjs.org/) for the frontend framework
