import React from 'react';
import { Routes, Route } from 'react-router-dom';
import { SnackbarProvider } from 'notistack';
import { LocalizationProvider } from '@mui/x-date-pickers';
import { AdapterDateFns } from '@mui/x-date-pickers/AdapterDateFns';
import { AdapterJalaali } from '@mui/x-date-pickers/AdapterJalaali';
import { useTranslation } from 'react-i18next';
import Layout from './components/Layout';
import PrivateRoute from './components/PrivateRoute';
import routes from './routes';

const App: React.FC = () => {
  const { i18n } = useTranslation();
  const isRTL = i18n.language === 'fa';

  return (
    <SnackbarProvider maxSnack={3}>
      <LocalizationProvider dateAdapter={isRTL ? AdapterJalaali : AdapterDateFns}>
        <Layout>
          <Routes>
            {routes.map((route) => (
              <Route
                key={route.path}
                path={route.path}
                element={
                  route.private ? (
                    <PrivateRoute>{route.element}</PrivateRoute>
                  ) : (
                    route.element
                  )
                }
              />
            ))}
          </Routes>
        </Layout>
      </LocalizationProvider>
    </SnackbarProvider>
  );
};

export default App; 