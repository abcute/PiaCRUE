import React from 'react';
import { Link } from 'react-router-dom';

function Navigation() {
  return (
    <nav className="app-nav">
      <ul>
        <li><Link to="/">Home</Link></li>
        <li><Link to="/cml">CML</Link></li>
        <li><Link to="/pes">PES</Link></li>
        <li><Link to="/se">SE</Link></li>
        <li><Link to="/avt">AVT</Link></li>
        <li><Link to="/settings">Settings</Link></li>
      </ul>
    </nav>
  );
}

export default Navigation;
