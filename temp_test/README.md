# 🤖 V2Ray Telegram Bot with Web Dashboard

## 🌟 Key Features

### 🤖 Telegram Bot
- Complete V2Ray account management
- Powerful admin panel
- Card-to-card and Zarinpal payment system
- Points and rewards system
- Live support chat
- Smart plan suggestions
- Multi-language support (Persian-first)
- Telegram notifications
- Card management with owner tracking
- Financial reports
- Seller panel
- Server management
- Bulk messaging

### 🎨 Web Dashboard
- Modern and beautiful UI
- Dark and deep blue theme
- RTL support
- Advanced admin panel
- User management
- Server management
- Card management
- Points system
- Live chat
- Financial reports
- License management
- Analytics

### ⚙️ Technical Features
- Multiple 3x-UI panel integration
- Secure payment system
- Card data encryption
- Receipt protection
- Automatic backups
- Server monitoring
- License system
- Advanced security
- Performance optimization
- Docker support

## 🚀 Installation

### Prerequisites
- Ubuntu 22.04 server
- Docker and Docker Compose
- Domain or public IP
- Minimum 2GB RAM
- 20GB SSD space

### Setup
1. Clone the repository:
```bash
git clone https://github.com/yourusername/mrjbot.git
cd mrjbot
```

2. Configure environment variables:
```bash
cp .env.example .env
# Edit .env file with your settings
```

3. Start with Docker:
```bash
docker-compose up -d
```

4. Run initial commands:
```bash
docker-compose exec backend python manage.py migrate
docker-compose exec backend python manage.py createsuperuser
```

5. Configure SSL:
```bash
./mrjbot setup-ssl
```

6. Set up license:
```bash
./mrjbot set-license YOUR-LICENSE-KEY
```

## 🛠️ Management Commands

### Main Commands
```bash
./mrjbot start          # Start services
./mrjbot stop           # Stop services
./mrjbot restart        # Restart services
./mrjbot status         # Check service status
./mrjbot logs           # View logs
```

### Backup Commands
```bash
./mrjbot backup         # Create backup
./mrjbot restore        # Restore from backup
./mrjbot list-backups   # List backups
```

### Management Commands
```bash
./mrjbot update         # Update system
./mrjbot check-points   # Check points
./mrjbot monitor        # Monitor servers
./mrjbot report         # Financial reports
```

## 🔒 Security

### Security Features
- Sensitive data encryption
- DDoS protection
- Web Application Firewall
- IP whitelisting
- Two-factor authentication
- Card encryption
- Receipt protection

### Backup System
- Daily automatic backups
- Cloud storage
- Encrypted backups
- Quick recovery
- Backup history

## 💰 Payment System

### Payment Methods
- Card-to-card with owner tracking
- Zarinpal gateway
- Internal wallet
- Points system

### Payment Features
- Automatic transaction verification
- Commission system
- Financial reports
- Transaction history
- Card management

## 🎯 Points System

### Earning Points
- Account purchases
- User referrals
- System usage
- Support chat activity

### Using Points
- Purchase discounts
- VIP status upgrade
- Direct purchases
- Special rewards

## 💬 Live Chat Support

### Features
- Real-time support
- Operator transfer
- Chat history
- File sharing
- Auto-responses

### Management
- Operator panel
- Response statistics
- Service quality
- Performance reports

## 📊 Reports and Analytics

### Financial Reports
- Daily/weekly/monthly sales
- Card transactions
- Commissions
- Profit/loss

### System Statistics
- Server status
- Traffic usage
- User count
- System performance

## 🔄 Updates

### Update System
- Automatic updates
- Pre-update backups
- Telegram notifications
- Error recovery

### Update Commands
```bash
./mrjbot update         # Update system
./mrjbot update-check   # Check for updates
./mrjbot rollback       # Rollback to previous version
```

## 📱 Future Versions

### New Features
- OpenVPN support
- Apple ID account sales
- PUBG UC sales
- Mobile app
- Desktop app

### Improvements
- New UI
- Faster performance
- Enhanced security
- New capabilities

## 📝 Documentation

### Guides
- Installation guide
- User guide
- Admin guide
- Developer guide

### Tutorials
- Setup tutorial
- Usage tutorial
- Management tutorial
- Development tutorial

## 🤝 Contributing

### How to Contribute
- Report bugs
- Suggest features
- Submit code
- Improve documentation

### Guidelines
- Clean code
- Complete testing
- Updated docs
- Follow standards

## 📄 License

### License Types
- Free version
- Professional version
- Enterprise version
- Custom version

### License Features
- User limits
- Server limits
- API limits
- Special support

## 📞 Support

### Contact Methods
- Telegram
- Email
- Ticket system
- Live chat

### Response Times
- 24/7 technical support
- 9 AM to 9 PM general support
- Holiday support
- Emergency support
