import React from 'react';
import { Routes, Route, Navigate } from 'react-router-dom';

import Layout from './components/Layout';
import LoginPage from './pages/LoginPage';
import Dashboard from './pages/Dashboard';
import HistoryStore from './pages/HistoryStore';
import UploadPage from './pages/UploadPage';
import ReportPage from './pages/ReportPage';
import DemoPage from './pages/DemoPage';

export default function App() {
  return (
    <>
      <div className="animated-gradient-bg"></div>
      <Routes>
        <Route path="/login" element={<LoginPage />} />
        
        {/* Protected Routes Wrapper */}
        <Route element={<Layout />}>
          <Route path="/" element={<Dashboard />} />
          <Route path="/history" element={<HistoryStore />} />
          <Route path="/upload" element={<UploadPage />} />
          <Route path="/reports/:reportId" element={<ReportPage />} />
          <Route path="/demo" element={<DemoPage />} />
        </Route>

        {/* Catch-all redirect */}
        <Route path="*" element={<Navigate to="/" replace />} />
      </Routes>
    </>
  );
}
