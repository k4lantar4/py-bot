# MRJ Bot Project Blueprint 🌟

## Overview

MRJ Bot is a powerful V2Ray subscription and payment management system with a Telegram bot interface and web dashboard. Built with Django, React, and python-telegram-bot, it integrates with multiple 3x-UI panels for seamless V2Ray account management.

## Project Structure

```
mrjbot/
├── backend/                 # Django backend
│   ├── config/             # Django settings
│   ├── mrjbot/             # Main app
│   │   ├── models/         # Database models
│   │   ├── serializers/    # API serializers
│   │   ├── views/          # API views
│   │   ├── urls/           # URL routing
│   │   └── tasks/          # Celery tasks
│   └── manage.py
├── bot/                    # Telegram bot
│   ├── handlers/           # Command handlers
│   ├── keyboards/          # Inline keyboards
│   ├── messages/           # Message templates
│   └── utils/              # Utility functions
├── frontend/               # React frontend
│   ├── src/
│   │   ├── components/     # React components
│   │   ├── pages/         # Page components
│   │   ├── store/         # Redux store
│   │   ├── api/           # API clients
│   │   └── utils/         # Utility functions
│   └── package.json
├── nginx/                  # Nginx configuration
├── scripts/               # Utility scripts
├── tests/                 # Test files
├── docker-compose.yml     # Docker Compose config
├── Dockerfile            # Docker configuration
├── requirements.txt      # Python dependencies
└── README.md            # Project documentation
```

## Features

### Backend (Django)
- User Authentication & Authorization
- Subscription Management
- Payment Processing (Card-to-Card & Zarinpal)
- Commission System
- Notification System
- System Settings
- RESTful API
- Swagger Documentation
- Celery Tasks
- Redis Caching
- PostgreSQL Database
- Points System
- Live Chat Support
- Smart Plan Suggestions
- Server Monitoring
- Bulk Messaging
- Role Management (Admin, Seller, VIP)
- Card Owner Tracking
- Financial Reports
- License System

### Telegram Bot
- User Commands
  - /start - Start bot
  - /help - Show help
  - /profile - User profile
  - /subscription - Subscription info
  - /payment - Payment options
  - /wallet - Wallet balance
  - /transactions - Transaction history
  - /support - Contact support
  - /points - Check points
  - /chat - Live chat support
  - /plans - View smart plans

- Admin Commands
  - /admin - Admin panel
  - /users - User management
  - /subscriptions - Subscription management
  - /payments - Payment management
  - /settings - System settings
  - /broadcast - Send message to users
  - /stats - System statistics
  - /servers - Server management
  - /cards - Card tracking
  - /reports - Financial reports
  - /license - License management

- Seller Commands
  - /seller - Seller panel
  - /sales - Sales history
  - /commission - Commission info
  - /withdraw - Withdrawal request
  - /balance - Account balance
  - /cards - Card management
  - /points - Points management

### Frontend (React)
- Admin Dashboard
  - User Management
  - Subscription Management
  - Payment Management
  - Commission Management
  - System Settings
  - Statistics & Reports
  - Server Monitoring
  - Card Tracking
  - Points Management
  - License Management
  - Live Chat Support

- User Dashboard
  - Profile Management
  - Subscription Management
  - Transaction History
  - Wallet Management
  - Notifications
  - Points History
  - Live Chat
  - Smart Plan Suggestions

- Seller Dashboard
  - Sales History
  - Commission History
  - Withdrawal Requests
  - Account Balance
  - Performance Stats
  - Card Management
  - Points Management

## Technical Stack

### Backend
- Django 5.x
- Django REST framework
- PostgreSQL 13+
- Redis 6+
- Celery
- JWT Authentication
- CORS
- Swagger/OpenAPI
- 3x-UI API Integration
- OCR for Receipts
- Real-time WebSocket

### Frontend
- React 18.x
- TypeScript
- Material-UI
- Redux Toolkit
- React Query
- Axios
- RTL Support
- Dark Theme
- WebSocket Client
- Chart.js

### Bot
- python-telegram-bot v20+
- aiohttp
- SQLAlchemy
- Pydantic
- OCR Integration
- WebSocket Support

### Infrastructure
- Docker & Docker Compose
- Nginx
- SSL/TLS
- Ubuntu 22.04 LTS
- Backup System
- Monitoring Stack

## Security Features

### Authentication & Authorization
- JWT-based authentication
- Role-based access control
- Session management
- Password hashing
- 2FA support
- IP whitelisting

### Data Protection
- HTTPS encryption
- Input validation
- XSS protection
- CSRF protection
- SQL injection prevention
- Card data encryption
- Receipt data protection

### Infrastructure Security
- Firewall rules
- Rate limiting
- IP whitelisting
- SSL/TLS encryption
- Regular backups
- DDoS protection
- WAF integration

## Deployment

### Requirements
- Ubuntu 22.04 LTS
- Docker & Docker Compose
- Domain or public IP
- SSL certificate
- Minimum 2GB RAM
- 20GB SSD

### Installation
1. Clone repository
2. Configure environment variables
3. Build Docker images
4. Start services
5. Apply migrations
6. Create superuser
7. Configure SSL
8. Set up monitoring
9. Configure backup system
10. Set up license

### Maintenance
- Regular backups
- Log rotation
- Performance monitoring
- Security updates
- Database optimization
- License validation
- Server health checks

## Development Workflow

### Setup
1. Create virtual environment
2. Install dependencies
3. Configure database
4. Apply migrations
5. Create superuser
6. Run development server
7. Set up development SSL
8. Configure monitoring

### Testing
- Unit tests
- Integration tests
- API tests
- Frontend tests
- Bot tests
- Load tests
- Security tests

### Code Quality
- Black formatting
- isort imports
- flake8 linting
- mypy type checking
- pre-commit hooks
- SonarQube integration
- Code coverage tracking

## Future Enhancements

### Features
- OpenVPN Support
- Apple ID Integration
- PUBG UC Integration
- Mobile app
- Desktop app
- Browser extension
- API marketplace
- Webhook system
- Real-time updates
- File storage
- Search functionality

### Integration
- Additional Payment Gateways
- Email services
- SMS services
- Social media
- Cloud storage
- Analytics tools
- Monitoring services
- CRM systems

### Performance
- Database optimization
- Query caching
- Asset optimization
- Code splitting
- Lazy loading
- Service workers
- Edge computing
- CDN optimization

## License System

### Features
- License key validation
- Version control
- Feature flags
- Usage tracking
- Auto-renewal
- Grace period
- Backup protection
- Multi-server support

### Management
- License generation
- Activation system
- Usage monitoring
- Expiration handling
- Backup protection
- Server validation
- Feature control
- Analytics

## New Features 🚀

### AI Content Generation System
- OpenAI integration for automated content
- Scheduled post generation for Telegram channels
- Content types:
  - Promotional posts
  - VPN usage tips
  - Tech news
  - Service updates
  - Special offers
- Content approval workflow
- Multi-language support (Persian/English)
- Performance tracking

### Advanced Backup System
- Automated 30-minute backup intervals
- API-based backup collection
- Telegram group notifications
- Backup contents:
  - Database dumps
  - Configuration files
  - User data
  - System logs
- Backup rotation policy
- Emergency restore functionality

### Location Management
- Dynamic location switching
- Server locations:
  - Netherlands
  - France
  - Germany
  - United States
  - Singapore
- Smart naming convention (e.g., MoonVpn-France-1000-1)
- Location-based performance metrics
- Auto-failover system
- Load balancing

### Enhanced Role System
- Custom role creation
- Role types:
  - Receipt Admin
  - Support Agent
  - Content Manager
  - Location Manager
  - Points Admin
- Granular permission system
- Role activity logging
- Role-based analytics

### Points & Rewards System
- Point earning methods:
  - Purchases
  - Referrals
  - Account longevity
  - Special events
- Redemption options:
  - Service discounts
  - VIP status
  - Extended validity
  - Premium features
- Point expiry system
- Leaderboard integration

### Live Chat Integration
- Real-time support in Telegram bot
- Features:
  - Queue management
  - Agent assignment
  - Chat history
  - Quick responses
  - File sharing
  - Rating system
- Analytics dashboard
- Support team management

### Smart Plan Recommendations
- Usage pattern analysis
- Personalized suggestions
- Factors considered:
  - Data usage
  - Connection frequency
  - Peak usage times
  - Location preferences
- A/B testing system
- Conversion tracking

### Additional Enhancements
- Receipt OCR system
- Cryptocurrency payment integration:
  - USDT (TRC20)
  - Bitcoin
  - Other altcoins
- Multi-server API synchronization
- Enhanced monitoring system
- Automated reporting

### Telegram Group Integration
- Dedicated groups for:
  - User activity logs
  - Financial reports
  - Server status updates
  - Feature toggles
  - Support coordination
- Automated notifications
- Interactive commands
- Analytics reporting

### CLI Enhancements
New `mrjbot` commands:
```bash
mrjbot enable-backups     # Enable automated backups
mrjbot disable-backups    # Disable automated backups
mrjbot enable-chat        # Enable live chat
mrjbot disable-chat       # Disable live chat
mrjbot check-points       # Check user points
mrjbot redeem-points      # Redeem points
mrjbot set-role          # Set custom role
mrjbot toggle-ai         # Toggle AI features
mrjbot switch-location   # Change server location
``` 