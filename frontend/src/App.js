import React, { useEffect } from 'react';
import { Routes, Route, Navigate } from 'react-router-dom';
import { useTranslation } from 'react-i18next';
import { useSnackbar } from 'notistack';

// Layouts
import DashboardLayout from './layouts/DashboardLayout';
import AuthLayout from './layouts/AuthLayout';

// Pages
import Dashboard from './pages/Dashboard';
import Login from './pages/auth/Login';
import Register from './pages/auth/Register';
import ForgotPassword from './pages/auth/ForgotPassword';
import ResetPassword from './pages/auth/ResetPassword';
import NotFound from './pages/NotFound';

// Feature Pages
import LocationsList from './pages/locations/LocationsList';
import LocationDetails from './pages/locations/LocationDetails';
import ServersList from './pages/servers/ServersList';
import ServerDetails from './pages/servers/ServerDetails';
import ServicesList from './pages/services/ServicesList';
import ServiceDetails from './pages/services/ServiceDetails';
// These imports are commented out until the components are created
// import UsersList from './pages/users/UsersList';
// import UserDetails from './pages/users/UserDetails';
// import Profile from './pages/users/Profile';
// import OrdersList from './pages/orders/OrdersList';
// import OrderDetails from './pages/orders/OrderDetails';
// import DiscountsList from './pages/discounts/DiscountsList';
// import DiscountDetails from './pages/discounts/DiscountDetails';
// import MessagesList from './pages/messages/MessagesList';
// import MessageDetails from './pages/messages/MessageDetails';
// import Reports from './pages/reports/Reports';
// import Settings from './pages/settings/Settings';

// Contexts
import { useAuth } from './contexts/AuthContext';
import { useSettings } from './contexts/SettingsContext';

// Guards
import AuthGuard from './guards/AuthGuard';
import GuestGuard from './guards/GuestGuard';
import RoleGuard from './guards/RoleGuard';

function App() {
  const { isInitialized, isAuthenticated } = useAuth();
  const { settings, saveSettings } = useSettings();
  const { i18n } = useTranslation();
  const { enqueueSnackbar } = useSnackbar();

  // Set language from settings
  useEffect(() => {
    if (settings.language) {
      i18n.changeLanguage(settings.language);
    }
  }, [settings.language, i18n]);

  return (
    <Routes>
      {/* Auth Routes */}
      <Route element={<GuestGuard />}>
        <Route path="/auth" element={<AuthLayout />}>
          <Route path="login" element={<Login />} />
          <Route path="register" element={<Register />} />
          <Route path="forgot-password" element={<ForgotPassword />} />
          <Route path="reset-password" element={<ResetPassword />} />
        </Route>
      </Route>

      {/* Dashboard Routes */}
      <Route element={<AuthGuard />}>
        <Route path="/" element={<DashboardLayout />}>
          <Route index element={<Dashboard />} />
          
          {/* User Profile */}
          {/* <Route path="profile" element={<Profile />} /> */}
          
          {/* Location Management */}
          <Route element={<RoleGuard roles={['admin', 'manager']} />}>
            <Route path="locations" element={<LocationsList />} />
            <Route path="locations/:id" element={<LocationDetails />} />
          </Route>
          
          {/* Server Management */}
          <Route element={<RoleGuard roles={['admin', 'manager']} />}>
            <Route path="servers" element={<ServersList />} />
            <Route path="servers/:id" element={<ServerDetails />} />
          </Route>
          
          {/* Service Management */}
          <Route element={<RoleGuard roles={['admin', 'manager', 'vendor']} />}>
            <Route path="services" element={<ServicesList />} />
            <Route path="services/:id" element={<ServiceDetails />} />
          </Route>
          
          {/* User Management */}
          {/* <Route element={<RoleGuard roles={['admin', 'manager']} />}>
            <Route path="users" element={<UsersList />} />
            <Route path="users/:id" element={<UserDetails />} />
          </Route> */}
          
          {/* Order Management */}
          {/* <Route path="orders" element={<OrdersList />} />
          <Route path="orders/:id" element={<OrderDetails />} /> */}
          
          {/* Discount Management */}
          {/* <Route element={<RoleGuard roles={['admin', 'manager']} />}>
            <Route path="discounts" element={<DiscountsList />} />
            <Route path="discounts/:id" element={<DiscountDetails />} />
          </Route> */}
          
          {/* Messaging */}
          {/* <Route element={<RoleGuard roles={['admin', 'manager']} />}>
            <Route path="messages" element={<MessagesList />} />
            <Route path="messages/:id" element={<MessageDetails />} />
          </Route> */}
          
          {/* Reports */}
          {/* <Route element={<RoleGuard roles={['admin', 'manager']} />}>
            <Route path="reports" element={<Reports />} />
          </Route> */}
          
          {/* Settings */}
          {/* <Route path="settings" element={<Settings />} /> */}
        </Route>
      </Route>

      {/* NotFound and Redirect Route */}
      <Route
        path="*"
        element={
          !isInitialized ? (
            <div>Loading...</div>
          ) : isAuthenticated ? (
            <Navigate to="/" replace />
          ) : (
            <NotFound />
          )
        }
      />
    </Routes>
  );
}

export default App; 