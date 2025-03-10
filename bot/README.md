# 3X-UI Telegram Bot

A modular Telegram bot for managing 3X-UI services with a focus on Persian language support and user-friendly interactions.

## Features

- 🌐 Full Persian language support with internationalization
- 🔐 Secure authentication and session management
- 👥 User and admin command separation
- 📊 Service management and monitoring
- 🛠️ Modular and maintainable codebase

## Directory Structure

```
bot/
├── src/
│   ├── commands/      # Command handlers
│   ├── handlers/      # Message and callback handlers
│   ├── utils/         # Utility functions
│   ├── i18n/         # Translation files
│   ├── keyboards/     # Keyboard layouts
│   ├── services/     # Business logic
│   └── config/       # Configuration
├── tests/           # Test files
└── requirements.txt # Dependencies
```

## Setup

1. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Create a `.env` file with your configuration:
```env
TELEGRAM_BOT_TOKEN=your_bot_token
ADMIN_USER_IDS=["123456789"]
API_BASE_URL=http://localhost:8000/api/v1
```

## Running the Bot

Start the bot:
```bash
python src/main.py
```

## Available Commands

### Basic Commands
- `/start` - Start the bot
- `/help` - Show help message

### Authentication
- `/login` - Log in to your account
- `/logout` - Log out from your account
- `/profile` - View your profile

### User Commands
- `/services` - List available services
- `/orders` - List your orders
- `/clients` - List your clients
- `/status` - Check server status

### Admin Commands
- `/users` - List users
- `/servers` - List servers
- `/locations` - List locations
- `/stats` - Show system statistics

## Development

### Code Style
The project uses:
- Black for code formatting
- isort for import sorting
- flake8 for linting

Format code:
```bash
black .
isort .
flake8
```

### Testing
Run tests:
```bash
pytest
```

With coverage:
```bash
pytest --cov=src tests/
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Run tests and linting
5. Submit a pull request

## License

MIT License - see LICENSE file for details 