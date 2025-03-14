# MRJ Bot - Ultimate V2Ray Management System 🚀

## Overview 🌟

MRJ Bot is a comprehensive V2Ray subscription and payment management system featuring a Telegram bot interface and web dashboard. Built with Django 5.x, React 18.x, and python-telegram-bot v20+, it seamlessly integrates with multiple 3x-UI panels for advanced V2Ray account management.

## Core Features 🎯

### Payment & Financial Management 💰
- Card-to-Card Payments with Owner Tracking
  - Track card owners and transactions
  - Automatic receipt verification (OCR)
  - Payment confirmation workflow
  - Transaction history
  - Card owner statistics
  - Admin/seller confirmation system
- Zarinpal Integration
  - Automatic payment verification
  - Transaction logging
  - Refund handling
- Financial Reports
  - Daily/weekly/monthly sales
  - Card-wise breakdowns
  - Confirmation statistics
  - Revenue projections
  - Card owner analytics

### Points & Rewards System 🌟
- Point Earning
  - Purchase-based points
  - Referral bonuses
  - Activity rewards
  - Special event multipliers
- Point Management
  - Point expiry system
  - Redemption options
  - VIP status tiers
  - Point history tracking
  - CLI command: `mrjbot check-points`
- VIP Benefits
  - Exclusive discounts
  - Priority support
  - Special features
  - Custom plans

### Live Chat Support System 💬
- Real-time chat in Telegram bot
- Support ticket management
- Agent assignment
- Chat history
- Response templates
- Performance metrics
- Multi-language support
- Quick response buttons
- Chat analytics

### Smart Plan Suggestions 🎯
- Usage-based recommendations
- Traffic analysis
- Personalized offers
- Upgrade suggestions
- Multi-language templates
- Usage patterns analysis
- Custom plan creation
- Plan comparison
- Traffic optimization tips

### Server Management 🖥️
- Multi-panel Integration
  - 3x-UI API sync
  - Load balancing
  - Failover support
  - Auto-recovery
  - Health monitoring
- Server Monitoring
  - Health checks
  - Traffic monitoring
  - Performance metrics
  - Alert system
  - Resource usage tracking
  - Auto-scaling support
- Server Analytics
  - Usage patterns
  - Performance trends
  - Cost analysis
  - Optimization suggestions

### Role Management 👥
- User Roles
  - Admin
  - Seller
  - VIP User
  - Regular User
  - Support Agent
- Permission System
  - Granular access control
  - Custom role creation
  - Activity logging
  - Role-based features
  - Audit trails
- Role Features
  - Custom permissions
  - Role inheritance
  - Temporary roles
  - Role expiration

## Technical Architecture 🏗️

### Backend (Django 5.x) ⚙️
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

### Telegram Bot (python-telegram-bot v20+) 🤖
```
bot/
├── handlers/
│   ├── payment/         # Payment handlers
│   ├── account/         # Account management
│   ├── support/         # Live chat
│   ├── points/          # Points system
│   ├── admin/           # Admin controls
│   ├── server/          # Server management
│   └── analytics/       # Analytics & reports
├── keyboards/           # Inline keyboards
├── messages/            # Message templates
└── utils/              # Bot utilities
```

### Frontend (React 18.x) 🎨
```
frontend/
├── src/
│   ├── components/      # Reusable components
│   ├── pages/          # Page components
│   ├── store/          # Redux store
│   ├── api/            # API clients
│   └── utils/          # Utilities
└── public/             # Static assets
```

## Deployment & Management 🚀

### CLI Tool (`mrjbot`)
- Installation: `mrjbot install`
- Updates: `mrjbot update`
- Backups: `mrjbot backup`
- Points: `mrjbot check-points`
- License: `mrjbot set-license <code>`
- Server: `mrjbot server <command>`
- Analytics: `mrjbot analytics <command>`

### Docker Deployment
- One-command setup: `docker-compose up -d`
- Auto-updates via `update.sh`
- Backup system
- Health monitoring
- SSL management
- Auto-scaling support

### Update System
- Automated updates via `update.sh`
- Config backup
- Database backup
- Docker rebuild
- Admin notifications
- Rollback support: `mrjbot restore-backup`
- Telegram group notifications

## Security & Performance 🔒

### Security Features
- HTTPS everywhere
- JWT authentication
- Input validation
- Session encryption
- API rate limiting
- IP whitelisting
- 2FA support
- Audit logging
- Security headers

### Performance Optimization
- Redis caching
- Database optimization
- Load balancing
- CDN integration
- Asset compression
- Query optimization
- Background tasks
- Rate limiting
- Resource monitoring

## Future Extensions 🔮

### Planned Features
- OpenVPN Support
  - Account management
  - Traffic monitoring
  - Multi-server support
- Apple ID Sales
  - Account management
  - Stock tracking
  - Price automation
- PUBG UC Integration
  - Order management
  - Stock tracking
  - Price automation
- Additional Payment Methods
  - Crypto support
  - Bank integration
  - Mobile wallets
- Enhanced Analytics
  - AI-powered insights
  - Predictive analytics
  - Custom reports
- AI-powered Support
  - Smart responses
  - Ticket classification
  - Sentiment analysis

## Documentation 📚

### User Guides
- Persian Guide (README-fa.md)
- English Guide (README.md)
- Installation Guide
- API Documentation
- Admin Manual
- User Manual
- Developer Guide

### Development
- Contributing Guidelines
- API Reference
- Testing Guide
- Security Guidelines
- Deployment Guide
- Architecture Guide
- Style Guide

## License & Updates 📝

### License System
- License validation
- Feature tiers
- Usage tracking
- Expiry management
- Auto-renewal
- Multi-server support
- Custom features

### Update Management
- Version control
- Change logging
- Migration scripts
- Backup system
- Rollback procedures
- Auto-updates
- Telegram notifications 