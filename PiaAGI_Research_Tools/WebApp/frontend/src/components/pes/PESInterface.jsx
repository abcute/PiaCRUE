import React from 'react';
import { Link, Outlet, useLocation } from 'react-router-dom';

function PESInterface() {
  const location = useLocation();

  // Basic styling for sub-navigation
  const navLinkStyle = "px-4 py-2 mr-2 rounded-t-lg";
  const activeNavLinkStyle = "bg-slate-700 text-white";
  const inactiveNavLinkStyle = "bg-slate-500 hover:bg-slate-600 text-gray-200";

  // Determine if we are on a "new", "edit", or "view" page to hide sub-nav
  const isSubPage = location.pathname.includes("/prompt/") || location.pathname.includes("/curriculum/");

  return (
    <div className="pes-interface">
      <h1 className="text-2xl font-bold mb-4">Prompt Engineering System (PES)</h1>
      
      {!isSubPage && (
        <nav className="mb-6">
          <Link 
            to="/pes/prompts" 
            className={`${navLinkStyle} ${location.pathname.endsWith('/pes') || location.pathname.endsWith('/prompts') ? activeNavLinkStyle : inactiveNavLinkStyle}`}
          >
            Manage Prompts
          </Link>
          <Link 
            to="/pes/curricula" 
            className={`${navLinkStyle} ${location.pathname.endsWith('/curricula') ? activeNavLinkStyle : inactiveNavLinkStyle}`}
          >
            Manage Curricula
          </Link>
          <Link 
            to="/pes/prompt/new" 
            className={`${navLinkStyle} ${inactiveNavLinkStyle} bg-green-600 hover:bg-green-700`}
           >
            + New Prompt
          </Link>
          <Link 
            to="/pes/curriculum/new" 
            className={`${navLinkStyle} ${inactiveNavLinkStyle} bg-green-600 hover:bg-green-700`}
          >
            + New Curriculum
          </Link>
        </nav>
      )}
      
      {/* Nested routes will render here */}
      <Outlet /> 
    </div>
  );
}

export default PESInterface;
