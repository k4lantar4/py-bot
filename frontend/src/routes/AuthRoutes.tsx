import React from 'react';
import { RouteObject } from 'react-router-dom';

// Layouts
import AuthLayout from '../layouts/AuthLayout';

// Auth pages
import Login from '../pages/Auth/Login';
import Register from '../pages/Auth/Register';
import ForgotPassword from '../pages/Auth/ForgotPassword';

// Define authentication routes
const AuthRoutes: RouteObject = {
  path: 'auth',
  element: <AuthLayout />,
  children: [
    {
      path: 'login',
      element: <Login />,
    },
    {
      path: 'register',
      element: <Register />,
    },
    {
      path: 'forgot-password',
      element: <ForgotPassword />,
    },
    // Redirect to login page by default
    {
      path: '',
      element: <Login />,
    },
  ],
};

export default AuthRoutes; 