import React from 'react';
import Navbar from '../common/NavBar';

const HomePage = () => {
  return (
    <div className="page">
      <Navbar />
      <main className="home-content">
        <h1>Bienvenido a la página principal</h1>
        <p>contenido público.</p>
      </main>
    </div>
  );
};

export default HomePage;