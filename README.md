# V2Ray Account Management System

A comprehensive system for managing V2Ray accounts with a Telegram bot and web dashboard, allowing for the sale and management of V2Ray accounts.

## Key Features

### Telegram Bot
- **User Authentication**: Registration and login
- **Account Management**: View, create, and renew V2Ray accounts
- **Payments**: Card-to-card payments and Zarinpal gateway
- **User Profile**: View and edit user information
- **Notification System**: Account expiry, traffic usage, and payment status notifications
- **Admin Panel**: Manage users, servers, payments, and system settings

### Web Dashboard
- **User Panel**: Manage accounts, payments, and profile
- **Admin Panel**: Manage users, servers, payments, and system settings

### 3x-UI Integration
- **Account Management**: Create and manage accounts in 3x-UI panels
- **Traffic Monitoring**: Check account traffic usage
- **Server Statistics**: Monitor server status

## Recent Changes

### Telegram Bot Improvements
- **Payment System**: Complete implementation of card-to-card and Zarinpal payments
- **Account Management**: Improved account display, renewal, and configuration with QR code
- **User Profile**: Edit user information and view transaction history
- **Admin Panel**: Manage users, servers, payments, and system settings
- **Notification System**: Account expiry, traffic usage, and payment status notifications

## Installation and Setup

### Prerequisites
- Python 3.8+
- Docker and Docker Compose
- Ubuntu 22.04 server

### Installation
1. Clone the repository:
```bash
git clone https://github.com/username/v2ray-management.git
cd v2ray-management
```

2. Run the installation script:
```bash
chmod +x install.sh
./install.sh
```

3. Set up the Telegram webhook:
```bash
python bot/set_webhook.py --token YOUR_BOT_TOKEN --url https://your-domain.com/webhook
```

## For Developers
For local development and testing, you can use the following commands:

1. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # on Linux
venv\Scripts\activate  # on Windows
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Run the bot in polling mode:
```bash
python bot/polling.py
```

## Documentation
For more information, refer to the following files:
- `docs/user-guide.md`: User guide
- `docs/admin-guide.md`: Admin guide
- `docs/developer-guide.md`: Developer guide
