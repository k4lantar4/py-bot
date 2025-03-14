# MRJBot - Project Blueprint

## Project Overview

MRJBot is a comprehensive system for managing VPN accounts, featuring a Telegram bot, web dashboard, and management API. The system allows for easy creation, management, and tracking of VPN accounts, with features like payment processing, user management, and detailed analytics.

## System Architecture

The system is built using a microservices architecture with the following components:

```
                                  +----------------+
                                  |                |
                                  |  Load Balancer |
                                  |    (Nginx)     |
                                  |                |
                                  +--------+-------+
                                           |
                 +------------------------+------------------------+
                 |                        |                        |
        +--------v-------+       +--------v-------+       +--------v-------+
        |                |       |                |       |                |
        |  Frontend      |       |  Backend API   |       |  Telegram Bot  |
        |  (React)       |       |  (Django)      |       |  (Python)      |
        |                |       |                |       |                |
        +--------+-------+       +--------+-------+       +--------+-------+
                 |                        |                        |
                 |                        |                        |
                 |                +-------v--------+               |
                 |                |                |               |
                 +--------------->+  Database      +<--------------+
                                  |  (PostgreSQL)  |
                                  |                |
                                  +-------+--------+
                                          |
                                  +-------v--------+
                                  |                |
                                  |  Cache         |
                                  |  (Redis)       |
                                  |                |
                                  +----------------+
```

## Core Components

### 1. Backend API (Django)

The backend API is built with Django and Django REST Framework, providing:

- User management
- VPN account management
- Payment processing
- Analytics and reporting
- Admin operations

Key features:
- RESTful API design
- JWT authentication
- Role-based access control
- Comprehensive logging
- Metrics and monitoring endpoints

### 2. Telegram Bot (Python)

The Telegram bot is built using the python-telegram-bot library, providing:

- User registration and authentication
- VPN account purchase and management
- Payment processing
- Support chat
- Account status and usage statistics
- Notifications and alerts

### 3. Frontend Dashboard (React)

The frontend dashboard is built with React, providing:

- Admin dashboard for system management
- User dashboard for account management
- Sales and analytics visualization
- Payment management
- User management
- System monitoring

### 4. Database (PostgreSQL)

PostgreSQL is used as the primary database, with the following key tables:

- Users
- VPN Accounts
- Payments
- Transactions
- Plans
- Support Tickets
- System Logs

### 5. Cache (Redis)

Redis is used for:

- Session management
- Caching frequently accessed data
- Rate limiting
- Task queues
- Real-time notifications

### 6. Load Balancer (Nginx)

Nginx serves as:

- Static file server
- Reverse proxy
- Load balancer
- SSL termination
- Request routing

## Directory Structure

```
mrjbot/
├── backend/                  # Django backend API
│   ├── config/               # Django settings
│   ├── api/                  # API endpoints
│   ├── accounts/             # User account management
│   ├── vpn/                  # VPN account management
│   ├── payments/             # Payment processing
│   ├── analytics/            # Analytics and reporting
│   ├── notifications/        # Notification system
│   └── utils/                # Utility functions
│
├── bot/                      # Telegram bot
│   ├── handlers/             # Message handlers
│   ├── keyboards/            # Telegram keyboards
│   ├── services/             # Bot services
│   ├── utils/                # Utility functions
│   └── main.py               # Bot entry point
│
├── frontend/                 # React frontend
│   ├── public/               # Static files
│   ├── src/                  # Source code
│   │   ├── components/       # React components
│   │   ├── pages/            # Page components
│   │   ├── services/         # API services
│   │   ├── store/            # Redux store
│   │   ├── utils/            # Utility functions
│   │   └── App.js            # Main application
│   └── package.json          # NPM dependencies
│
├── nginx/                    # Nginx configuration
│   └── conf.d/               # Server configurations
│
├── scripts/                  # Utility scripts
│   ├── backup.sh             # Backup script
│   ├── restore.sh            # Restore script
│   └── update.sh             # Update script
│
├── monitoring/               # Monitoring configuration
│   ├── prometheus/           # Prometheus configuration
│   └── grafana/              # Grafana dashboards
│
├── docker-compose.yml        # Docker Compose configuration
├── .env.example              # Example environment variables
├── install.sh                # Installation script
├── mrjbot                    # CLI tool
├── README.md                 # English documentation
├── README-fa.md              # Persian documentation
└── project_blueprint.md      # This file
```

## Database Schema

### Users Table
- id (PK)
- username
- email
- password (hashed)
- first_name
- last_name
- role (admin, staff, user)
- telegram_id
- points
- created_at
- updated_at

### VPN Accounts Table
- id (PK)
- user_id (FK)
- plan_id (FK)
- username
- password
- server_id (FK)
- ip_address
- status (active, suspended, expired)
- data_limit
- data_used
- expiry_date
- created_at
- updated_at

### Plans Table
- id (PK)
- name
- description
- price
- duration (days)
- data_limit
- concurrent_connections
- features (JSON)
- is_active
- created_at
- updated_at

### Servers Table
- id (PK)
- name
- ip_address
- location
- provider
- capacity
- current_load
- status (online, offline, maintenance)
- created_at
- updated_at

### Payments Table
- id (PK)
- user_id (FK)
- amount
- payment_method
- transaction_id
- status (pending, completed, failed, refunded)
- receipt_image
- confirmed_by (FK, staff_id)
- confirmation_date
- created_at
- updated_at

### Transactions Table
- id (PK)
- user_id (FK)
- payment_id (FK)
- vpn_account_id (FK)
- amount
- type (purchase, renewal, refund)
- description
- created_at

### Support Tickets Table
- id (PK)
- user_id (FK)
- subject
- message
- status (open, in_progress, closed)
- assigned_to (FK, staff_id)
- created_at
- updated_at

### Ticket Messages Table
- id (PK)
- ticket_id (FK)
- user_id (FK)
- message
- is_staff
- created_at

## API Endpoints

### Authentication
- POST /api/auth/login/
- POST /api/auth/logout/
- POST /api/auth/register/
- POST /api/auth/refresh-token/
- GET /api/auth/me/

### Users
- GET /api/users/
- POST /api/users/
- GET /api/users/{id}/
- PUT /api/users/{id}/
- DELETE /api/users/{id}/
- GET /api/users/{id}/vpn-accounts/
- GET /api/users/{id}/payments/
- GET /api/users/{id}/tickets/

### VPN Accounts
- GET /api/vpn-accounts/
- POST /api/vpn-accounts/
- GET /api/vpn-accounts/{id}/
- PUT /api/vpn-accounts/{id}/
- DELETE /api/vpn-accounts/{id}/
- POST /api/vpn-accounts/{id}/renew/
- POST /api/vpn-accounts/{id}/suspend/
- POST /api/vpn-accounts/{id}/activate/
- GET /api/vpn-accounts/{id}/usage/

### Plans
- GET /api/plans/
- POST /api/plans/
- GET /api/plans/{id}/
- PUT /api/plans/{id}/
- DELETE /api/plans/{id}/

### Servers
- GET /api/servers/
- POST /api/servers/
- GET /api/servers/{id}/
- PUT /api/servers/{id}/
- DELETE /api/servers/{id}/
- GET /api/servers/{id}/status/
- GET /api/servers/{id}/accounts/

### Payments
- GET /api/payments/
- POST /api/payments/
- GET /api/payments/{id}/
- PUT /api/payments/{id}/
- DELETE /api/payments/{id}/
- POST /api/payments/{id}/confirm/
- POST /api/payments/{id}/reject/
- POST /api/payments/verify-receipt/

### Support Tickets
- GET /api/tickets/
- POST /api/tickets/
- GET /api/tickets/{id}/
- PUT /api/tickets/{id}/
- DELETE /api/tickets/{id}/
- GET /api/tickets/{id}/messages/
- POST /api/tickets/{id}/messages/
- POST /api/tickets/{id}/close/
- POST /api/tickets/{id}/reopen/

### Analytics
- GET /api/analytics/sales/
- GET /api/analytics/users/
- GET /api/analytics/vpn-accounts/
- GET /api/analytics/servers/
- GET /api/analytics/payments/

### System
- GET /api/health/
- GET /api/metrics/
- GET /api/logs/

## Telegram Bot Commands

- /start - Start the bot and show welcome message
- /help - Show help information
- /register - Register a new account
- /login - Login to existing account
- /account - Show account information
- /buy - Purchase a new VPN account
- /plans - Show available plans
- /renew - Renew existing VPN account
- /status - Check VPN account status
- /usage - Check data usage
- /payment - Make a payment
- /support - Contact support
- /faq - Show frequently asked questions
- /settings - Change settings
- /referral - Show referral information
- /points - Check points balance
- /redeem - Redeem points for rewards

## Security Considerations

1. **Authentication and Authorization**
   - JWT-based authentication
   - Role-based access control
   - Secure password storage (bcrypt)
   - Token expiration and refresh

2. **Data Protection**
   - HTTPS for all communications
   - Database encryption for sensitive data
   - Input validation and sanitization
   - Protection against SQL injection and XSS

3. **API Security**
   - Rate limiting
   - CORS configuration
   - API key authentication for external services
   - Request validation

4. **Infrastructure Security**
   - Docker container isolation
   - Regular security updates
   - Firewall configuration
   - Secure environment variable handling

5. **Monitoring and Logging**
   - Comprehensive logging of all operations
   - Real-time monitoring of system health
   - Alerting for suspicious activities
   - Regular security audits

## Deployment Requirements

### Minimum System Requirements
- Ubuntu 20.04 or 22.04 LTS
- 2 CPU cores
- 4GB RAM
- 40GB SSD storage
- Public IP address or domain name

### Recommended System Requirements
- Ubuntu 22.04 LTS
- 4 CPU cores
- 8GB RAM
- 80GB SSD storage
- Domain name with SSL certificate

### Software Requirements
- Docker and Docker Compose
- Nginx
- PostgreSQL 14+
- Redis 6+
- Python 3.10+
- Node.js 18+

## Future Enhancements

1. **Multi-server Support**
   - Load balancing across multiple VPN servers
   - Geographic distribution of servers
   - Automatic server selection based on user location

2. **Advanced Analytics**
   - User behavior analysis
   - Predictive analytics for resource planning
   - Advanced reporting capabilities

3. **Additional Payment Methods**
   - Cryptocurrency support
   - International payment gateways
   - Subscription-based billing

4. **Enhanced Security**
   - Two-factor authentication
   - Advanced threat detection
   - Automated security audits

5. **API Expansion**
   - Support for additional VPN protocols
   - Integration with third-party services
   - Public API for partners

6. **Mobile Applications**
   - Native iOS and Android apps
   - Mobile-specific features
   - Push notifications

## Conclusion

This blueprint provides a comprehensive overview of the MRJBot system architecture, components, and functionality. It serves as a guide for development, deployment, and future enhancements of the system. 