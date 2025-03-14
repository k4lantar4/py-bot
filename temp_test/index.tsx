import React from 'react';
import ReactDOM from 'react-dom/client';
import { Provider } from 'react-redux';
import { BrowserRouter } from 'react-router-dom';
import { ThemeProvider } from '@mui/material/styles';
import CssBaseline from '@mui/material/CssBaseline';
import { CacheProvider } from '@emotion/react';
import createCache from '@emotion/cache';
import rtlPlugin from 'stylis-plugin-rtl';
import { prefixer } from 'stylis';
import { I18nextProvider } from 'react-i18next';
import i18n from './i18n';
import { store } from './store';
import theme from './theme';
import App from './App';

// Create rtl cache
const cacheRtl = createCache({
  key: 'muirtl',
  stylisPlugins: [prefixer, rtlPlugin],
});

const root = ReactDOM.createRoot(
  document.getElementById('root') as HTMLElement
);

root.render(
  <React.StrictMode>
    <Provider store={store}>
      <I18nextProvider i18n={i18n}>
        <CacheProvider value={cacheRtl}>
          <ThemeProvider theme={theme}>
            <CssBaseline />
            <BrowserRouter>
              <App />
            </BrowserRouter>
          </ThemeProvider>
        </CacheProvider>
      </I18nextProvider>
    </Provider>
  </React.StrictMode>
); 