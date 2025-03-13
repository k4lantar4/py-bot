import React, { useState, useMemo } from 'react';
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { ThemeProvider, createTheme, CssBaseline } from '@mui/material';
import { blue, deepOrange } from '@mui/material/colors';
import rtlPlugin from 'stylis-plugin-rtl';
import { prefixer } from 'stylis';
import { CacheProvider } from '@emotion/react';
import createCache from '@emotion/cache';
import { I18nextProvider } from 'react-i18next';
import i18n from './i18n';

// Routes
import AuthRoutes from './routes/AuthRoutes';

// Create rtl cache
const rtlCache = createCache({
  key: 'muirtl',
  stylisPlugins: [prefixer, rtlPlugin],
});

// Create ltr cache
const ltrCache = createCache({
  key: 'muiltr',
  stylisPlugins: [prefixer],
});

function App() {
  // State for dark/light mode
  const [mode, setMode] = useState<'light' | 'dark'>('dark');
  
  // State for direction (RTL/LTR)
  const [isRtl, setIsRtl] = useState<boolean>(true);
  
  // Toggle theme mode
  const toggleTheme = () => {
    setMode((prevMode) => (prevMode === 'light' ? 'dark' : 'light'));
  };
  
  // Toggle language/direction
  const toggleLanguage = () => {
    const newIsRtl = !isRtl;
    setIsRtl(newIsRtl);
    
    // Change language in i18n
    i18n.changeLanguage(newIsRtl ? 'fa' : 'en');
    
    // Change HTML dir attribute
    document.dir = newIsRtl ? 'rtl' : 'ltr';
  };
  
  // Create theme with Persian fonts and RTL/LTR support
  const theme = useMemo(
    () =>
      createTheme({
        direction: isRtl ? 'rtl' : 'ltr',
        palette: {
          mode,
          primary: blue,
          secondary: deepOrange,
          background: {
            default: mode === 'dark' ? '#121212' : '#f5f5f5',
            paper: mode === 'dark' ? '#1e1e1e' : '#ffffff',
          },
        },
        typography: {
          fontFamily: isRtl 
            ? '"Vazir", "Roboto", "Helvetica", "Arial", sans-serif'
            : '"Roboto", "Helvetica", "Arial", sans-serif',
        },
        shape: {
          borderRadius: 8,
        },
        components: {
          MuiButton: {
            styleOverrides: {
              root: {
                borderRadius: 8,
                textTransform: 'none',
              },
            },
          },
        },
      }),
    [mode, isRtl]
  );
  
  return (
    <I18nextProvider i18n={i18n}>
      <CacheProvider value={isRtl ? rtlCache : ltrCache}>
        <ThemeProvider theme={theme}>
          <CssBaseline />
          <BrowserRouter>
            <Routes>
              {/* Render AuthRoutes with toggleTheme and toggleLanguage props */}
              <Route
                path="/auth/*"
                element={React.cloneElement(AuthRoutes.element as React.ReactElement, {
                  toggleTheme,
                  toggleLanguage,
                })}
              >
                {AuthRoutes.children?.map((route) => (
                  <Route
                    key={route.path}
                    path={route.path}
                    element={route.element}
                  />
                ))}
              </Route>
              
              {/* Add other routes here */}
              
              {/* Redirect root to auth/login */}
              <Route
                path="/"
                element={<Navigate to="/auth/login" replace />}
              />
              
              {/* Catch-all route */}
              <Route
                path="*"
                element={<Navigate to="/auth/login" replace />}
              />
            </Routes>
          </BrowserRouter>
        </ThemeProvider>
      </CacheProvider>
    </I18nextProvider>
  );
}

export default App; 