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
- [ ] Create API endpoints for bot and frontend
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
- [ ] Task: Documentation - Status: Not started
- [ ] Task: Deployment scripts - Status: Not started 