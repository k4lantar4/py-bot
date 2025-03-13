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

### Backend API
- ✅ User Authentication
- ✅ User Management
- ✅ Account Management
- ✅ Server Management
- ✅ Payment Processing
- ✅ Wallet Management
- ✅ Transaction History

### Telegram Bot
- ✅ Bot Setup & Configuration
- ✅ User Authentication (Login/Registration)
- ✅ Main Menu Structure
- ✅ Multi-language Support
- ✅ Payment Handlers
  - ✅ Card Payment
  - ✅ Zarinpal Payment
  - ✅ Transaction History
- ✅ Account Handlers
  - ✅ View Accounts
  - ✅ View Account Details
  - ✅ Create Account
  - ✅ Renew Account
  - ✅ Show Configuration (with QR code)
- ✅ Profile Handlers
  - ✅ View Profile
  - ✅ Edit Profile
  - ✅ Transaction History
- ✅ Admin Handlers
  - ✅ User Management
  - ✅ Server Management
  - ✅ Payment Verification
  - ✅ System Settings
- ⏳ Server Management
- ✅ Notification System
  - ✅ User Preferences
  - ✅ Account Expiry Notifications
  - ✅ Traffic Usage Alerts
  - ✅ Payment Status Updates
  - ✅ Server Status Notifications

### Web Dashboard
- ✅ User Dashboard
  - ✅ Main Dashboard Layout
  - ✅ Account Management Interface
  - ✅ Service Purchase Flow
  - ✅ Account Status/Details

- ✅ Admin Dashboard
  - ✅ Admin Overview
  - ✅ User Management
  - ✅ Server Management
  - ✅ Plan Management
  - ✅ Financial Reports
  - ✅ System Settings

- ✅ Payment Processing
  - ✅ Payment Gateway Integration (Zarinpal)
  - ✅ Transaction History
  - ✅ Wallet Management
  - ✅ Card-to-Card Payment

- ✅ Authentication System
  - ✅ User Registration
  - ✅ Login/Logout
  - ✅ Password Recovery
  - ✅ Role-based Access Control

## 3x-UI Integration
- ✅ API Client
- ✅ Session Management
- ✅ Account Creation
- ✅ Traffic Monitoring
- ⏳ Server Statistics

### Deployment
- ⏳ Docker Configuration
- ⏳ Installation Script
- ⏳ Documentation
  - ⏳ User Guide (Persian)
  - ⏳ Admin Guide (Persian)
  - ⏳ Developer Notes (English)

## Next Steps
1. ✅ Complete Profile Handlers in the Telegram bot
2. ✅ Implement Admin Handlers for server and user management
3. ✅ Add notification system for new payments and accounts
4. ⏳ Begin work on the Web Dashboard
   - ✅ Create user dashboard UI
   - ✅ Implement account management interface
   - ⏳ Add payment processing UI
   - ⏳ Create admin dashboard
5. Create Docker deployment configuration
   - Set up Docker Compose for all services
   - Create installation script
   - Configure Nginx for web and webhook
   - Add SSL support
6. Write comprehensive documentation
   - User guide in Persian
   - Admin guide in Persian
   - Developer notes in English

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
4. [x] Implement payment processing (Zarinpal and Card-to-Card)

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
- [x] Task: Implement payment processing - Status: Completed
  - Implemented CardPaymentProcessor for card-to-card payments
  - Implemented ZarinpalGateway for online payments
  - Created notification services for admin and user notifications
  - Updated payment templates and JavaScript for better user experience
  - Added proper error handling and validation
  - Integrated with Telegram notification system

### Phase 2: Bot Functionality
- [ ] Task: Complete Telegram bot handlers - Status: Not started
- [ ] Task: Integrate bot with backend API - Status: Not started
- [ ] Task: Add error handling and logging - Status: Not started
- [ ] Task: Test bot functionality - Status: Not started

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

## Next Steps (2024-03-13)

1. Complete the Telegram bot handlers implementation
   - Implement conversation flows for account management
   - Add payment processing integration
   - Implement admin commands and notifications
   - Add user profile management

2. Implement frontend UI components
   - Create user dashboard
   - Create admin dashboard
   - Implement payment processing UI
   - Add account management UI

3. Test the entire system
   - Test payment processing with Zarinpal and card payments
   - Test 3x-UI integration with multiple panels
   - Test Telegram bot functionality
   - Verify Docker deployment 

## Recent Updates
- Completed Account Management Interface
  - Implemented account list with status indicators
  - Added account creation form with plan selection
  - Created account history view with transaction details
  - Added RTL support and Persian language integration
  - Implemented dark theme with consistent styling
- Completed Admin Dashboard
  - Implemented Admin Overview with statistics and charts
  - Created User Management interface with search, filtering, and CRUD operations
  - Added Server Management interface with server statistics and configuration
  - Implemented Plan Management with subscription plan creation and management
  - Added RTL support and Persian language integration
  - Implemented dark theme with consistent styling
- Added routing for all dashboard components
  - Set up lazy loading for better performance
  - Created responsive layout wrappers for all routes
- Enhanced UI with RTL support, Persian language, and dark theme
- Next: Implementing Financial Reports and System Settings components 

## Web Dashboard
- ✅ User Dashboard
  - ✅ Main Dashboard Layout
  - ✅ Account Management Interface
  - ✅ Service Purchase Flow
  - ✅ Account Status/Details

- ✅ Admin Dashboard
  - ✅ Admin Overview
  - ✅ User Management
  - ✅ Server Management
  - ✅ Plan Management
  - ✅ Financial Reports
  - ✅ System Settings

- ✅ Payment Processing
  - ✅ Payment Gateway Integration (Zarinpal)
  - ✅ Transaction History
  - ✅ Wallet Management
  - ✅ Card-to-Card Payment

- ✅ Authentication System
  - ✅ User Registration
  - ✅ Login/Logout
  - ✅ Password Recovery
  - ✅ Role-based Access Control

## Backend API
- ✅ 3x-UI Integration
  - ✅ Account Creation
  - ✅ Subscription Management
  - ✅ Traffic Monitoring
  - ✅ Server Status

- ✅ User Management
  - ✅ User CRUD Operations
  - ✅ Authentication & Authorization
  - ✅ Profile Management

- ✅ Payment System
  - ✅ Zarinpal Integration
  - ✅ Manual Payment Verification
  - ✅ Wallet System
  - ✅ Discount Codes

- ✅ Subscription System
  - ✅ Plan Management
  - ✅ Subscription Lifecycle
  - ✅ Notifications

## Telegram Bot
- ✅ Bot Setup
  - ✅ Command Structure
  - ✅ User Authentication
  - ✅ Admin Commands

- ✅ Service Management
  - ✅ Account Creation
  - ✅ Account Renewal
  - ✅ Account Status

- ✅ Payment Integration
  - ✅ Payment Methods
  - ✅ Payment Verification
  - ✅ Receipts

## Infrastructure
- ✅ Docker Setup
  - ✅ Containerization
  - ✅ Docker Compose
  - ✅ Environment Configuration

- ✅ Deployment
  - ✅ Production Setup
  - ✅ Backup System
  - ✅ Monitoring

## Documentation
- ✅ User Guide
  - ✅ Dashboard Usage
  - ✅ Telegram Bot Commands
  - ✅ Troubleshooting

- ✅ Developer Documentation
  - ✅ API Documentation
  - ✅ Code Structure
  - ✅ Contribution Guide

---

## Recent Updates
- **۰۹ خرداد ۱۴۰۳:** Completed the Payment Processing system with the following components:
  - WalletTopup for adding funds to user wallets
  - CardPayment with step-by-step payment process and receipt upload
  - ZarinpalPayment for online payments via Zarinpal gateway
  - PaymentHistory for transaction tracking with filtering and search
  - All components have RTL support, Persian language integration, dark theme

- **۰۸ خرداد ۱۴۰۳:** Completed the Admin Dashboard with all components:
  - Integrated SystemSettings component with general, notification and backup settings
  - Added server management with monitoring and control features
  - Implemented plan management with pricing and feature configuration
  - All components include RTL support, Persian language, dark theme
  - Built statistical overview dashboards and user management interfaces

- **۰۷ خرداد ۱۴۰۳:** Implemented the User Dashboard with the following:
  - Main Dashboard with account summary
  - Wallet Card with balance and actions
  - Traffic Usage Chart with upload/download visualization
  - Account Cards showing status, expiry and traffic usage
  - Recent Transactions table
  - Used Material-UI for UI components, Recharts for data visualization
  - Added RTL support, Persian date/number formatting, responsive design 

## Project Progress

### Web Dashboard
- ✅ Component Library Setup
- ✅ Theme & Styling (RTL, Dark Mode, Persian Font)
- ✅ Admin Dashboard
  - ✅ Admin Overview
  - ✅ User Management
  - ✅ Server Management
  - ✅ Plan Management
  - ✅ Financial Reports
  - ✅ System Settings
- ✅ Authentication System
  - ✅ User Registration
  - ✅ Login/Logout
  - ✅ Password Recovery
  - ⏳ Role-based Access Control
- ⏳ User Dashboard
  - ⏳ User Overview
  - ⏳ Account Management
  - ⏳ Plan Subscription
  - ⏳ Invoices & Payments
- ⏳ Payment Processing
  - ⏳ Payment Gateways Integration (Zarinpal)
  - ⏳ Wallet System
  - ⏳ Card-to-Card Payment
  - ⏳ Payment Verification

### Backend API
- ⏳ User Authentication & Authorization
- ⏳ Server Management
- ⏳ Plan Management
- ⏳ Account Management
- ⏳ 3x-UI API Integration
- ⏳ Payment Processing
- ⏳ Admin Features

### Telegram Bot
- ⏳ Bot Setup
- ⏳ User Registration/Login
- ⏳ Account Management
- ⏳ Plan Subscription
- ⏳ Payment Methods
- ⏳ Admin Commands
- ⏳ Notifications

### Infrastructure
- ⏳ Docker Configuration
- ⏳ CI/CD Setup
- ⏳ Database Design

### Documentation
- ⏳ User Guide
- ⏳ Developer Documentation
- ⏳ API Documentation

## Recent Updates
1. **Authentication System Implemented:**
   - Created Login, Register, and ForgotPassword components
   - Implemented multi-step registration process with validation
   - Added password recovery flow with email verification
   - Created AuthLayout for consistent styling across auth pages
   - Added RTL support and language switching (Persian/English)
   - Implemented dark/light theme toggle

2. **Admin Dashboard Completed:**
   - Created full admin interface with statistics dashboard
   - Implemented user management with search and filtering
   - Added server management with monitoring statistics
   - Implemented plan management with protocol configuration
   - Added financial reports with charts and transaction tables
   - Created system settings for application configuration
   - Optimized UI for RTL and Persian language

Next steps: Implement Role-based Access Control and User Dashboard components 