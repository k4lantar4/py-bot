# 3X-UI Management System

A comprehensive management system for 3X-UI panels with user management, role-based access control, and API integration.

## Features

- **User Management**: Create, update, and delete users with role-based access control
- **Authentication**: JWT-based authentication with refresh tokens
- **Role Management**: Assign roles to users with different permissions
- **API Integration**: RESTful API for integration with other systems
- **Redis Caching**: Efficient caching for improved performance
- **Logging**: Comprehensive logging for monitoring and debugging

## Backend Technology Stack

- **Framework**: FastAPI
- **Database**: PostgreSQL with SQLAlchemy ORM
- **Authentication**: JWT tokens with refresh capability
- **Caching**: Redis
- **Task Queue**: Celery (for background tasks)

## Frontend Technology Stack

- **Framework**: React
- **UI Library**: Material-UI (MUI)
- **State Management**: Redux
- **Routing**: React Router
- **Internationalization**: i18next
- **Charts**: Chart.js

## Getting Started

### Prerequisites

- Python 3.9+
- PostgreSQL
- Redis
- Node.js 16+

### Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/3x-ui-management.git
   cd 3x-ui-management
   ```

2. Set up the backend:
   ```bash
   cd backend
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   pip install -r requirements.txt
   ```

3. Create a `.env` file in the backend directory with the following content:
   ```
   # API settings
   SECRET_KEY=your-secret-key
   
   # Database settings
   POSTGRES_SERVER=localhost
   POSTGRES_USER=postgres
   POSTGRES_PASSWORD=password
   POSTGRES_DB=3xui_management
   
   # Redis settings
   REDIS_HOST=localhost
   REDIS_PORT=6379
   REDIS_DB=0
   
   # First superuser
   FIRST_SUPERUSER_USERNAME=admin
   FIRST_SUPERUSER_EMAIL=admin@example.com
   FIRST_SUPERUSER_PASSWORD=admin
   
   # Environment
   ENVIRONMENT=development
   ```

4. Set up the frontend:
   ```bash
   cd ../frontend
   npm install
   ```

### Running the Application

1. Start the backend:
   ```bash
   cd backend
   uvicorn app.main:app --reload
   ```

2. Start the frontend:
   ```bash
   cd frontend
   npm start
   ```

3. Access the application:
   - Backend API: http://localhost:8000
   - API Documentation: http://localhost:8000/api/docs
   - Frontend: http://localhost:3000

## API Documentation

The API documentation is available at `/api/docs` when the backend is running. It provides detailed information about all available endpoints, request/response schemas, and authentication requirements.

## License

This project is licensed under the MIT License - see the LICENSE file for details. 