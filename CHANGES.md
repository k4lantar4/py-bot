# Changes and Development Notes

## Development Decisions

### Architecture
- Implemented a modular architecture with clear separation between backend, frontend, and Telegram bot components
- Used FastAPI for backend due to its performance, type hinting, and automatic documentation generation
- Chose React with MUI for frontend to provide a responsive, modern UI with minimal development effort
- Implemented a microservices-like approach with separate modules for each feature that can be toggled via configuration

### Database Design
- Used PostgreSQL with SQLAlchemy ORM for robust data storage with transaction support
- Implemented separate tables for locations, servers, services, users, discounts, orders, and payments
- Added foreign key constraints to maintain data integrity
- Used Redis for caching and session management to improve performance

### Security Considerations
- Implemented JWT authentication with refresh token mechanism
- Added role-based access control (RBAC) with customizable permissions
- Used Pydantic models for request validation to prevent injection attacks
- Stored credentials and sensitive data in environment variables
- Implemented rate limiting for API endpoints to prevent abuse
- Added 2FA support for enhanced security

### Integration with 3X-UI
- Used async/await for API calls to 3X-UI panels
- Stored session cookies in Redis with automatic refresh mechanism
- Implemented fallback mechanisms for when 3X-UI panels are unreachable
- Added periodic health checks for server status monitoring

## Assumptions

### 3X-UI Integration
- Assumed 3X-UI panels are accessible via HTTP/HTTPS
- Assumed 3X-UI API stays compatible with our implementation
- Assumed each server has a unique domain/IP address

### User Management
- Assumed users will have unique email addresses and usernames
- Assumed a hierarchical role system (admin > vendor > user)
- Assumed email notifications are required for important actions

### Performance
- Assumed moderate user load (up to 10,000 users)
- Assumed up to 100 concurrent API requests
- Designed Redis caching to handle high-traffic scenarios

### Deployment
- Assumed deployment on Ubuntu 22.04+ servers
- Assumed availability of PostgreSQL, Redis, and Node.js on the deployment server
- Assumed the system will run behind a reverse proxy (like Nginx)

### AI Features
- Implemented basic ML models for user behavior analysis and plan suggestions
- Assumed periodic batch processing for AI model training
- Used scikit-learn for ML implementations due to its simplicity and effectiveness 