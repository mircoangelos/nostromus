import React from "react";
import { BrowserRouter, Routes, Route, Navigate } from "react-router-dom";
import { useKeycloak } from "@react-keycloak/web";

import SalesPage from "./features/sales/SalesPage";
import AdminPage from "./features/admin/AdminPage";
import HomePage from "./features/home/HomePage";
import UnauthorizedPage from "./features/unauthorized/UnauthorizedPage";
import IncidentsPage from "./features/incidents/IncidentsPage";
import ReportsPage from "./features/reports/ReportsPage";
import DecisionPanel from "./features/decision/DecisionPanel";

const RequireAuth = ({ roles, children }) => {
  const { keycloak } = useKeycloak();

  if (!keycloak.authenticated) return <Navigate to="/login" />;

  const userRoles = keycloak.tokenParsed?.realm_access?.roles || [];
  const hasRole = roles.some(role => userRoles.includes(role));

  return hasRole ? children : <Navigate to="/unauthorized" />;
};

const Login = () => {
  const { keycloak } = useKeycloak();
  keycloak.login();
  return <div>Redirigiendo a Keycloak...</div>;
};

const Logout = () => {
  const { keycloak } = useKeycloak();
  keycloak.clearToken();
  keycloak.logout({ redirectUri: window.location.origin, idTokenHint: keycloak.idToken });
  return <div>Saliendo...</div>;
};


function App() {
  const { keycloak, initialized } = useKeycloak();

  if (!initialized) return <div>Cargando Keycloak...</div>;

  return (
    <BrowserRouter>
      <Routes>
        <Route path="/login" element={<Login />} />
        <Route path="/logout" element={<Logout />} />
        <Route path="/unauthorized" element={<UnauthorizedPage />} />

        <Route path="/home" element={
          <RequireAuth roles={["admin", "threat_analyst"]}><HomePage /></RequireAuth>
        } />
        <Route path="/home/ventas" element={
          <RequireAuth roles={["admin", "threat_analyst"]}><SalesPage /></RequireAuth>
        } />
        <Route path="/home/user-admin" element={
          <RequireAuth roles={["admin"]}><AdminPage /></RequireAuth>
        } />

        <Route path="/incidents" element={
          <RequireAuth roles={["admin", "viewer"]}><IncidentsPage /></RequireAuth>
        } />

        <Route path="/reports" element={
          <RequireAuth roles={["admin", "viewer"]}><ReportsPage /></RequireAuth>
        } />

        <Route path="/decision-panel" element={
          <RequireAuth roles={["admin", "threat_analyst"]}><DecisionPanel /></RequireAuth>
        } />

        <Route path="*" element={<Navigate to="/home" />} />
      </Routes>
    </BrowserRouter>
  );
}

export default App;
