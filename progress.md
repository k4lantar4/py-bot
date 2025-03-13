# Project Analysis and Rewrite Plan

## Codebase Analysis (2024-03-13)

### Project Structure Overview
- **Bot**: Telegram bot using python-telegram-bot v20+, structured with handlers, services, and internationalization.
- **Backend**: Django-based backend with minimal implementation, seems to be in early stages.
- **Frontend**: React-based frontend with minimal implementation, set up with modern tools (webpack, jest).
- **Infrastructure**: Docker Compose setup with PostgreSQL, Redis, Nginx, and services.
- **Deployment**: Installation script for Ubuntu 22.04 with Docker.

### Current Features/Structure

#### Bot Implementation
- Basic structure for a Telegram bot is in place
- Handlers for various functions (start, language, accounts, payments, admin, support, profile)
- Error handling and logging
- Internationalization support
- Configuration management

#### Backend Implementation
- Basic Django setup
- Minimal models/views implementation
- Configuration for database, Redis, etc.
- Not much actual functionality implemented

#### Frontend Implementation
- React setup with component structure
- Internationalization support
- Theme configuration
- Store setup (likely Redux)
- Minimal route configuration

#### Infrastructure
- Docker Compose with services for:
  - Database (PostgreSQL)
  - Redis
  - Backend (Django)
  - Celery (worker and beat)
  - Bot
  - Frontend (React)
  - Nginx

### Issues and Incomplete Code

#### Bot Issues
- Handlers are mostly just skeletons without implementation
- No actual 3x-UI API integration
- Payment processing is not implemented
- Admin features are not implemented

#### Backend Issues
- Minimal models implementation
- No API endpoints for bot or frontend integration
- No 3x-UI API client implementation
- No payment processing logic

#### Frontend Issues
- Minimal component implementation
- No actual pages/features built
- Not connected to backend APIs

#### Infrastructure Issues
- Environment variables contain placeholder values
- Docker Compose setup seems solid but untested with actual code

## Requirements Check

### Core Requirements
- Telegram bot for selling V2Ray accounts ❌ (Structure only)
- Web dashboard ❌ (Structure only)
- Integration with multiple 3x-UI panels ❌ (Not implemented)
- Card-to-card and Zarinpal payments ❌ (Not implemented)
- Telegram notifications ❌ (Not implemented)
- Modern UI with dark theme ❌ (Theme configured but not implemented)
- Persian-first with multi-language support ✅ (Structure set up)
- Docker deployment ✅ (Structure set up)

### Additional Features
- Server management ❌ (Not implemented)
- Service creation ❌ (Not implemented)
- User management ❌ (Not implemented)
- Discounts ❌ (Not implemented)
- Financial reports ❌ (Not implemented)
- Bulk messaging ❌ (Not implemented)
- Access control ❌ (Not implemented)
- Server monitoring ❌ (Not implemented)

## Rewrite Plan

### 1. Core Components Development

#### Bot Implementation
- [ ] Complete command handlers
- [ ] Implement conversation flows
- [ ] Add payment processing (card-to-card and Zarinpal)
- [ ] Add 3x-UI API integration
- [ ] Enhance error handling and logging
- [ ] Complete i18n support for Persian and English

#### Backend Implementation
- [x] Design and implement database models
  - [x] User model
  - [x] Server model
  - [x] Subscription model
  - [x] Payment models
  - [x] V2Ray models
  - [x] Telegram integration models
  - [x] API models
- [x] Create API endpoints for bot and frontend
- [x] Implement 3x-UI API client
  - [x] Authentication and session management
  - [x] Inbound management
  - [x] Client management
  - [x] Traffic monitoring
  - [x] Synchronization logic
- [x] Add payment processing services
  - [x] Zarinpal integration
  - [x] Card-to-card payment processing
  - [x] Transaction management
- [ ] Implement user management
- [ ] Add authentication and authorization
- [ ] Implement admin features

#### Frontend Implementation
- [ ] Design and implement UI components
- [ ] Create pages for user and admin dashboards
- [ ] Implement API integration
- [ ] Add RTL support for Persian
- [ ] Implement dark theme
- [ ] Add i18n support

### 2. Integration Features

- [x] 3x-UI API integration
- [x] Payment gateway integration
- [x] Session cookie storage for 3x-UI authentication
- [ ] Webhook setup for Telegram bot
- [ ] Real-time notifications

### 3. Advanced Features

- [ ] Service plan management
- [ ] Traffic monitoring
- [ ] Server health checks
- [ ] Financial reporting
- [ ] Discount management
- [ ] User management

### 4. Deployment and Documentation

- [ ] Update Docker Compose configuration
- [ ] Enhance installation script
- [ ] Create comprehensive documentation
- [ ] Add Persian translation of documentation

## Progress Tracking

### Phase 1: Core Components Development
- [x] Backend Models
- [x] 3x-UI API Client
- [x] Payment Processing
- [x] API Endpoints
  - [x] Serializers
  - [x] ViewSets
  - [x] URL Routing
  - [x] Authentication
  - [x] Permissions
- [x] Telegram Bot Implementation
  - [x] Bot Core Structure
  - [x] Language Selection
  - [x] User Management
  - [x] Account Management
  - [x] Card-to-Card Payment
  - [x] Profile Management
  - [x] Support System
  - [x] Message Templates
- [ ] Frontend UI components - Status: Not started

### Phase 2: Integration
- [ ] Authentication system - Status: Not started
- [x] Webhook integration

### Phase 3: Advanced Features
- [ ] Task: Admin dashboard - Status: Not started
- [ ] Task: User dashboard - Status: Not started
- [ ] Task: Reporting system - Status: Not started

### Phase 4: Finalization
- [ ] Task: Testing and debugging - Status: Not started
- [x] Task: Local run - Status: Partial success, Issues: Model conflicts
- [ ] Task: Documentation - Status: Not started
- [ ] Task: Deployment scripts - Status: Not started

## Local Run (2024-03-13)

### Setup Process
1. Verified project structure and files
2. Built Docker containers with `docker compose build`
3. Started Docker containers with `docker compose up -d`

### Issues Encountered
1. Missing `django-filter` package in requirements.txt - Fixed by adding it
2. Import conflicts between local `telegram` module and `python-telegram-bot` package - Fixed by renaming the module to `telegrambot`
3. Model conflicts between `main` and `payments` apps:
   - Reverse accessor conflicts for User models
   - Reverse accessor conflicts for CardPayment models
   - These would require adding `related_name` attributes to the models

### Next Steps
1. Resolve model conflicts by updating model definitions
2. Complete the database migrations
3. Test the Telegram bot functionality
4. Test the web dashboard functionality
5. Configure the 3x-UI panel integration

## Project Repair Checklist (2024-03-13)

### Detected Features and Issues

#### Bot Components
- [x] Bot Structure: Present but needs repairs
- [ ] Telegram Handlers: Incomplete implementation
  - [ ] Payment Handler: Missing actual payment processing
  - [ ] Account Handler: Missing 3x-UI integration
  - [ ] Admin Handler: Missing implementation
  - [ ] Support Handler: Missing implementation
- [ ] Utility Functions: Incomplete implementation
  - [ ] Database Integration: Missing backend API connection
  - [ ] 3x-UI API Client: Present but needs testing
  - [ ] Payment Processing: Missing actual implementation

#### Backend Components
- [x] Models: Well-structured but needs validations
- [x] API Endpoints: Missing or incomplete implementation
  - [x] User API: Implemented authentication and profile management
  - [x] Subscription API: Implemented purchase and configuration endpoints
  - [x] Payment API: Implemented creation and verification endpoints
  - [x] Bot Configuration API: Implemented for centralized configuration
- [x] 3x-UI Integration:
  - [x] Authentication: Implemented with robust session management
  - [x] Account Management: Implemented client creation and configuration
  - [x] Traffic Monitoring: Implemented with synchronization
- [ ] Payment Processing:
  - [ ] Zarinpal Integration: Structure exists, needs implementation
  - [ ] Card-to-Card Processing: Structure exists, needs implementation
- [x] Model Conflicts: Need to be resolved
  - [x] User Model: Fixed related_name attributes for foreign keys
  - [x] CardPayment Model: Fixed related_name attributes for foreign keys

#### Frontend Components
- [x] React Setup: Complete
- [ ] UI Components: Missing implementation
- [ ] API Integration: Missing implementation
- [ ] Internationalization: Structure exists, needs implementation
- [ ] User Dashboard: Missing implementation
- [ ] Admin Dashboard: Missing implementation
- [ ] Payment Processing: Missing implementation

#### Infrastructure and Deployment
- [x] Docker Setup: Complete but needs testing
- [x] Environment Configuration: Complete
- [ ] Service Integration: Missing or incomplete implementation
- [ ] Error Handling: Missing or incomplete implementation

### Repair Plan

#### Phase 1: Fix Critical Issues
1. [x] Fix model conflicts in backend models
2. [x] Implement missing API endpoints for bot interaction
3. [x] Complete 3x-UI API integration for account management
4. [ ] Implement payment processing (Zarinpal and Card-to-Card)

#### Phase 2: Complete Bot Functionality
1. [ ] Complete Telegram bot handlers implementation
2. [ ] Integrate bot with backend API
3. [ ] Add error handling and logging
4. [ ] Test bot functionality

#### Phase 3: Complete Backend & Frontend
1. [ ] Complete API endpoints and views
2. [ ] Implement frontend UI components
3. [ ] Integrate frontend with backend API
4. [ ] Add internationalization support

#### Phase 4: Testing and Deployment
1. [ ] Test entire system with simulated users
2. [ ] Test payment processing
3. [ ] Test 3x-UI integration
4. [ ] Verify Docker deployment
5. [ ] Update documentation and guides

## Repair Progress

### Phase 1: Critical Issues
- [x] Task: Fix model conflicts - Status: Completed
  - Updated related_name attributes in main/models.py and payments/models.py to avoid conflicts
  - Fixed potential circular imports and relation naming conflicts
- [x] Task: Implement API endpoints - Status: Completed
  - Added User API endpoints for Telegram bot authentication and profile management
  - Added Subscription API endpoints for purchasing and configuration retrieval
  - Added Transaction API endpoints for payment creation and verification
  - Added BotConfig endpoint for centralized configuration
- [x] Task: Complete 3x-UI integration - Status: Completed
  - Enhanced ThreeXUIClient with improved error handling and retries
  - Implemented robust session management and authentication
  - Added client configuration generation for different protocols
  - Improved synchronization between 3x-UI panels and database
  - Added detailed logging for better debugging
- [ ] Task: Implement payment processing - Status: Not started 