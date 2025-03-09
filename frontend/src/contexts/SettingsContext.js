/**
 * Settings context for the 3X-UI Management System.
 * 
 * This module provides settings state and methods for the application.
 */

import React, { createContext, useContext, useState, useEffect } from 'react';
import PropTypes from 'prop-types';
import { useTranslation } from 'react-i18next';
import { createTheme, ThemeProvider, responsiveFontSizes } from '@mui/material/styles';
import { CssBaseline } from '@mui/material';
import { lightTheme, darkTheme } from '../theme';

// Default settings
const defaultSettings = {
  themeMode: 'light',
  direction: 'ltr',
  language: 'en',
  pageSize: 10, // Number of items per page
  sidebarOpen: true, // Sidebar state (open/closed)
  notifications: {
    sound: true,
    pushEnabled: true,
    emailEnabled: true
  },
  dashboard: {
    refreshInterval: 60, // In seconds
    showServerStats: true,
    showFinancialStats: true,
    showUserStats: true
  }
};

// Create context
const SettingsContext = createContext(null);

/**
 * Settings provider component.
 * 
 * @param {Object} props - Component props
 * @param {React.ReactNode} props.children - Child components
 */
export const SettingsProvider = ({ children }) => {
  const { i18n } = useTranslation();
  
  // Load settings from localStorage or use defaults
  const [settings, setSettings] = useState(() => {
    const storedSettings = localStorage.getItem('settings');
    if (storedSettings) {
      const parsedSettings = JSON.parse(storedSettings);
      // Apply stored language
      if (parsedSettings.language) {
        i18n.changeLanguage(parsedSettings.language);
      }
      return parsedSettings;
    }
    return defaultSettings;
  });
  
  // Create theme based on current settings
  const theme = responsiveFontSizes(
    createTheme(
      settings.themeMode === 'dark' ? darkTheme : lightTheme,
      {
        direction: settings.direction,
      }
    )
  );
  
  // Update settings and save to localStorage
  const saveSettings = (newSettings) => {
    const updatedSettings = {
      ...settings,
      ...newSettings,
    };
    
    setSettings(updatedSettings);
    localStorage.setItem('settings', JSON.stringify(updatedSettings));
    
    // Update language if changed
    if (newSettings.language && newSettings.language !== settings.language) {
      i18n.changeLanguage(newSettings.language);
    }
  };
  
  // Reset settings to defaults
  const resetSettings = () => {
    setSettings(defaultSettings);
    localStorage.removeItem('settings');
    i18n.changeLanguage(defaultSettings.language);
  };
  
  // Change theme mode (light/dark)
  const toggleThemeMode = () => {
    saveSettings({
      themeMode: settings.themeMode === 'light' ? 'dark' : 'light',
    });
  };
  
  // Change language
  const changeLanguage = (lang) => {
    saveSettings({ language: lang });
  };
  
  // Apply direction based on language
  useEffect(() => {
    const isRtlLanguage = ['ar', 'fa', 'he'].includes(settings.language);
    if (isRtlLanguage && settings.direction !== 'rtl') {
      saveSettings({ direction: 'rtl' });
    } else if (!isRtlLanguage && settings.direction !== 'ltr') {
      saveSettings({ direction: 'ltr' });
    }
  }, [settings.language]);
  
  return (
    <SettingsContext.Provider
      value={{
        settings,
        theme,
        saveSettings,
        resetSettings,
        toggleThemeMode,
        changeLanguage,
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
 * Hook for using the settings context.
 * 
 * @returns {Object} Settings context
 */
export const useSettings = () => useContext(SettingsContext);

export default SettingsContext; 