import React from 'react';
import { Navigate, Outlet, useLocation } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';

const GuestGuard = () => {
  const { isAuthenticated, isInitialized } = useAuth();
  const location = useLocation();
  const from = location.state?.from?.pathname || '/';

  // If auth is still initializing, show nothing
  if (!isInitialized) {
    return null;
  }

  // If authenticated, redirect to dashboard or the page they came from
  if (isAuthenticated) {
    return <Navigate to={from} replace />;
  }

  // If not authenticated, render the guest routes (login, register, etc.)
  return <Outlet />;
};

export default GuestGuard; 