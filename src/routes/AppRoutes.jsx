import React from 'react';
import { Routes, Route } from 'react-router-dom';
import SalesPage from '../features/sales/SalesPage';

export const AppRoutes = () => (
  <Routes>
    <Route path="/sales" element={<SalesPage />} />
    {/* Puedes añadir /home, /admin, /unauthorized aquí también */}
  </Routes>
);