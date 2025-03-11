/**
 * Settings context for the 3X-UI Management System.
 * 
 * This module provides settings state and methods for the application.
 */

import React, { createContext, useContext, useEffect, useReducer } from 'react';
import PropTypes from 'prop-types';
import { useTranslation } from 'react-i18next';
import { createTheme, ThemeProvider, responsiveFontSizes } from '@mui/material/styles';
import { CssBaseline } from '@mui/material';
import { lightTheme, darkTheme } from '../theme';

// Initial state
const initialState = {
  direction: localStorage.getItem('direction') || 'rtl',
  theme: localStorage.getItem('theme') || 'light',
  language: localStorage.getItem('language') || 'fa',
  dateFormat: localStorage.getItem('dateFormat') || 'jalali',
  currency: localStorage.getItem('currency') || 'IRR',
  notifications: JSON.parse(localStorage.getItem('notifications')) || {
    email: true,
    push: true,
    sms: false,
  },
};

// Action types
const ActionTypes = {
  CHANGE_DIRECTION: 'CHANGE_DIRECTION',
  CHANGE_THEME: 'CHANGE_THEME',
  CHANGE_LANGUAGE: 'CHANGE_LANGUAGE',
  CHANGE_DATE_FORMAT: 'CHANGE_DATE_FORMAT',
  CHANGE_CURRENCY: 'CHANGE_CURRENCY',
  CHANGE_NOTIFICATIONS: 'CHANGE_NOTIFICATIONS',
  RESET_SETTINGS: 'RESET_SETTINGS',
};

// Reducer
const reducer = (state, action) => {
  switch (action.type) {
    case ActionTypes.CHANGE_DIRECTION:
      localStorage.setItem('direction', action.payload);
      return {
        ...state,
        direction: action.payload,
      };

    case ActionTypes.CHANGE_THEME:
      localStorage.setItem('theme', action.payload);
      return {
        ...state,
        theme: action.payload,
      };

    case ActionTypes.CHANGE_LANGUAGE:
      localStorage.setItem('language', action.payload);
      return {
        ...state,
        language: action.payload,
      };

    case ActionTypes.CHANGE_DATE_FORMAT:
      localStorage.setItem('dateFormat', action.payload);
      return {
        ...state,
        dateFormat: action.payload,
      };

    case ActionTypes.CHANGE_CURRENCY:
      localStorage.setItem('currency', action.payload);
      return {
        ...state,
        currency: action.payload,
      };

    case ActionTypes.CHANGE_NOTIFICATIONS:
      localStorage.setItem('notifications', JSON.stringify(action.payload));
      return {
        ...state,
        notifications: action.payload,
      };

    case ActionTypes.RESET_SETTINGS:
      localStorage.removeItem('direction');
      localStorage.removeItem('theme');
      localStorage.removeItem('language');
      localStorage.removeItem('dateFormat');
      localStorage.removeItem('currency');
      localStorage.removeItem('notifications');
      return initialState;

    default:
      return state;
  }
};

// Create context
const SettingsContext = createContext(null);

/**
 * Settings provider component
 */
export const SettingsProvider = ({ children }) => {
  const { i18n } = useTranslation();
  const [state, dispatch] = useReducer(reducer, initialState);

  const changeDirection = (direction) => {
    dispatch({
      type: ActionTypes.CHANGE_DIRECTION,
      payload: direction,
    });
  };

  const changeTheme = (theme) => {
    dispatch({
      type: ActionTypes.CHANGE_THEME,
      payload: theme,
    });
  };

  const changeLanguage = (language) => {
    dispatch({
      type: ActionTypes.CHANGE_LANGUAGE,
      payload: language,
    });
  };

  const changeDateFormat = (format) => {
    dispatch({
      type: ActionTypes.CHANGE_DATE_FORMAT,
      payload: format,
    });
  };

  const changeCurrency = (currency) => {
    dispatch({
      type: ActionTypes.CHANGE_CURRENCY,
      payload: currency,
    });
  };

  const changeNotifications = (notifications) => {
    dispatch({
      type: ActionTypes.CHANGE_NOTIFICATIONS,
      payload: notifications,
    });
  };

  const resetSettings = () => {
    dispatch({
      type: ActionTypes.RESET_SETTINGS,
    });
  };

  // Update document direction when direction changes
  useEffect(() => {
    document.dir = state.direction;
  }, [state.direction]);

  // Create theme based on current settings
  const theme = responsiveFontSizes(
    createTheme(
      state.theme === 'dark' ? darkTheme : lightTheme,
      {
        direction: state.direction,
      }
    )
  );

  return (
    <SettingsContext.Provider
      value={{
        ...state,
        changeDirection,
        changeTheme,
        changeLanguage,
        changeDateFormat,
        changeCurrency,
        changeNotifications,
        resetSettings,
      }}
    >
      <ThemeProvider theme={theme}>
        <CssBaseline />
        {children}
      </ThemeProvider>
    </SettingsContext.Provider>
  );
};

SettingsProvider.propTypes = {
  children: PropTypes.node.isRequired,
};

/**
 * Hook for using the settings context
 */
export const useSettings = () => {
  const context = useContext(SettingsContext);

  if (!context) {
    throw new Error('useSettings must be used within a SettingsProvider');
  }

  return context;
};

export default SettingsContext; 