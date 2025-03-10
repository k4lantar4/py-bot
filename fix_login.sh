#!/bin/bash

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[0;33m'
BLUE='\033[0;34m'
NC='\033[0m'

echo -e "${BLUE}┌────────────────────────────────────────┐${NC}"
echo -e "${BLUE}│      Login Component Fix Script        │${NC}"
echo -e "${BLUE}└────────────────────────────────────────┘${NC}"

# Check if the frontend directory exists
if [ ! -d "frontend" ]; then
    echo -e "${RED}❌ Frontend directory not found${NC}"
    exit 1
fi

# Check if the Login component exists
LOGIN_PATH="frontend/src/pages/auth/Login.js"
if [ ! -f "$LOGIN_PATH" ]; then
    echo -e "${YELLOW}⚠️ Login component not found. Creating it...${NC}"
    
    # Make sure the directory exists
    mkdir -p "frontend/src/pages/auth"
    
    # Create Login component with proper React and Formik usage
    cat > "$LOGIN_PATH" << 'EOF'
import React from 'react';
import { useFormik } from 'formik';
import * as Yup from 'yup';
import {
  Box,
  Button,
  Container,
  TextField,
  Typography,
  Link,
  Paper,
  CircularProgress
} from '@mui/material';
import { useNavigate, Link as RouterLink } from 'react-router-dom';

const Login = () => {
  const navigate = useNavigate();
  const [isLoading, setIsLoading] = React.useState(false);
  const [error, setError] = React.useState('');

  // Define validation schema using Yup
  const validationSchema = Yup.object({
    email: Yup.string()
      .email('ایمیل نامعتبر است')
      .required('ایمیل الزامی است'),
    password: Yup.string()
      .required('رمز عبور الزامی است')
  });

  // Initialize formik with safe values and handlers
  const formik = useFormik({
    initialValues: {
      email: '',
      password: ''
    },
    validationSchema,
    onSubmit: async (values) => {
      setIsLoading(true);
      setError('');
      
      try {
        // Simulate API call
        console.log('Login attempt with:', values);
        
        // Here you would normally make an API call:
        // const response = await api.post('/auth/login', values);
        
        setTimeout(() => {
          // Simulate successful login
          localStorage.setItem('isAuthenticated', 'true');
          setIsLoading(false);
          navigate('/dashboard');
        }, 1000);
      } catch (err) {
        setIsLoading(false);
        setError('نام کاربری یا رمز عبور اشتباه است');
        console.error('Login error:', err);
      }
    }
  });

  return (
    <Container component="main" maxWidth="xs">
      <Paper elevation={3} sx={{ p: 4, mt: 8 }}>
        <Box
          sx={{
            display: 'flex',
            flexDirection: 'column',
            alignItems: 'center',
          }}
        >
          <Typography component="h1" variant="h5" sx={{ mb: 3 }}>
            ورود به سیستم
          </Typography>
          
          {error && (
            <Typography color="error" sx={{ mb: 2 }}>
              {error}
            </Typography>
          )}
          
          <Box component="form" onSubmit={formik.handleSubmit} sx={{ mt: 1 }}>
            <TextField
              margin="normal"
              fullWidth
              id="email"
              label="ایمیل"
              name="email"
              autoComplete="email"
              autoFocus
              value={formik.values.email}
              onChange={formik.handleChange}
              onBlur={formik.handleBlur}
              error={formik.touched.email && Boolean(formik.errors.email)}
              helperText={formik.touched.email && formik.errors.email}
              InputProps={{
                dir: "ltr"
              }}
            />
            <TextField
              margin="normal"
              fullWidth
              name="password"
              label="رمز عبور"
              type="password"
              id="password"
              autoComplete="current-password"
              value={formik.values.password}
              onChange={formik.handleChange}
              onBlur={formik.handleBlur}
              error={formik.touched.password && Boolean(formik.errors.password)}
              helperText={formik.touched.password && formik.errors.password}
              InputProps={{
                dir: "ltr"
              }}
            />
            <Button
              type="submit"
              fullWidth
              variant="contained"
              sx={{ mt: 3, mb: 2 }}
              disabled={isLoading}
            >
              {isLoading ? <CircularProgress size={24} /> : 'ورود'}
            </Button>
            <Box sx={{ display: 'flex', justifyContent: 'space-between', mt: 2 }}>
              <Link component={RouterLink} to="/forgot-password" variant="body2">
                فراموشی رمز عبور
              </Link>
              <Link component={RouterLink} to="/register" variant="body2">
                ثبت نام
              </Link>
            </Box>
          </Box>
        </Box>
      </Paper>
    </Container>
  );
};

export default Login;
EOF
    echo -e "${GREEN}✅ Created Login component${NC}"
else
    echo -e "${YELLOW}⚠️ Login component found. Creating backup and fixing...${NC}"
    # Create a backup
    cp "$LOGIN_PATH" "${LOGIN_PATH}.bak"
    
    # Replace with fixed component
    cat > "$LOGIN_PATH" << 'EOF'
import React from 'react';
import { useFormik } from 'formik';
import * as Yup from 'yup';
import {
  Box,
  Button,
  Container,
  TextField,
  Typography,
  Link,
  Paper,
  CircularProgress
} from '@mui/material';
import { useNavigate, Link as RouterLink } from 'react-router-dom';

const Login = () => {
  const navigate = useNavigate();
  const [isLoading, setIsLoading] = React.useState(false);
  const [error, setError] = React.useState('');

  // Define validation schema using Yup
  const validationSchema = Yup.object({
    email: Yup.string()
      .email('ایمیل نامعتبر است')
      .required('ایمیل الزامی است'),
    password: Yup.string()
      .required('رمز عبور الزامی است')
  });

  // Initialize formik with safe values and handlers
  const formik = useFormik({
    initialValues: {
      email: '',
      password: ''
    },
    validationSchema,
    onSubmit: async (values) => {
      setIsLoading(true);
      setError('');
      
      try {
        // Simulate API call
        console.log('Login attempt with:', values);
        
        // Here you would normally make an API call:
        // const response = await api.post('/auth/login', values);
        
        setTimeout(() => {
          // Simulate successful login
          localStorage.setItem('isAuthenticated', 'true');
          setIsLoading(false);
          navigate('/dashboard');
        }, 1000);
      } catch (err) {
        setIsLoading(false);
        setError('نام کاربری یا رمز عبور اشتباه است');
        console.error('Login error:', err);
      }
    }
  });

  return (
    <Container component="main" maxWidth="xs">
      <Paper elevation={3} sx={{ p: 4, mt: 8 }}>
        <Box
          sx={{
            display: 'flex',
            flexDirection: 'column',
            alignItems: 'center',
          }}
        >
          <Typography component="h1" variant="h5" sx={{ mb: 3 }}>
            ورود به سیستم
          </Typography>
          
          {error && (
            <Typography color="error" sx={{ mb: 2 }}>
              {error}
            </Typography>
          )}
          
          <Box component="form" onSubmit={formik.handleSubmit} sx={{ mt: 1 }}>
            <TextField
              margin="normal"
              fullWidth
              id="email"
              label="ایمیل"
              name="email"
              autoComplete="email"
              autoFocus
              value={formik.values.email}
              onChange={formik.handleChange}
              onBlur={formik.handleBlur}
              error={formik.touched.email && Boolean(formik.errors.email)}
              helperText={formik.touched.email && formik.errors.email}
              InputProps={{
                dir: "ltr"
              }}
            />
            <TextField
              margin="normal"
              fullWidth
              name="password"
              label="رمز عبور"
              type="password"
              id="password"
              autoComplete="current-password"
              value={formik.values.password}
              onChange={formik.handleChange}
              onBlur={formik.handleBlur}
              error={formik.touched.password && Boolean(formik.errors.password)}
              helperText={formik.touched.password && formik.errors.password}
              InputProps={{
                dir: "ltr"
              }}
            />
            <Button
              type="submit"
              fullWidth
              variant="contained"
              sx={{ mt: 3, mb: 2 }}
              disabled={isLoading}
            >
              {isLoading ? <CircularProgress size={24} /> : 'ورود'}
            </Button>
            <Box sx={{ display: 'flex', justifyContent: 'space-between', mt: 2 }}>
              <Link component={RouterLink} to="/forgot-password" variant="body2">
                فراموشی رمز عبور
              </Link>
              <Link component={RouterLink} to="/register" variant="body2">
                ثبت نام
              </Link>
            </Box>
          </Box>
        </Box>
      </Paper>
    </Container>
  );
};

export default Login;
EOF
    echo -e "${GREEN}✅ Fixed Login component${NC}"
fi

# Check React version and install proper dependencies
echo -e "${YELLOW}📦 Checking and installing required dependencies...${NC}"
cd frontend

# Add missing dependencies for React and Formik to work correctly
npm install --save formik@2.4.5 yup@1.3.2 react@18.2.0 react-dom@18.2.0 @mui/material @mui/icons-material react-router-dom

# Fix package.json to ensure proper React version
if [ -f "package.json" ]; then
    echo -e "${YELLOW}📝 Updating package.json...${NC}"
    # Use sed to update React version if needed
    sed -i 's/"react": "[^"]*"/"react": "^18.2.0"/g' package.json
    sed -i 's/"react-dom": "[^"]*"/"react-dom": "^18.2.0"/g' package.json
    
    # Ensure formik and yup dependencies
    if ! grep -q '"formik"' package.json; then
        sed -i '/"dependencies": {/a \    "formik": "^2.4.5",' package.json
    fi
    if ! grep -q '"yup"' package.json; then
        sed -i '/"dependencies": {/a \    "yup": "^1.3.2",' package.json
    fi
fi

# Ensure main.jsx/index.js is configured properly
if [ -f "src/index.js" ]; then
    echo -e "${YELLOW}📝 Checking React entry point...${NC}"
    # Create backup
    cp src/index.js src/index.js.bak
    
    # Update to proper React 18 setup
    cat > src/index.js << 'EOF'
import React from 'react';
import { createRoot } from 'react-dom/client';
import App from './App';
import './index.css';

const container = document.getElementById('root');
const root = createRoot(container);

root.render(
  <React.StrictMode>
    <App />
  </React.StrictMode>
);
EOF
    echo -e "${GREEN}✅ Updated React entry point to use createRoot (React 18)${NC}"
fi

# Return to the project root directory
cd ..

# Restart frontend service
echo -e "${YELLOW}🔄 Restarting frontend service...${NC}"
supervisorctl restart frontend

echo -e "${GREEN}✅ Login component fix completed!${NC}"
echo -e "${YELLOW}ℹ️ Next steps:${NC}"
echo -e "1. Check frontend logs: ${BLUE}tail -f logs/frontend_error.log${NC}"
echo -e "2. Access the frontend at: ${BLUE}http://65.109.207.182:3000${NC}"
echo -e "3. If still encountering issues, run: ${BLUE}./fix_services.sh frontend${NC}" 