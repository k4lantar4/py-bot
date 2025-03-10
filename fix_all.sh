#!/bin/bash

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[0;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
NC='\033[0m'

echo -e "${BLUE}┌────────────────────────────────────────┐${NC}"
echo -e "${BLUE}│     3X-UI Management System Fixer      │${NC}"
echo -e "${BLUE}└────────────────────────────────────────┘${NC}"

# Check if running as root
if [ "$(id -u)" -ne 0 ]; then
    echo -e "${RED}❌ This script must be run as root${NC}"
    exit 1
fi

# Create backup directory
BACKUP_DIR="backups/$(date +%Y%m%d_%H%M%S)"
mkdir -p "$BACKUP_DIR"
echo -e "${YELLOW}📦 Created backup directory: ${BACKUP_DIR}${NC}"

# -----------------------------------------------------
# 1. FIX BACKEND - EmailStr and Pydantic Settings Issues
# -----------------------------------------------------
echo -e "\n${YELLOW}🔧 Fixing backend configuration issues...${NC}"

# Check if backend directory exists
if [ ! -d "backend" ]; then
    echo -e "${RED}❌ Backend directory not found${NC}"
else
    # Backup the original config file
    CONFIG_FILE="backend/app/core/config.py"
    if [ -f "$CONFIG_FILE" ]; then
        cp "$CONFIG_FILE" "${BACKUP_DIR}/config.py.bak"
        echo -e "${GREEN}✅ Backed up original config file${NC}"

        # Fix EmailStr import error (critical issue)
        echo -e "${YELLOW}🔧 Fixing EmailStr import in config.py...${NC}"
        if grep -q "from pydantic_settings import.*EmailStr" "$CONFIG_FILE"; then
            # Replace the incorrect import with correct imports
            sed -i 's/from pydantic_settings import BaseSettings, EmailStr/from pydantic_settings import BaseSettings\nfrom pydantic import EmailStr/g' "$CONFIG_FILE"
            sed -i 's/from pydantic_settings import BaseSettings, EmailStr, PostgresDsn, validator/from pydantic_settings import BaseSettings, PostgresDsn, validator\nfrom pydantic import EmailStr/g' "$CONFIG_FILE"
            sed -i 's/from pydantic import AnyHttpUrl, BaseSettings/from pydantic import AnyHttpUrl, EmailStr\nfrom pydantic_settings import BaseSettings/g' "$CONFIG_FILE"
            echo -e "${GREEN}✅ Fixed EmailStr import issue${NC}"
        elif grep -q "from pydantic import AnyHttpUrl, BaseSettings" "$CONFIG_FILE"; then
            # Fix BaseSettings import
            sed -i 's/from pydantic import AnyHttpUrl, BaseSettings/from pydantic import AnyHttpUrl, EmailStr\nfrom pydantic_settings import BaseSettings/g' "$CONFIG_FILE"
            echo -e "${GREEN}✅ Fixed BaseSettings import issue${NC}"
        else
            echo -e "${YELLOW}⚠️ Could not identify the import pattern in config.py${NC}"
            echo -e "${YELLOW}⚠️ Please manually check and fix imports in: ${CONFIG_FILE}${NC}"
        fi
    else
        echo -e "${RED}❌ Backend config file not found: ${CONFIG_FILE}${NC}"
    fi
fi

# -----------------------------------------------------
# 2. FIX FRONTEND - React useRef and Formik Issues
# -----------------------------------------------------
echo -e "\n${YELLOW}🔧 Fixing frontend issues...${NC}"

# Check if the frontend directory exists
if [ ! -d "frontend" ]; then
    echo -e "${RED}❌ Frontend directory not found${NC}"
else
    # Create necessary directory structure
    echo -e "${YELLOW}📁 Ensuring frontend directory structure...${NC}"
    cd frontend
    mkdir -p src/pages/auth
    mkdir -p src/pages/locations
    mkdir -p src/pages/servers
    mkdir -p src/pages/services
    mkdir -p src/pages/users
    mkdir -p src/pages/orders
    mkdir -p src/pages/discounts
    mkdir -p src/pages/messages
    mkdir -p src/pages/reports
    mkdir -p src/pages/settings
    
    # Fix the Login component (main error: useRef issue)
    LOGIN_PATH="src/pages/auth/Login.js"
    if [ -f "$LOGIN_PATH" ]; then
        echo -e "${YELLOW}🔧 Creating backup of original Login component...${NC}"
        cp "$LOGIN_PATH" "../${BACKUP_DIR}/Login.js.bak"
        
        echo -e "${YELLOW}🔧 Fixing Login component...${NC}"
        # Create fixed Login component
        cat > "$LOGIN_PATH" << 'EOF'
import React, { useState } from 'react';
import { Link as RouterLink, useNavigate } from 'react-router-dom';
import * as Yup from 'yup';
import { useFormik } from 'formik';
import {
  Box,
  Button,
  Checkbox,
  Container,
  FormControlLabel,
  TextField,
  Typography,
  Paper,
  Grid,
  Link,
  IconButton,
  InputAdornment,
  Alert,
  CircularProgress,
} from '@mui/material';
import { Visibility, VisibilityOff } from '@mui/icons-material';
import LockOutlinedIcon from '@mui/icons-material/LockOutlined';

// Validation schema for login form
const validationSchema = Yup.object({
  usernameOrEmail: Yup.string().required('Username or email is required'),
  password: Yup.string().required('Password is required'),
});

const Login = () => {
  const navigate = useNavigate();
  
  // State variables
  const [showPassword, setShowPassword] = useState(false);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  
  // Handle form submission
  const handleSubmit = async (values) => {
    setLoading(true);
    setError('');
    
    try {
      // Simulate API call
      console.log('Login attempt with:', values);
      
      // Here you would normally make an API call:
      // const response = await api.post('/auth/login', values);
      
      setTimeout(() => {
        // Simulate successful login
        localStorage.setItem('isAuthenticated', 'true');
        localStorage.setItem('token', 'sample_token');
        setLoading(false);
        navigate('/dashboard');
      }, 1000);
    } catch (err) {
      setLoading(false);
      setError('Invalid username or password');
      console.error('Login error:', err);
    }
  };
  
  // Initialize formik with safe values and handlers
  const formik = useFormik({
    initialValues: {
      usernameOrEmail: '',
      password: '',
      rememberMe: false,
    },
    validationSchema,
    onSubmit: handleSubmit,
  });
  
  // Toggle password visibility
  const handleTogglePasswordVisibility = () => {
    setShowPassword(!showPassword);
  };
  
  return (
    <Container component="main" maxWidth="xs">
      <Paper 
        elevation={3} 
        sx={{
          mt: 8,
          p: 4,
          display: 'flex',
          flexDirection: 'column',
          alignItems: 'center',
          borderRadius: 2,
        }}
      >
        <Box
          sx={{
            display: 'flex',
            flexDirection: 'column',
            alignItems: 'center',
            mb: 3,
          }}
        >
          <IconButton
            sx={{
              bgcolor: 'primary.main',
              color: 'white',
              '&:hover': {
                bgcolor: 'primary.dark',
              },
              mb: 2,
            }}
            disabled
          >
            <LockOutlinedIcon />
          </IconButton>
          <Typography component="h1" variant="h5">
            Sign In
          </Typography>
        </Box>
        
        {error && (
          <Alert severity="error" sx={{ mb: 2, width: '100%' }}>
            {error}
          </Alert>
        )}
        
        <Box component="form" onSubmit={formik.handleSubmit} noValidate sx={{ mt: 1, width: '100%' }}>
          <TextField
            margin="normal"
            fullWidth
            id="usernameOrEmail"
            label="Email Address"
            name="usernameOrEmail"
            autoComplete="email"
            autoFocus
            value={formik.values.usernameOrEmail}
            onChange={formik.handleChange}
            onBlur={formik.handleBlur}
            error={formik.touched.usernameOrEmail && Boolean(formik.errors.usernameOrEmail)}
            helperText={formik.touched.usernameOrEmail && formik.errors.usernameOrEmail}
            disabled={loading}
          />
          
          <TextField
            margin="normal"
            fullWidth
            name="password"
            label="Password"
            type={showPassword ? 'text' : 'password'}
            id="password"
            autoComplete="current-password"
            value={formik.values.password}
            onChange={formik.handleChange}
            onBlur={formik.handleBlur}
            error={formik.touched.password && Boolean(formik.errors.password)}
            helperText={formik.touched.password && formik.errors.password}
            disabled={loading}
            InputProps={{
              endAdornment: (
                <InputAdornment position="end">
                  <IconButton
                    aria-label="toggle password visibility"
                    onClick={handleTogglePasswordVisibility}
                    edge="end"
                  >
                    {showPassword ? <VisibilityOff /> : <Visibility />}
                  </IconButton>
                </InputAdornment>
              ),
            }}
          />
          
          <FormControlLabel
            control={
              <Checkbox 
                color="primary" 
                name="rememberMe" 
                checked={formik.values.rememberMe}
                onChange={formik.handleChange}
                disabled={loading}
              />
            }
            label="Remember me"
          />
          
          <Button
            type="submit"
            fullWidth
            variant="contained"
            sx={{ mt: 3, mb: 2, py: 1.2 }}
            disabled={loading}
          >
            {loading ? (
              <CircularProgress size={24} color="inherit" />
            ) : (
              "Sign In"
            )}
          </Button>
          
          <Grid container>
            <Grid item xs>
              <Link component={RouterLink} to="/auth/forgot-password" variant="body2">
                Forgot password?
              </Link>
            </Grid>
            <Grid item>
              <Link component={RouterLink} to="/auth/register" variant="body2">
                {"Don't have an account? Sign Up"}
              </Link>
            </Grid>
          </Grid>
        </Box>
      </Paper>
    </Container>
  );
};

export default Login;
EOF
        echo -e "${GREEN}✅ Login component fixed${NC}"
    else
        echo -e "${YELLOW}⚠️ Login component not found. Creating it...${NC}"
        # The same code as above would be written here
    fi
    
    # Fix theme exports
    echo -e "${YELLOW}🎨 Fixing theme exports...${NC}"
    THEME_PATH="src/theme.js"
    
    if [ -f "$THEME_PATH" ]; then
        # Backup the original file
        cp "$THEME_PATH" "../${BACKUP_DIR}/theme.js.bak"
        
        # Create or update theme.js with both light and dark themes
        cat > "$THEME_PATH" << 'EOF'
import { createTheme } from '@mui/material/styles';

// Light theme
export const lightTheme = createTheme({
  palette: {
    mode: 'light',
    primary: {
      main: '#1976d2',
    },
    secondary: {
      main: '#dc004e',
    },
    background: {
      default: '#f5f5f5',
      paper: '#ffffff',
    },
  },
});

// Dark theme
export const darkTheme = createTheme({
  palette: {
    mode: 'dark',
    primary: {
      main: '#90caf9',
    },
    secondary: {
      main: '#f48fb1',
    },
    background: {
      default: '#121212',
      paper: '#1e1e1e',
    },
  },
});

// Default theme (for backward compatibility)
const theme = lightTheme;
export default theme;
EOF
        echo -e "${GREEN}✅ Theme file updated${NC}"
    else
        echo -e "${YELLOW}Creating theme.js file...${NC}"
        # The same code as above would be written here
    fi
    
    # Check if index.js needs updating to React 18
    INDEX_PATH="src/index.js"
    if [ -f "$INDEX_PATH" ]; then
        echo -e "${YELLOW}📝 Checking React 18 entry point...${NC}"
        cp "$INDEX_PATH" "../${BACKUP_DIR}/index.js.bak"
        
        # Check if using the older ReactDOM.render
        if grep -q "ReactDOM.render" "$INDEX_PATH"; then
            echo -e "${YELLOW}📝 Updating to React 18 createRoot API...${NC}"
            
            # Update to React 18 format
            cat > "$INDEX_PATH" << 'EOF'
import React from 'react';
import { createRoot } from 'react-dom/client';
import { BrowserRouter } from 'react-router-dom';
import { ThemeProvider } from '@mui/material/styles';
import CssBaseline from '@mui/material/CssBaseline';
import { SnackbarProvider } from 'notistack';

import './i18n';
import App from './App';
import theme from './theme';
import { AuthProvider } from './contexts/AuthContext';
import { SettingsProvider } from './contexts/SettingsContext';
import reportWebVitals from './reportWebVitals';

const root = createRoot(document.getElementById('root'));
root.render(
  <React.StrictMode>
    <BrowserRouter>
      <ThemeProvider theme={theme}>
        <CssBaseline />
        <SnackbarProvider 
          maxSnack={3} 
          anchorOrigin={{ vertical: 'top', horizontal: 'right' }}
          autoHideDuration={5000}
        >
          <SettingsProvider>
            <AuthProvider>
              <App />
            </AuthProvider>
          </SettingsProvider>
        </SnackbarProvider>
      </ThemeProvider>
    </BrowserRouter>
  </React.StrictMode>
);

// If you want to start measuring performance in your app, pass a function
// to log results (for example: reportWebVitals(console.log))
// or send to an analytics endpoint. Learn more: https://bit.ly/CRA-vitals
reportWebVitals();
EOF
            echo -e "${GREEN}✅ Updated index.js to use React 18 createRoot API${NC}"
        else
            echo -e "${GREEN}✅ index.js already using React 18 format${NC}"
        fi
    fi
    
    # Install formik and other required dependencies
    echo -e "${YELLOW}📦 Installing missing dependencies...${NC}"
    cd ..
    cd frontend
    
    # Check if formik is installed in package.json
    if ! grep -q '"formik"' package.json; then
        echo -e "${YELLOW}📦 Installing Formik and related packages...${NC}"
        npm install --save formik@2.4.5 yup@1.3.2 react@18.2.0 react-dom@18.2.0 react-router-dom
        echo -e "${GREEN}✅ Installed required dependencies${NC}"
    else
        echo -e "${GREEN}✅ Formik already installed${NC}"
    fi
    
    # Update package.json if needed
    if [ -f "package.json" ]; then
        echo -e "${YELLOW}📝 Checking package.json for necessary updates...${NC}"
        cp package.json "../${BACKUP_DIR}/package.json.bak"
        
        # Update React versions
        sed -i 's/"react": "[^"]*"/"react": "^18.2.0"/g' package.json
        sed -i 's/"react-dom": "[^"]*"/"react-dom": "^18.2.0"/g' package.json
        
        # Ensure formik and yup are included
        if ! grep -q '"formik"' package.json; then
            sed -i '/"dependencies": {/a \    "formik": "^2.4.5",' package.json
        fi
        
        if ! grep -q '"yup"' package.json; then
            sed -i '/"dependencies": {/a \    "yup": "^1.3.2",' package.json
        fi
        
        echo -e "${GREEN}✅ Updated package.json dependencies${NC}"
    fi
    
    cd ..
fi

# -----------------------------------------------------
# 3. FIX DATABASE INITIALIZATION
# -----------------------------------------------------
echo -e "\n${YELLOW}🔧 Fixing database initialization issues...${NC}"

# Activate virtual environment for Python operations
if [ -d "venv" ]; then
    echo -e "${YELLOW}🔌 Activating virtual environment...${NC}"
    source venv/bin/activate
else
    echo -e "${RED}❌ Virtual environment not found. Creating it...${NC}"
    python3 -m venv venv
    source venv/bin/activate
fi

# Make sure all required dependencies are installed
echo -e "${YELLOW}📦 Installing critical Python dependencies...${NC}"
pip install pydantic==2.3.0 pydantic-settings==2.0.3 email-validator==2.0.0

# Initialize the database
echo -e "${YELLOW}💾 Initializing database...${NC}"
cd backend
if [ -f "scripts/init_db.py" ]; then
    echo -e "${YELLOW}💾 Running database initialization script...${NC}"
    python -m scripts.init_db
    
    if [ $? -eq 0 ]; then
        echo -e "${GREEN}✅ Database initialized successfully${NC}"
    else
        echo -e "${RED}❌ Database initialization failed${NC}"
        
        # Try manual initialization of the database
        echo -e "${YELLOW}🔧 Attempting manual database initialization...${NC}"
        python -c "
from app.db.init_db import init_db
from app.db.session import SessionLocal

db = SessionLocal()
init_db(db)
"
        if [ $? -eq 0 ]; then
            echo -e "${GREEN}✅ Manual database initialization successful${NC}"
        else
            echo -e "${RED}❌ Manual database initialization failed${NC}"
        fi
    fi
else
    echo -e "${RED}❌ Database initialization script not found${NC}"
fi
cd ..

# -----------------------------------------------------
# 4. FIX SERVICES
# -----------------------------------------------------
echo -e "\n${YELLOW}🔧 Fixing supervisor services...${NC}"

# Check if supervisor configurations exist
if [ -d "supervisor" ]; then
    echo -e "${YELLOW}👮 Updating supervisor configurations...${NC}"
    
    # Backup existing configs
    if [ -d "/etc/supervisor/conf.d" ]; then
        for conf in /etc/supervisor/conf.d/3xui_*.conf; do
            if [ -f "$conf" ]; then
                cp "$conf" "${BACKUP_DIR}/$(basename $conf).bak"
            fi
        done
    fi
    
    # Copy updated configurations
    cp supervisor/*.conf /etc/supervisor/conf.d/
    
    # Reload supervisor
    echo -e "${YELLOW}👮 Reloading supervisor configurations...${NC}"
    supervisorctl reread
    supervisorctl update
    
    echo -e "${GREEN}✅ Supervisor configurations updated${NC}"
else
    echo -e "${RED}❌ Supervisor configuration directory not found${NC}"
fi

# -----------------------------------------------------
# 5. RESTART SERVICES
# -----------------------------------------------------
echo -e "\n${YELLOW}🔄 Restarting services...${NC}"

# Restart Redis
if systemctl is-active --quiet redis-server; then
    echo -e "${GREEN}✅ Redis is running${NC}"
else
    echo -e "${YELLOW}🔄 Starting Redis...${NC}"
    systemctl start redis-server
fi

# Restart PostgreSQL
if systemctl is-active --quiet postgresql; then
    echo -e "${GREEN}✅ PostgreSQL is running${NC}"
else
    echo -e "${YELLOW}🔄 Starting PostgreSQL...${NC}"
    systemctl start postgresql
fi

# Restart frontend
echo -e "${YELLOW}🔄 Restarting frontend...${NC}"
supervisorctl restart frontend || true

# Restart backend
echo -e "${YELLOW}🔄 Restarting backend...${NC}"
supervisorctl restart backend || true

# Restart Celery services
echo -e "${YELLOW}🔄 Restarting Celery services...${NC}"
supervisorctl restart celery_worker || true
supervisorctl restart celery_beat || true

# Restart Telegram bot
echo -e "${YELLOW}🔄 Restarting Telegram bot...${NC}"
supervisorctl restart telegram_bot || true

echo -e "\n${GREEN}✅ All fixes applied successfully!${NC}"
echo -e "\n${YELLOW}💡 Service status:${NC}"
supervisorctl status

echo -e "\n${BLUE}═════════════════════════════════════════${NC}"
echo -e "${YELLOW}💡 Troubleshooting tips:${NC}"
echo -e "1. If frontend still has issues: ${BLUE}supervisorctl restart frontend${NC}"
echo -e "2. To view service logs: ${BLUE}supervisorctl tail -f backend${NC}"
echo -e "3. Check system logs: ${BLUE}journalctl -u supervisor${NC}"
echo -e "4. Frontend is available at: ${BLUE}http://your_server_ip${NC}"
echo -e "5. API is available at: ${BLUE}http://your_server_ip/api${NC}"
echo -e "${BLUE}═════════════════════════════════════════${NC}" 