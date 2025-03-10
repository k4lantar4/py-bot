#!/bin/bash

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[0;33m'
BLUE='\033[0;34m'
NC='\033[0m'

echo -e "${BLUE}┌────────────────────────────────────────┐${NC}"
echo -e "${BLUE}│      Frontend Fix Script               │${NC}"
echo -e "${BLUE}└────────────────────────────────────────┘${NC}"

# Check if the frontend directory exists
if [ ! -d "frontend" ]; then
    echo -e "${RED}❌ Frontend directory not found${NC}"
    exit 1
fi

# Create necessary directory structure
echo -e "${YELLOW}📁 Creating necessary directory structure...${NC}"
cd frontend/src

# Create missing directories
mkdir -p pages/auth
mkdir -p pages/locations
mkdir -p pages/servers
mkdir -p pages/services
mkdir -p pages/users
mkdir -p pages/orders
mkdir -p pages/discounts
mkdir -p pages/messages
mkdir -p pages/reports
mkdir -p pages/settings

# Create basic placeholder files for missing components
echo -e "${YELLOW}📝 Creating placeholder component files...${NC}"

# Auth pages
cat > pages/auth/Register.js << 'EOF'
import React from 'react';
import { Typography, Container, Paper, Box } from '@mui/material';

const Register = () => {
  return (
    <Container component="main" maxWidth="xs">
      <Paper elevation={3} sx={{ padding: 3, marginTop: 8 }}>
        <Typography variant="h5" component="h1" gutterBottom align="center">
          Register
        </Typography>
        <Box>
          <Typography>Registration form will be implemented here.</Typography>
        </Box>
      </Paper>
    </Container>
  );
};

export default Register;
EOF

cat > pages/auth/ForgotPassword.js << 'EOF'
import React from 'react';
import { Typography, Container, Paper, Box } from '@mui/material';

const ForgotPassword = () => {
  return (
    <Container component="main" maxWidth="xs">
      <Paper elevation={3} sx={{ padding: 3, marginTop: 8 }}>
        <Typography variant="h5" component="h1" gutterBottom align="center">
          Forgot Password
        </Typography>
        <Box>
          <Typography>Password recovery form will be implemented here.</Typography>
        </Box>
      </Paper>
    </Container>
  );
};

export default ForgotPassword;
EOF

cat > pages/auth/ResetPassword.js << 'EOF'
import React from 'react';
import { Typography, Container, Paper, Box } from '@mui/material';

const ResetPassword = () => {
  return (
    <Container component="main" maxWidth="xs">
      <Paper elevation={3} sx={{ padding: 3, marginTop: 8 }}>
        <Typography variant="h5" component="h1" gutterBottom align="center">
          Reset Password
        </Typography>
        <Box>
          <Typography>Password reset form will be implemented here.</Typography>
        </Box>
      </Paper>
    </Container>
  );
};

export default ResetPassword;
EOF

# NotFound page
cat > pages/NotFound.js << 'EOF'
import React from 'react';
import { Typography, Container, Paper, Box, Button } from '@mui/material';
import { useNavigate } from 'react-router-dom';

const NotFound = () => {
  const navigate = useNavigate();

  return (
    <Container component="main" maxWidth="md">
      <Paper elevation={3} sx={{ padding: 4, marginTop: 8, textAlign: 'center' }}>
        <Typography variant="h1" component="h1" gutterBottom>
          404
        </Typography>
        <Typography variant="h5" component="h2" gutterBottom>
          Page Not Found
        </Typography>
        <Box my={4}>
          <Typography variant="body1" paragraph>
            The page you are looking for does not exist or has been moved.
          </Typography>
          <Button 
            variant="contained" 
            color="primary" 
            onClick={() => navigate('/')}
          >
            Go to Homepage
          </Button>
        </Box>
      </Paper>
    </Container>
  );
};

export default NotFound;
EOF

# Create placeholder files for other sections
# Locations
cat > pages/locations/LocationsList.js << 'EOF'
import React from 'react';
import { Typography, Container } from '@mui/material';

const LocationsList = () => {
  return (
    <Container>
      <Typography variant="h4" component="h1" gutterBottom>
        Locations List
      </Typography>
      <Typography>
        Locations list will be displayed here.
      </Typography>
    </Container>
  );
};

export default LocationsList;
EOF

cat > pages/locations/LocationDetails.js << 'EOF'
import React from 'react';
import { Typography, Container } from '@mui/material';
import { useParams } from 'react-router-dom';

const LocationDetails = () => {
  const { id } = useParams();
  
  return (
    <Container>
      <Typography variant="h4" component="h1" gutterBottom>
        Location Details
      </Typography>
      <Typography>
        Details for location ID: {id || 'Not specified'}
      </Typography>
    </Container>
  );
};

export default LocationDetails;
EOF

# Servers
cat > pages/servers/ServersList.js << 'EOF'
import React from 'react';
import { Typography, Container } from '@mui/material';

const ServersList = () => {
  return (
    <Container>
      <Typography variant="h4" component="h1" gutterBottom>
        Servers List
      </Typography>
      <Typography>
        Servers list will be displayed here.
      </Typography>
    </Container>
  );
};

export default ServersList;
EOF

cat > pages/servers/ServerDetails.js << 'EOF'
import React from 'react';
import { Typography, Container } from '@mui/material';
import { useParams } from 'react-router-dom';

const ServerDetails = () => {
  const { id } = useParams();
  
  return (
    <Container>
      <Typography variant="h4" component="h1" gutterBottom>
        Server Details
      </Typography>
      <Typography>
        Details for server ID: {id || 'Not specified'}
      </Typography>
    </Container>
  );
};

export default ServerDetails;
EOF

# Services
cat > pages/services/ServicesList.js << 'EOF'
import React from 'react';
import { Typography, Container } from '@mui/material';

const ServicesList = () => {
  return (
    <Container>
      <Typography variant="h4" component="h1" gutterBottom>
        Services List
      </Typography>
      <Typography>
        Services list will be displayed here.
      </Typography>
    </Container>
  );
};

export default ServicesList;
EOF

cat > pages/services/ServiceDetails.js << 'EOF'
import React from 'react';
import { Typography, Container } from '@mui/material';
import { useParams } from 'react-router-dom';

const ServiceDetails = () => {
  const { id } = useParams();
  
  return (
    <Container>
      <Typography variant="h4" component="h1" gutterBottom>
        Service Details
      </Typography>
      <Typography>
        Details for service ID: {id || 'Not specified'}
      </Typography>
    </Container>
  );
};

export default ServiceDetails;
EOF

# Users
cat > pages/users/UsersList.js << 'EOF'
import React from 'react';
import { Typography, Container } from '@mui/material';

const UsersList = () => {
  return (
    <Container>
      <Typography variant="h4" component="h1" gutterBottom>
        Users List
      </Typography>
      <Typography>
        Users list will be displayed here.
      </Typography>
    </Container>
  );
};

export default UsersList;
EOF

cat > pages/users/UserDetails.js << 'EOF'
import React from 'react';
import { Typography, Container } from '@mui/material';
import { useParams } from 'react-router-dom';

const UserDetails = () => {
  const { id } = useParams();
  
  return (
    <Container>
      <Typography variant="h4" component="h1" gutterBottom>
        User Details
      </Typography>
      <Typography>
        Details for user ID: {id || 'Not specified'}
      </Typography>
    </Container>
  );
};

export default UserDetails;
EOF

cat > pages/users/Profile.js << 'EOF'
import React from 'react';
import { Typography, Container, Paper } from '@mui/material';

const Profile = () => {
  return (
    <Container>
      <Paper elevation={2} sx={{ p: 3, mt: 3 }}>
        <Typography variant="h4" component="h1" gutterBottom>
          User Profile
        </Typography>
        <Typography>
          User profile page will be displayed here.
        </Typography>
      </Paper>
    </Container>
  );
};

export default Profile;
EOF

# Orders
cat > pages/orders/OrdersList.js << 'EOF'
import React from 'react';
import { Typography, Container } from '@mui/material';

const OrdersList = () => {
  return (
    <Container>
      <Typography variant="h4" component="h1" gutterBottom>
        Orders List
      </Typography>
      <Typography>
        Orders list will be displayed here.
      </Typography>
    </Container>
  );
};

export default OrdersList;
EOF

cat > pages/orders/OrderDetails.js << 'EOF'
import React from 'react';
import { Typography, Container } from '@mui/material';
import { useParams } from 'react-router-dom';

const OrderDetails = () => {
  const { id } = useParams();
  
  return (
    <Container>
      <Typography variant="h4" component="h1" gutterBottom>
        Order Details
      </Typography>
      <Typography>
        Details for order ID: {id || 'Not specified'}
      </Typography>
    </Container>
  );
};

export default OrderDetails;
EOF

# Discounts
cat > pages/discounts/DiscountsList.js << 'EOF'
import React from 'react';
import { Typography, Container } from '@mui/material';

const DiscountsList = () => {
  return (
    <Container>
      <Typography variant="h4" component="h1" gutterBottom>
        Discounts List
      </Typography>
      <Typography>
        Discounts list will be displayed here.
      </Typography>
    </Container>
  );
};

export default DiscountsList;
EOF

cat > pages/discounts/DiscountDetails.js << 'EOF'
import React from 'react';
import { Typography, Container } from '@mui/material';
import { useParams } from 'react-router-dom';

const DiscountDetails = () => {
  const { id } = useParams();
  
  return (
    <Container>
      <Typography variant="h4" component="h1" gutterBottom>
        Discount Details
      </Typography>
      <Typography>
        Details for discount ID: {id || 'Not specified'}
      </Typography>
    </Container>
  );
};

export default DiscountDetails;
EOF

# Messages
cat > pages/messages/MessagesList.js << 'EOF'
import React from 'react';
import { Typography, Container } from '@mui/material';

const MessagesList = () => {
  return (
    <Container>
      <Typography variant="h4" component="h1" gutterBottom>
        Messages List
      </Typography>
      <Typography>
        Messages list will be displayed here.
      </Typography>
    </Container>
  );
};

export default MessagesList;
EOF

cat > pages/messages/MessageDetails.js << 'EOF'
import React from 'react';
import { Typography, Container } from '@mui/material';
import { useParams } from 'react-router-dom';

const MessageDetails = () => {
  const { id } = useParams();
  
  return (
    <Container>
      <Typography variant="h4" component="h1" gutterBottom>
        Message Details
      </Typography>
      <Typography>
        Details for message ID: {id || 'Not specified'}
      </Typography>
    </Container>
  );
};

export default MessageDetails;
EOF

# Reports
cat > pages/reports/Reports.js << 'EOF'
import React from 'react';
import { Typography, Container } from '@mui/material';

const Reports = () => {
  return (
    <Container>
      <Typography variant="h4" component="h1" gutterBottom>
        Reports
      </Typography>
      <Typography>
        Reports dashboard will be displayed here.
      </Typography>
    </Container>
  );
};

export default Reports;
EOF

# Settings
cat > pages/settings/Settings.js << 'EOF'
import React from 'react';
import { Typography, Container } from '@mui/material';

const Settings = () => {
  return (
    <Container>
      <Typography variant="h4" component="h1" gutterBottom>
        System Settings
      </Typography>
      <Typography>
        Settings panel will be displayed here.
      </Typography>
    </Container>
  );
};

export default Settings;
EOF

# Create reportWebVitals.js
cat > reportWebVitals.js << 'EOF'
const reportWebVitals = (onPerfEntry) => {
  if (onPerfEntry && onPerfEntry instanceof Function) {
    import('web-vitals').then(({ getCLS, getFID, getFCP, getLCP, getTTFB }) => {
      getCLS(onPerfEntry);
      getFID(onPerfEntry);
      getFCP(onPerfEntry);
      getLCP(onPerfEntry);
      getTTFB(onPerfEntry);
    });
  }
};

export default reportWebVitals;
EOF

# Fix theme exports
echo -e "${YELLOW}🎨 Fixing theme exports...${NC}"

# Check theme.js file
if [ -f "theme.js" ]; then
  # Backup the original file
  cp theme.js theme.js.bak
  
  # Create or update theme.js with both light and dark themes
  cat > theme.js << 'EOF'
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
  echo -e "${GREEN}✅ Theme file updated with light and dark themes${NC}"
else
  echo -e "${YELLOW}Creating theme.js file...${NC}"
  # Create theme.js file with both light and dark themes
  cat > theme.js << 'EOF'
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
  echo -e "${GREEN}✅ Theme file created${NC}"
fi

# Install formik if missing
echo -e "${YELLOW}📦 Installing missing dependencies...${NC}"
cd ../..
npm install --save formik yup web-vitals

echo -e "${GREEN}✅ Frontend fixes completed!${NC}"
echo -e "${YELLOW}ℹ️ Next step: Restart frontend service with ${BLUE}supervisorctl restart frontend${NC}" 