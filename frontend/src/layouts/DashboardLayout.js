import React, { useState } from 'react';
import { Outlet } from 'react-router-dom';
import { useTranslation } from 'react-i18next';
import { styled, useTheme } from '@mui/material/styles';
import {
  Box,
  Drawer,
  AppBar,
  Toolbar,
  List,
  Typography,
  Divider,
  IconButton,
  ListItem,
  ListItemButton,
  ListItemIcon,
  ListItemText,
  Avatar,
  Menu,
  MenuItem,
  Badge,
  Tooltip,
  useMediaQuery
} from '@mui/material';
import {
  Menu as MenuIcon,
  ChevronLeft as ChevronLeftIcon,
  ChevronRight as ChevronRightIcon,
  Dashboard as DashboardIcon,
  LocationOn as LocationIcon,
  Computer as ServerIcon,
  Layers as ServiceIcon,
  People as UserIcon,
  ShoppingCart as OrderIcon,
  LocalOffer as DiscountIcon,
  Email as MessageIcon,
  BarChart as ReportIcon,
  Settings as SettingsIcon,
  Notifications as NotificationsIcon,
  Translate as TranslateIcon,
  Brightness4 as DarkModeIcon,
  Brightness7 as LightModeIcon,
  AccountCircle,
  Logout
} from '@mui/icons-material';

import { useAuth } from '../contexts/AuthContext';
import { useSettings } from '../contexts/SettingsContext';

// Drawer width
const drawerWidth = 240;

// Styled components
const Main = styled('main', { shouldForwardProp: (prop) => prop !== 'open' })(
  ({ theme, open }) => ({
    flexGrow: 1,
    padding: theme.spacing(3),
    transition: theme.transitions.create('margin', {
      easing: theme.transitions.easing.sharp,
      duration: theme.transitions.duration.leavingScreen,
    }),
    marginLeft: `-${drawerWidth}px`,
    ...(open && {
      transition: theme.transitions.create('margin', {
        easing: theme.transitions.easing.easeOut,
        duration: theme.transitions.duration.enteringScreen,
      }),
      marginLeft: 0,
    }),
  }),
);

const AppBarStyled = styled(AppBar, {
  shouldForwardProp: (prop) => prop !== 'open',
})(({ theme, open }) => ({
  transition: theme.transitions.create(['margin', 'width'], {
    easing: theme.transitions.easing.sharp,
    duration: theme.transitions.duration.leavingScreen,
  }),
  ...(open && {
    width: `calc(100% - ${drawerWidth}px)`,
    marginLeft: `${drawerWidth}px`,
    transition: theme.transitions.create(['margin', 'width'], {
      easing: theme.transitions.easing.easeOut,
      duration: theme.transitions.duration.enteringScreen,
    }),
  }),
}));

const DrawerHeader = styled('div')(({ theme }) => ({
  display: 'flex',
  alignItems: 'center',
  padding: theme.spacing(0, 1),
  ...theme.mixins.toolbar,
  justifyContent: 'flex-end',
}));

export default function DashboardLayout() {
  const theme = useTheme();
  const { t, i18n } = useTranslation();
  const { user, logout } = useAuth();
  const { settings, saveSettings } = useSettings();
  const isMobile = useMediaQuery(theme.breakpoints.down('md'));
  
  // State for drawer and menus
  const [open, setOpen] = useState(!isMobile && settings.sidebarOpen);
  const [anchorElUser, setAnchorElUser] = useState(null);
  const [anchorElLang, setAnchorElLang] = useState(null);
  const [anchorElNotif, setAnchorElNotif] = useState(null);

  // Handle drawer open/close
  const handleDrawerOpen = () => {
    setOpen(true);
    saveSettings({ sidebarOpen: true });
  };

  const handleDrawerClose = () => {
    setOpen(false);
    saveSettings({ sidebarOpen: false });
  };

  // Handle user menu
  const handleOpenUserMenu = (event) => {
    setAnchorElUser(event.currentTarget);
  };

  const handleCloseUserMenu = () => {
    setAnchorElUser(null);
  };

  // Handle language menu
  const handleOpenLangMenu = (event) => {
    setAnchorElLang(event.currentTarget);
  };

  const handleCloseLangMenu = () => {
    setAnchorElLang(null);
  };

  // Handle notifications menu
  const handleOpenNotifMenu = (event) => {
    setAnchorElNotif(event.currentTarget);
  };

  const handleCloseNotifMenu = () => {
    setAnchorElNotif(null);
  };

  // Change language
  const changeLanguage = (lang) => {
    i18n.changeLanguage(lang);
    saveSettings({ language: lang });
    handleCloseLangMenu();
  };

  // Toggle theme
  const toggleTheme = () => {
    const newTheme = settings.theme === 'light' ? 'dark' : 'light';
    saveSettings({ theme: newTheme });
  };

  // Handle logout
  const handleLogout = () => {
    handleCloseUserMenu();
    logout();
  };

  // Menu items based on user role
  const getMenuItems = () => {
    const isAdmin = user?.roles?.includes('admin');
    const isManager = user?.roles?.includes('manager');
    const isVendor = user?.roles?.includes('vendor');
    
    const items = [
      {
        text: t('dashboard.dashboard'),
        icon: <DashboardIcon />,
        path: '/',
        roles: ['admin', 'manager', 'vendor', 'customer']
      },
      {
        text: t('location.locations'),
        icon: <LocationIcon />,
        path: '/locations',
        roles: ['admin', 'manager']
      },
      {
        text: t('server.servers'),
        icon: <ServerIcon />,
        path: '/servers',
        roles: ['admin', 'manager']
      },
      {
        text: t('service.services'),
        icon: <ServiceIcon />,
        path: '/services',
        roles: ['admin', 'manager', 'vendor']
      },
      {
        text: t('user.users'),
        icon: <UserIcon />,
        path: '/users',
        roles: ['admin', 'manager']
      },
      {
        text: t('order.orders'),
        icon: <OrderIcon />,
        path: '/orders',
        roles: ['admin', 'manager', 'vendor', 'customer']
      },
      {
        text: t('discount.discounts'),
        icon: <DiscountIcon />,
        path: '/discounts',
        roles: ['admin', 'manager']
      },
      {
        text: t('message.messages'),
        icon: <MessageIcon />,
        path: '/messages',
        roles: ['admin', 'manager']
      },
      {
        text: t('report.reports'),
        icon: <ReportIcon />,
        path: '/reports',
        roles: ['admin', 'manager']
      },
      {
        text: t('settings.settings'),
        icon: <SettingsIcon />,
        path: '/settings',
        roles: ['admin', 'manager', 'vendor', 'customer']
      }
    ];

    return items.filter(item => {
      if (isAdmin) return true;
      if (isManager && item.roles.includes('manager')) return true;
      if (isVendor && item.roles.includes('vendor')) return true;
      if (item.roles.includes('customer')) return true;
      return false;
    });
  };

  return (
    <Box sx={{ display: 'flex' }}>
      {/* App Bar */}
      <AppBarStyled position="fixed" open={open}>
        <Toolbar>
          <IconButton
            color="inherit"
            aria-label="open drawer"
            onClick={handleDrawerOpen}
            edge="start"
            sx={{ mr: 2, ...(open && { display: 'none' }) }}
          >
            <MenuIcon />
          </IconButton>
          <Typography variant="h6" noWrap component="div" sx={{ flexGrow: 1 }}>
            {t('common.appName')}
          </Typography>

          {/* Theme Toggle */}
          <Tooltip title={settings.theme === 'light' ? t('settings.darkMode') : t('settings.lightMode')}>
            <IconButton color="inherit" onClick={toggleTheme}>
              {settings.theme === 'light' ? <DarkModeIcon /> : <LightModeIcon />}
            </IconButton>
          </Tooltip>

          {/* Language Menu */}
          <Tooltip title={t('settings.language')}>
            <IconButton color="inherit" onClick={handleOpenLangMenu}>
              <TranslateIcon />
            </IconButton>
          </Tooltip>
          <Menu
            anchorEl={anchorElLang}
            open={Boolean(anchorElLang)}
            onClose={handleCloseLangMenu}
          >
            <MenuItem onClick={() => changeLanguage('en')}>English</MenuItem>
            <MenuItem onClick={() => changeLanguage('fa')}>فارسی</MenuItem>
          </Menu>

          {/* Notifications */}
          <Tooltip title={t('common.notifications')}>
            <IconButton color="inherit" onClick={handleOpenNotifMenu}>
              <Badge badgeContent={4} color="error">
                <NotificationsIcon />
              </Badge>
            </IconButton>
          </Tooltip>
          <Menu
            anchorEl={anchorElNotif}
            open={Boolean(anchorElNotif)}
            onClose={handleCloseNotifMenu}
          >
            <MenuItem onClick={handleCloseNotifMenu}>Notification 1</MenuItem>
            <MenuItem onClick={handleCloseNotifMenu}>Notification 2</MenuItem>
            <MenuItem onClick={handleCloseNotifMenu}>Notification 3</MenuItem>
            <MenuItem onClick={handleCloseNotifMenu}>Notification 4</MenuItem>
          </Menu>

          {/* User Menu */}
          <Tooltip title={user?.username || ''}>
            <IconButton onClick={handleOpenUserMenu} sx={{ p: 0, ml: 2 }}>
              <Avatar alt={user?.username || 'User'} src="/static/images/avatar/1.jpg" />
            </IconButton>
          </Tooltip>
          <Menu
            anchorEl={anchorElUser}
            open={Boolean(anchorElUser)}
            onClose={handleCloseUserMenu}
          >
            <MenuItem onClick={handleCloseUserMenu} component="a" href="/profile">
              <ListItemIcon>
                <AccountCircle fontSize="small" />
              </ListItemIcon>
              <ListItemText primary={t('user.profile')} />
            </MenuItem>
            <MenuItem onClick={handleLogout}>
              <ListItemIcon>
                <Logout fontSize="small" />
              </ListItemIcon>
              <ListItemText primary={t('auth.logout')} />
            </MenuItem>
          </Menu>
        </Toolbar>
      </AppBarStyled>

      {/* Sidebar */}
      <Drawer
        sx={{
          width: drawerWidth,
          flexShrink: 0,
          '& .MuiDrawer-paper': {
            width: drawerWidth,
            boxSizing: 'border-box',
          },
        }}
        variant="persistent"
        anchor="left"
        open={open}
      >
        <DrawerHeader>
          <Typography variant="h6" sx={{ flexGrow: 1, ml: 2 }}>
            3X-UI Manager
          </Typography>
          <IconButton onClick={handleDrawerClose}>
            {theme.direction === 'ltr' ? <ChevronLeftIcon /> : <ChevronRightIcon />}
          </IconButton>
        </DrawerHeader>
        <Divider />

        {/* Navigation Menu */}
        <List>
          {getMenuItems().map((item) => (
            <ListItem key={item.text} disablePadding>
              <ListItemButton component="a" href={item.path}>
                <ListItemIcon>{item.icon}</ListItemIcon>
                <ListItemText primary={item.text} />
              </ListItemButton>
            </ListItem>
          ))}
        </List>
      </Drawer>

      {/* Main Content */}
      <Main open={open}>
        <DrawerHeader />
        <Outlet />
      </Main>
    </Box>
  );
} 