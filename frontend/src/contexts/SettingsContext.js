import React, { createContext, useContext, useState, useEffect } from 'react';
import PropTypes from 'prop-types';

// Default settings
const defaultSettings = {
  theme: 'light', // 'light' or 'dark'
  language: 'en', // 'en', 'fa', etc.
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
const SettingsContext = createContext({
  settings: defaultSettings,
  saveSettings: () => {},
  resetSettings: () => {}
});

// Provider
export const SettingsProvider = ({ children }) => {
  // Load settings from localStorage or use defaults
  const [settings, setSettings] = useState(() => {
    const storedSettings = localStorage.getItem('settings');
    return storedSettings ? JSON.parse(storedSettings) : defaultSettings;
  });

  // Save settings to localStorage when changed
  useEffect(() => {
    localStorage.setItem('settings', JSON.stringify(settings));
  }, [settings]);

  // Update settings
  const saveSettings = (newSettings) => {
    setSettings((prevSettings) => ({
      ...prevSettings,
      ...newSettings
    }));
  };

  // Reset settings to defaults
  const resetSettings = () => {
    localStorage.removeItem('settings');
    setSettings(defaultSettings);
  };

  return (
    <SettingsContext.Provider
      value={{
        settings,
        saveSettings,
        resetSettings
      }}
    >
      {children}
    </SettingsContext.Provider>
  );
};

SettingsProvider.propTypes = {
  children: PropTypes.node.isRequired
};

// Hook
export const useSettings = () => useContext(SettingsContext);

export default SettingsContext; 