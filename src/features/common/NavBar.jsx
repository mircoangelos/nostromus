import React from 'react';
import { Link } from 'react-router-dom';

const Navbar = () => {
  return (
    <nav className="navbar">
      <ul>
        <li><Link to="/home">Home</Link></li>
        <li><Link to="/home/ventas">Sales</Link></li>
        <li><Link to="/home/user-admin">Admin</Link></li>
      </ul>
    </nav>
  );
};

export default Navbar;