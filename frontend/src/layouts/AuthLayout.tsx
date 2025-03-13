import React from 'react';
import { Box, Container, Paper, Typography, useTheme, Link, IconButton } from '@mui/material';
import { Outlet } from 'react-router-dom';
import { Brightness4 as DarkModeIcon, Brightness7 as LightModeIcon, Language as LanguageIcon } from '@mui/icons-material';
import { useTranslation } from 'react-i18next';

// Logo component
const Logo: React.FC = () => {
  return (
    <Typography
      variant="h4"
      component="div"
      sx={{
        fontWeight: 'bold',
        color: 'primary.main',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
      }}
    >
      VPN Manager
    </Typography>
  );
};

interface AuthLayoutProps {
  toggleTheme?: () => void;
  toggleLanguage?: () => void;
}

const AuthLayout: React.FC<AuthLayoutProps> = ({ toggleTheme, toggleLanguage }) => {
  const theme = useTheme();
  const { t } = useTranslation();
  const currentYear = new Date().getFullYear();
  
  // Background pattern style for the dark/light themes
  const backgroundPattern = {
    backgroundColor: theme.palette.background.default,
    backgroundImage: `linear-gradient(${theme.palette.background.paper} 1px, transparent 1px), 
                     linear-gradient(90deg, ${theme.palette.background.paper} 1px, transparent 1px)`,
    backgroundSize: '20px 20px',
    backgroundPosition: '-1px -1px',
    minHeight: '100vh',
    display: 'flex',
    flexDirection: 'column',
  };
  
  return (
    <Box sx={backgroundPattern}>
      {/* Header with theme toggle and language switch */}
      <Box 
        sx={{ 
          p: 2, 
          display: 'flex', 
          justifyContent: 'space-between',
          alignItems: 'center'
        }}
      >
        <Logo />
        
        <Box sx={{ display: 'flex', gap: 1 }}>
          {toggleLanguage && (
            <IconButton onClick={toggleLanguage} color="primary" title={t('تغییر زبان')}>
              <LanguageIcon />
            </IconButton>
          )}
          
          {toggleTheme && (
            <IconButton onClick={toggleTheme} color="primary" title={t('تغییر تم')}>
              {theme.palette.mode === 'dark' ? <LightModeIcon /> : <DarkModeIcon />}
            </IconButton>
          )}
        </Box>
      </Box>
      
      {/* Main content area */}
      <Container
        maxWidth="lg"
        sx={{
          flex: 1,
          display: 'flex',
          flexDirection: 'column',
          justifyContent: 'center',
          p: 2,
        }}
      >
        <Outlet />
      </Container>
      
      {/* Footer with copyright */}
      <Box
        component="footer"
        sx={{
          py: 3,
          px: 2,
          mt: 'auto',
          textAlign: 'center',
        }}
      >
        <Typography variant="body2" color="text.secondary">
          {t('تمامی حقوق محفوظ است')} &copy; {currentYear} VPN Manager
        </Typography>
        <Box sx={{ mt: 1 }}>
          <Link href="#" color="inherit" sx={{ mx: 1 }}>
            {t('شرایط استفاده')}
          </Link>
          <Link href="#" color="inherit" sx={{ mx: 1 }}>
            {t('حریم خصوصی')}
          </Link>
          <Link href="#" color="inherit" sx={{ mx: 1 }}>
            {t('پشتیبانی')}
          </Link>
        </Box>
      </Box>
    </Box>
  );
};

export default AuthLayout; 