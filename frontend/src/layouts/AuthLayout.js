import React from 'react';
import { Outlet } from 'react-router-dom';
import { useTranslation } from 'react-i18next';
import {
  Box,
  Container,
  Typography,
  Grid,
  Paper,
  useTheme,
  IconButton,
  Menu,
  MenuItem
} from '@mui/material';
import { Translate as TranslateIcon } from '@mui/icons-material';

import { useSettings } from '../contexts/SettingsContext';

const AuthLayout = () => {
  const theme = useTheme();
  const { t, i18n } = useTranslation();
  const { settings, saveSettings } = useSettings();
  const [anchorElLang, setAnchorElLang] = React.useState(null);

  // Handle language menu
  const handleOpenLangMenu = (event) => {
    setAnchorElLang(event.currentTarget);
  };

  const handleCloseLangMenu = () => {
    setAnchorElLang(null);
  };

  // Change language
  const changeLanguage = (lang) => {
    i18n.changeLanguage(lang);
    saveSettings({ language: lang });
    handleCloseLangMenu();
  };

  return (
    <Box
      sx={{
        display: 'flex',
        flexDirection: 'column',
        minHeight: '100vh',
        backgroundColor: theme.palette.background.default
      }}
    >
      {/* Header with language selector */}
      <Box
        sx={{
          display: 'flex',
          justifyContent: 'flex-end',
          p: 2
        }}
      >
        <IconButton color="primary" onClick={handleOpenLangMenu}>
          <TranslateIcon />
        </IconButton>
        <Menu
          anchorEl={anchorElLang}
          open={Boolean(anchorElLang)}
          onClose={handleCloseLangMenu}
        >
          <MenuItem onClick={() => changeLanguage('en')}>English</MenuItem>
          <MenuItem onClick={() => changeLanguage('fa')}>فارسی</MenuItem>
        </Menu>
      </Box>

      {/* Main content */}
      <Container maxWidth="sm" sx={{ py: 4, flexGrow: 1, display: 'flex', flexDirection: 'column', justifyContent: 'center' }}>
        <Grid container justifyContent="center" alignItems="center" spacing={4}>
          <Grid item xs={12}>
            <Typography 
              variant="h4" 
              component="h1" 
              align="center" 
              gutterBottom 
              sx={{ mb: 4, fontWeight: 'bold' }}
            >
              {t('common.appName')}
            </Typography>
          </Grid>
          
          <Grid item xs={12}>
            <Paper 
              elevation={6} 
              sx={{ 
                p: { xs: 3, sm: 4 },
                borderRadius: 2,
                boxShadow: (theme) => `0 8px 24px ${theme.palette.mode === 'light' 
                  ? 'rgba(149, 157, 165, 0.2)' 
                  : 'rgba(0, 0, 0, 0.35)'}`
              }}
            >
              <Outlet />
            </Paper>
          </Grid>
        </Grid>
      </Container>

      {/* Footer */}
      <Box
        component="footer"
        sx={{
          py: 3,
          px: 2,
          mt: 'auto',
          textAlign: 'center'
        }}
      >
        <Typography variant="body2" color="text.secondary">
          © {new Date().getFullYear()} 3X-UI Management System
        </Typography>
      </Box>
    </Box>
  );
};

export default AuthLayout; 