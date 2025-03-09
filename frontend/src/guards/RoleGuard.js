import React from 'react';
import PropTypes from 'prop-types';
import { Navigate, Outlet } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';

const RoleGuard = ({ roles }) => {
  const { user, isAuthenticated, isInitialized } = useAuth();

  // If auth is still initializing, show nothing
  if (!isInitialized) {
    return null;
  }

  // If not authenticated, redirect to login
  if (!isAuthenticated) {
    return <Navigate to="/auth/login" replace />;
  }

  // Check if user has required roles
  const hasRequiredRoles = roles.some(role => user?.roles?.includes(role));

  // If user doesn't have required roles, redirect to dashboard
  if (!hasRequiredRoles) {
    return <Navigate to="/" replace />;
  }

  // If user has required roles, render the child routes
  return <Outlet />;
};

RoleGuard.propTypes = {
  roles: PropTypes.arrayOf(PropTypes.string).isRequired
};

export default RoleGuard; 