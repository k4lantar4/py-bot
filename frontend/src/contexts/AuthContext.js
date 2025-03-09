/**
 * Authentication context for the 3X-UI Management System.
 * 
 * This module provides authentication state and methods for the application.
 */

import React, { createContext, useContext, useEffect, useReducer } from 'react';
import PropTypes from 'prop-types';
import { authAPI, userAPI } from '../services/api';

// Initial state
const initialState = {
  isAuthenticated: false,
  isInitialized: false,
  user: null,
};

// Action types
const ActionTypes = {
  INITIALIZE: 'INITIALIZE',
  LOGIN: 'LOGIN',
  LOGOUT: 'LOGOUT',
  UPDATE_USER: 'UPDATE_USER',
};

// Reducer for managing auth state
const reducer = (state, action) => {
  switch (action.type) {
    case ActionTypes.INITIALIZE:
      return {
        ...state,
        isAuthenticated: action.payload.isAuthenticated,
        isInitialized: true,
        user: action.payload.user,
      };
    
    case ActionTypes.LOGIN:
      return {
        ...state,
        isAuthenticated: true,
        user: action.payload.user,
      };
    
    case ActionTypes.LOGOUT:
      return {
        ...state,
        isAuthenticated: false,
        user: null,
      };
    
    case ActionTypes.UPDATE_USER:
      return {
        ...state,
        user: {
          ...state.user,
          ...action.payload.user,
        },
      };
    
    default:
      return state;
  }
};

// Create context
const AuthContext = createContext(null);

/**
 * Auth provider component.
 * 
 * @param {Object} props - Component props
 * @param {React.ReactNode} props.children - Child components
 */
export const AuthProvider = ({ children }) => {
  const [state, dispatch] = useReducer(reducer, initialState);
  
  /**
   * Initialize auth state from local storage or session.
   */
  const initialize = async () => {
    try {
      const accessToken = localStorage.getItem('accessToken');
      
      if (accessToken) {
        // Verify token and get user profile
        try {
          const user = await userAPI.getProfile();
          
          dispatch({
            type: ActionTypes.INITIALIZE,
            payload: {
              isAuthenticated: true,
              user,
            },
          });
        } catch (error) {
          console.error('Token verification failed:', error);
          
          // Token is invalid, clear local storage
          localStorage.removeItem('accessToken');
          localStorage.removeItem('refreshToken');
          
          dispatch({
            type: ActionTypes.INITIALIZE,
            payload: {
              isAuthenticated: false,
              user: null,
            },
          });
        }
      } else {
        dispatch({
          type: ActionTypes.INITIALIZE,
          payload: {
            isAuthenticated: false,
            user: null,
          },
        });
      }
    } catch (error) {
      console.error('Auth initialization error:', error);
      
      dispatch({
        type: ActionTypes.INITIALIZE,
        payload: {
          isAuthenticated: false,
          user: null,
        },
      });
    }
  };
  
  // Initialize on component mount
  useEffect(() => {
    initialize();
  }, []);
  
  /**
   * Login user with data from API.
   * 
   * @param {Object} user - User data
   * @param {Object} tokens - Auth tokens
   */
  const login = async (user, tokens) => {
    // Store tokens
    localStorage.setItem('accessToken', tokens.accessToken);
    localStorage.setItem('refreshToken', tokens.refreshToken);
    
    dispatch({
      type: ActionTypes.LOGIN,
      payload: {
        user,
      },
    });
  };
  
  /**
   * Logout current user.
   */
  const logout = async () => {
    try {
      // Call logout API
      await authAPI.logout();
    } catch (error) {
      console.error('Logout error:', error);
    } finally {
      // Remove tokens
      localStorage.removeItem('accessToken');
      localStorage.removeItem('refreshToken');
      
      dispatch({ type: ActionTypes.LOGOUT });
    }
  };
  
  /**
   * Register a new user.
   * 
   * @param {Object} userData - Registration data
   * @returns {Object} Registered user data
   */
  const register = async (userData) => {
    const response = await authAPI.register(userData);
    return response;
  };
  
  /**
   * Update user profile.
   * 
   * @param {Object} userData - User data to update
   */
  const updateProfile = async (userData) => {
    try {
      const updatedUser = await userAPI.updateProfile(userData);
      
      dispatch({
        type: ActionTypes.UPDATE_USER,
        payload: {
          user: updatedUser,
        },
      });
      
      return updatedUser;
    } catch (error) {
      console.error('Update profile error:', error);
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
      }}
    >
      {children}
    </AuthContext.Provider>
  );
};

AuthProvider.propTypes = {
  children: PropTypes.node.isRequired,
};

/**
 * Hook for using the auth context.
 * 
 * @returns {Object} Auth context
 */
export const useAuth = () => useContext(AuthContext);

export default AuthContext; 