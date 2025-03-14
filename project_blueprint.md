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
- Zarinpal Integration
  - Automatic payment verification
  - Transaction logging
  - Refund handling
- Financial Reports
  - Daily/weekly/monthly sales
  - Card-wise breakdowns
  - Confirmation statistics
  - Revenue projections

### Points & Rewards System 🌟
- Point Earning
  - Purchase-based points
  - Referral bonuses
  - Activity rewards
- Point Management
  - Point expiry system
  - Redemption options
  - VIP status tiers
  - CLI command: `mrjbot check-points`

### Live Chat Support System 💬
- Real-time chat in Telegram bot
- Support ticket management
- Agent assignment
- Chat history
- Response templates
- Performance metrics

### Smart Plan Suggestions 🎯
- Usage-based recommendations
- Traffic analysis
- Personalized offers
- Upgrade suggestions
- Multi-language templates

### Server Management 🖥️
- Multi-panel Integration
  - 3x-UI API sync
  - Load balancing
  - Failover support
- Server Monitoring
  - Health checks
  - Traffic monitoring
  - Performance metrics
  - Alert system

### Role Management 👥
- User Roles
  - Admin
  - Seller
  - VIP User
  - Regular User
- Permission System
  - Granular access control
  - Custom role creation
  - Activity logging

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
│   └── admin/           # Admin controls
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

### Docker Deployment
- One-command setup: `docker-compose up -d`
- Auto-updates via `update.sh`
- Backup system
- Health monitoring
- SSL management

### Update System
- Automated updates via `update.sh`
- Config backup
- Database backup
- Docker rebuild
- Admin notifications
- Rollback support: `mrjbot restore-backup`

## Security & Performance 🔒

### Security Features
- HTTPS everywhere
- JWT authentication
- Input validation
- Session encryption
- API rate limiting
- IP whitelisting

### Performance Optimization
- Redis caching
- Database optimization
- Load balancing
- CDN integration
- Asset compression

## Future Extensions 🔮

### Planned Features
- OpenVPN Support
- Apple ID Sales
- PUBG UC Integration
- Additional Payment Methods
- Enhanced Analytics
- AI-powered Support

## Documentation 📚

### User Guides
- Persian Guide (README-fa.md)
- English Guide (README.md)
- Installation Guide
- API Documentation
- Admin Manual

### Development
- Contributing Guidelines
- API Reference
- Testing Guide
- Security Guidelines
- Deployment Guide

## License & Updates 📝

### License System
- License validation
- Feature tiers
- Usage tracking
- Expiry management
- Auto-renewal

### Update Management
- Version control
- Change logging
- Migration scripts
- Backup system
- Rollback procedures 