import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import { I18nextProvider } from 'react-i18next';
import i18n from './i18n';
import { ToastProvider } from './components/common/Toast';
import Sidebar from './components/layout/Sidebar';
import Dashboard from './components/dashboard/Dashboard';
import PointsMenu from './components/points/PointsMenu';
import './styles/App.css';

function App() {
  return (
    <I18nextProvider i18n={i18n}>
      <ToastProvider>
        <Router>
          <div className="app-container">
            <Sidebar />
            <main className="main-content">
              <Routes>
                <Route path="/" element={<Dashboard />} />
                <Route path="/points" element={<PointsMenu />} />
              </Routes>
            </main>
          </div>
        </Router>
      </ToastProvider>
    </I18nextProvider>
  );
}

export default App; 