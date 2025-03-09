# 3X-UI Management System

A comprehensive management system for 3X-UI panels with FastAPI backend, React frontend, and Telegram bot integration.

## 🚀 Features

- **Location Management**: CRUD operations for server locations
- **Server Management**: Integrate and manage 3X-UI servers
- **Service Management**: Create and manage subscription plans
- **User Management**: User accounts with role-based permissions
- **Discount Management**: Create and manage discount codes
- **Financial Reports**: Generate and export payment reports
- **Bulk Messaging**: Send messages to users with delivery tracking
- **Server Monitoring**: Real-time status and traffic monitoring
- **Access Control**: Role-based access control (RBAC)
- **Telegram Bot**: Mirror all management features in a Telegram bot
- **AI Features**: User behavior analysis and plan suggestions

## 📋 Requirements

### Backend
- Python 3.10+
- PostgreSQL 14+
- Redis 6+

### Frontend
- Node.js 18+
- npm 8+

## 🛠️ Installation

### Automated Installation (Ubuntu 22.04+)
```bash
# Clone the repository
git clone https://github.com/yourusername/3x-ui-management.git
cd 3x-ui-management

# Run the installer script
python install.py
```

### Manual Installation

#### Backend Setup
```bash
# Navigate to the backend directory
cd backend

# Create and activate a virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Set up environment variables
cp .env.example .env
# Edit .env with your configuration

# Initialize the database
python -m scripts.init_db

# Start the backend server
uvicorn app.main:app --reload
```

#### Frontend Setup
```bash
# Navigate to the frontend directory
cd frontend

# Install dependencies
npm install

# Start the development server
npm start
```

#### Telegram Bot Setup
```bash
# Navigate to the bot directory
cd bot

# Install dependencies (if not already installed with backend)
pip install -r requirements.txt

# Configure your bot
cp .env.example .env
# Edit .env with your Telegram Bot API Token

# Start the bot
python bot.py
```

## 🧪 Testing

```bash
# Run backend tests
cd backend
pytest

# Run frontend tests
cd frontend
npm test
```

## 📝 Configuration

The system is highly configurable through environment variables and the `config.py` file. See the `.env.example` files in each directory for available options.

## 📊 Documentation

API documentation is available at `/docs` when the backend server is running.

## 📜 License

This project is licensed under the MIT License - see the LICENSE file for details. 