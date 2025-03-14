# 🤖 Telegram Bot & Dashboard for V2Ray Management

## 🌟 Key Features

### 💰 Smart Payment System
- Card-to-card payments with owner tracking
- Zarinpal payment gateway
- Admin/seller payment confirmation
- Advanced financial reporting
- Transaction history
- Card owner analytics

### ✨ Points & Rewards System
- Points earning from purchases
- Referral and reward system
- VIP levels
- Points to discount conversion
- Points history
- `mrjbot check-points` command

### 💬 Live Support
- Direct chat in Telegram
- Ticket system
- Operator management
- Chat history
- Quick responses
- Performance metrics

### 🎯 Smart Plan Suggestions
- Usage analysis
- Plan recommendations
- Traffic optimization
- Custom plans
- Plan comparison

### 🖥️ Server Management
- Multiple 3x-UI panel integration
- Server health monitoring
- Automatic load balancing
- Multi-server support
- Performance metrics
- Automatic alerts

### 👥 User Management
- Multiple roles (Admin, Seller, VIP)
- Advanced access control
- User profiles
- Activity history
- Operator management

## 🚀 Installation & Setup

### Prerequisites
- Ubuntu 22.04 server
- Domain or public IP
- Docker and Docker Compose

### Quick Installation
```bash
# Get the code
git clone https://github.com/yourusername/mrjbot.git
cd mrjbot

# Configure .env file
cp .env.example .env
nano .env

# Start with Docker
docker-compose up -d

# Install CLI
chmod +x mrjbot
sudo cp mrjbot /usr/local/bin/
```

### CLI Commands
```bash
# Installation
mrjbot install

# Update
mrjbot update

# Backup
mrjbot backup

# Check points
mrjbot check-points

# Set license
mrjbot set-license <code>

# Server management
mrjbot server <command>

# Analytics
mrjbot analytics <command>
```

## 🛡️ Security & Support

### Security Features
- HTTPS
- JWT authentication
- Data encryption
- API rate limiting
- IP filtering
- Two-factor authentication

### Support
- 24/7 support
- Live chat in Telegram
- Ticket system
- Persian guide
- Video tutorials

## 🔄 Updates & Maintenance

### Update System
- Automatic updates
- Config backup
- Database backup
- Auto recovery
- Telegram notifications

### Monitoring
- Server health
- Resource usage
- Traffic
- Errors
- Performance

## 📱 Access

### Web Dashboard
- URL: `https://your-domain.com`
- Persian UI
- Responsive design
- Dark/light theme

### Telegram Bot
- Username: `@your_bot_username`
- Persian commands
- User-friendly menu
- Smart responses

## 🔮 Future Development

### New Features
- OpenVPN support
- Apple ID account sales
- PUBG UC integration
- Crypto payments
- AI-powered support

### Improvements
- Performance optimization
- New UI
- Advanced reports
- Mobile app

## 📝 Important Notes

### Best Practices
- Use dedicated server
- Configure SSL
- Regular backups
- Continuous monitoring
- Keep updated

### Limitations
- Requires powerful server
- API limitations
- Payment restrictions
- Traffic limits

## 🤝 Contributing

### Developers
- Contribution guide
- Coding standards
- Unit tests
- API documentation

### Bug Reports
- Issue system
- Report guidelines
- Report template
- Prioritization

## 📄 License

### License Types
- Free version
- Professional version
- Enterprise version
- Custom version

### Usage Terms
- User limitations
- Server limitations
- API limitations
- Support limitations

## 📞 Contact Us

### Communication Channels
- Telegram: `@your_support_username`
- Email: `support@your-domain.com`
- Website: `https://your-domain.com`
- Live chat: On website

### Support Hours
- Support: 24/7
- Sales: 9 AM to 9 PM
- Technical: 9 AM to 6 PM
- Management: 9 AM to 5 PM

## Testing

### Component Tests

To verify that all components of the system are working correctly, you can use the test script:

```bash
# Run tests directly against a running system
python test_components.py

# Or use the dedicated testing Docker Compose setup
docker-compose -f docker-compose-testing.yml up
```

For Unix-based systems (Linux/macOS), you can use the included test runner script:
```bash
# Make the script executable first
chmod +x run_tests.sh

# Run the tests
./run_tests.sh
```

> Note: On Windows, use PowerShell or WSL to run the Docker Compose commands directly.

This will test connections to:
- PostgreSQL database
- Redis
- Backend API health endpoint

The test script will retry connections multiple times before failing, which is helpful during initial startup when services might take time to initialize.

### Running Backend Tests

To run Django unit tests:

```bash
# Navigate to the backend directory
cd backend

# Run the tests
python manage.py test
```

## Troubleshooting

### Django Module Import Issues

If you encounter errors with modules not being found, such as `django-environ` or `model_utils`, try these steps:

1. Verify that all dependencies are installed:
   ```bash
   # In the backend container
   docker exec -it mrjbot_backend pip install -r requirements.txt
   
   # Specifically install problematic packages
   docker exec -it mrjbot_backend pip install django-environ django-model-utils
   ```

2. If the settings module can't be found, try using the test settings:
   ```bash
   # Update the environment variable
   docker exec -it mrjbot_backend bash -c "export DJANGO_SETTINGS_MODULE=config.test_settings"
   ```

3. Check that the PYTHONPATH is correctly set:
   ```bash
   # Inside the container
   docker exec -it mrjbot_backend bash -c "echo $PYTHONPATH"
   ```

### Database Connection Issues

If you see database connection errors:

1. Verify that the PostgreSQL server is running:
   ```bash
   docker ps | grep postgres
   ```

2. Check the connection settings:
   ```bash
   # Inside the backend container
   docker exec -it mrjbot_backend bash -c "env | grep DB_"
   ```

3. Try connecting manually:
   ```bash
   docker exec -it mrjbot_postgres psql -U mrjbot -d mrjbot
   ```

4. Ensure that your application is using the correct port:
   - Inside Docker network: Port 5432
   - From host machine: Port 5433

### Redis Connection Issues

If Redis connections fail:

1. Verify that the Redis server is running:
   ```bash
   docker ps | grep redis
   ```

2. Try connecting manually:
   ```bash
   docker exec -it mrjbot_redis redis-cli ping
   ```

3. Check if Redis is responsive:
   ```bash
   docker exec -it mrjbot_redis redis-cli info
   ```

### Testing the Core Components Separately

You can test the core components separately using our simplified test script:

```bash
# Run the simplified test
docker-compose -f docker-compose-simple-test.yml up
```

This will test only the PostgreSQL and Redis connections without depending on the Django backend, which is useful for isolating issues.

## Monitoring & Observability

### System Monitoring Dashboard

MRJBot comes with a comprehensive monitoring dashboard that provides real-time insights into the health and performance of your system. Access it at:

```
https://your-domain.com/admin/monitoring/
```

> Note: You must be logged in as a staff member to access the dashboard.

The dashboard includes:
- System metrics (CPU, memory, disk usage)
- Database statistics and performance
- Redis cache usage and statistics
- Docker container status and resource usage

### Metrics APIs

For programmatic access or integration with other monitoring tools, MRJBot provides several metrics endpoints:

```
# Health check endpoint
GET /api/health/

# Container metrics
GET /api/metrics/containers/

# Database metrics
GET /api/metrics/database/

# Redis metrics
GET /api/metrics/redis/

# System metrics
GET /api/metrics/system/
```

These endpoints require authentication and return detailed JSON metrics about the system.

### Automated Monitoring

You can set up automated monitoring by:
1. Using a monitoring service like Prometheus, Grafana, or Datadog
2. Creating cron jobs that check the health endpoint
3. Setting up alerts for critical metrics

Example cron job to check health and send notifications:
```bash
# Check every 5 minutes
*/5 * * * * curl -s -f https://your-domain.com/api/health/ || telegram-send "System health check failed!"
```
