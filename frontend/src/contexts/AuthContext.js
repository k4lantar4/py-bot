import React, { createContext, useContext, useEffect, useReducer, useState } from 'react';
import PropTypes from 'prop-types';
import { jwtDecode } from 'jwt-decode';
import { useSnackbar } from 'notistack';
import api from '../services/api';

// Initial state
const initialState = {
  isAuthenticated: false,
  isInitializing: true,
  user: null
};

// Create context
const AuthContext = createContext({
  ...initialState,
  login: () => Promise.resolve(),
  logout: () => Promise.resolve(),
  register: () => Promise.resolve(),
  updateProfile: () => Promise.resolve()
});

// Actions
const SET_AUTH = 'SET_AUTH';
const LOGOUT = 'LOGOUT';
const INITIALIZE = 'INITIALIZE';
const UPDATE_USER = 'UPDATE_USER';

// Reducer
const reducer = (state, action) => {
  switch (action.type) {
    case INITIALIZE:
      return {
        ...state,
        isAuthenticated: action.payload.isAuthenticated,
        user: action.payload.user,
        isInitializing: false
      };
    case SET_AUTH:
      return {
        ...state,
        isAuthenticated: true,
        user: action.payload.user
      };
    case LOGOUT:
      return {
        ...state,
        isAuthenticated: false,
        user: null
      };
    case UPDATE_USER:
      return {
        ...state,
        user: {
          ...state.user,
          ...action.payload
        }
      };
    default:
      return state;
  }
};

// Provider
export const AuthProvider = ({ children }) => {
  const [state, dispatch] = useReducer(reducer, initialState);
  const { enqueueSnackbar } = useSnackbar();

  // Initialize auth from localStorage
  useEffect(() => {
    const initialize = async () => {
      try {
        const accessToken = localStorage.getItem('accessToken');
        const refreshToken = localStorage.getItem('refreshToken');

        if (accessToken && refreshToken) {
          // Validate token and get user data
          try {
            api.setAuthToken(accessToken);
            const decodedToken = jwtDecode(accessToken);

            // Check if token is expired
            if (decodedToken.exp * 1000 < Date.now()) {
              // Try to refresh token
              const response = await api.post('/auth/refresh-token', { refreshToken });
              const { access_token, refresh_token } = response.data;
              
              localStorage.setItem('accessToken', access_token);
              localStorage.setItem('refreshToken', refresh_token);
              api.setAuthToken(access_token);
              
              // Get user data
              const { data: user } = await api.get('/users/me');
              
              dispatch({
                type: INITIALIZE,
                payload: {
                  isAuthenticated: true,
                  user
                }
              });
            } else {
              // Get user data
              const { data: user } = await api.get('/users/me');
              
              dispatch({
                type: INITIALIZE,
                payload: {
                  isAuthenticated: true,
                  user
                }
              });
            }
          } catch (error) {
            console.error('Failed to validate token', error);
            localStorage.removeItem('accessToken');
            localStorage.removeItem('refreshToken');
            
            dispatch({
              type: INITIALIZE,
              payload: {
                isAuthenticated: false,
                user: null
              }
            });
          }
        } else {
          dispatch({
            type: INITIALIZE,
            payload: {
              isAuthenticated: false,
              user: null
            }
          });
        }
      } catch (error) {
        console.error('Failed to initialize auth', error);
        dispatch({
          type: INITIALIZE,
          payload: {
            isAuthenticated: false,
            user: null
          }
        });
      }
    };

    initialize();
  }, []);

  // Login
  const login = async (email, password) => {
    try {
      const response = await api.post('/auth/login', {
        username: email,
        password
      });

      const { access_token, refresh_token, user } = response.data;

      localStorage.setItem('accessToken', access_token);
      localStorage.setItem('refreshToken', refresh_token);
      
      api.setAuthToken(access_token);

      dispatch({
        type: SET_AUTH,
        payload: {
          user
        }
      });

      enqueueSnackbar('Login successful! Welcome back!', { variant: 'success' });
      return response;
    } catch (error) {
      enqueueSnackbar(error.response?.data?.detail || 'Login failed', { variant: 'error' });
      throw error;
    }
  };

  // Logout
  const logout = async () => {
    try {
      await api.post('/auth/logout');
    } catch (error) {
      console.error('Logout error', error);
    }

    localStorage.removeItem('accessToken');
    localStorage.removeItem('refreshToken');
    api.setAuthToken(null);
    
    dispatch({ type: LOGOUT });
    enqueueSnackbar('You have been logged out successfully', { variant: 'success' });
  };

  // Register
  const register = async (userData) => {
    try {
      const response = await api.post('/auth/register', userData);
      enqueueSnackbar('Registration successful! Please log in.', { variant: 'success' });
      return response;
    } catch (error) {
      enqueueSnackbar(error.response?.data?.detail || 'Registration failed', { variant: 'error' });
      throw error;
    }
  };

  // Update profile
  const updateProfile = async (userData) => {
    try {
      const response = await api.put('/users/me', userData);
      dispatch({
        type: UPDATE_USER,
        payload: response.data
      });
      enqueueSnackbar('Profile updated successfully!', { variant: 'success' });
      return response;
    } catch (error) {
      enqueueSnackbar(error.response?.data?.detail || 'Failed to update profile', { variant: 'error' });
      throw error;
    }
  };

  return (
    <AuthContext.Provider
      value={{
        ...state,
        login,
        logout,
        register,
        updateProfile,
        isInitialized: !state.isInitializing
      }}
    >
      {children}
    </AuthContext.Provider>
  );
};

AuthProvider.propTypes = {
  children: PropTypes.node.isRequired
};

// Hook
export const useAuth = () => useContext(AuthContext);

export default AuthContext; 