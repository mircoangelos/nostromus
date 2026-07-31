import React from 'react';
import { Link } from 'react-router-dom';

const UnauthorizedPage = () => {
  return (
    <div>
      <h1>Usuario no autorizado</h1>
      <p>No tienes permisos para acceder a esta sección.</p>
      <Link to="/">Volver al inicio</Link>
    </div>
  );
};

export default UnauthorizedPage;