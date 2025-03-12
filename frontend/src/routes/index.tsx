import React, { Suspense } from 'react';
import { Routes, Route, Navigate } from 'react-router-dom';
import { CircularProgress, Box } from '@mui/material';
import ResponsiveLayout from '../layouts/ResponsiveLayout';

// Lazy load components
const Dashboard = React.lazy(() => import('../components/Dashboard/AnalyticsDashboard'));
const UserManagement = React.lazy(() => import('../components/Users/UserManagement'));
const ServerManagement = React.lazy(() => import('../components/Servers/ServerManagement'));
const Settings = React.lazy(() => import('../components/Settings/Settings'));
const AccessibilitySettings = React.lazy(() => import('../components/Settings/AccessibilitySettings'));
const KeyboardShortcuts = React.lazy(() => import('../components/Settings/KeyboardShortcuts'));
const TutorialGuide = React.lazy(() => import('../components/Tutorial/TutorialGuide'));

// Loading component
const LoadingFallback = () => (
  <Box
    display="flex"
    justifyContent="center"
    alignItems="center"
    minHeight="100vh"
  >
    <CircularProgress />
  </Box>
);

const AppRoutes = () => {
  return (
    <Suspense fallback={<LoadingFallback />}>
      <Routes>
        <Route path="/" element={<Navigate to="/dashboard" replace />} />
        <Route
          path="/dashboard"
          element={
            <ResponsiveLayout title="Dashboard">
              <Dashboard />
            </ResponsiveLayout>
          }
        />
        <Route
          path="/users"
          element={
            <ResponsiveLayout title="User Management">
              <UserManagement />
            </ResponsiveLayout>
          }
        />
        <Route
          path="/servers"
          element={
            <ResponsiveLayout title="Server Management">
              <ServerManagement />
            </ResponsiveLayout>
          }
        />
        <Route
          path="/settings"
          element={
            <ResponsiveLayout title="Settings">
              <Settings />
            </ResponsiveLayout>
          }
        />
        <Route
          path="/settings/accessibility"
          element={
            <ResponsiveLayout title="Accessibility Settings">
              <AccessibilitySettings />
            </ResponsiveLayout>
          }
        />
        <Route
          path="/settings/keyboard-shortcuts"
          element={
            <ResponsiveLayout title="Keyboard Shortcuts">
              <KeyboardShortcuts />
            </ResponsiveLayout>
          }
        />
        <Route
          path="/tutorial"
          element={
            <ResponsiveLayout title="Tutorial">
              <TutorialGuide />
            </ResponsiveLayout>
          }
        />
      </Routes>
    </Suspense>
  );
};

export default AppRoutes; 