import { useEffect, useState } from 'react';
import { NavLink } from 'react-router-dom';
import { api } from '../api';

export default function Layout({ children }) {
  const [health, setHealth] = useState({ status: 'unknown', mode: 'UNKNOWN' });

  useEffect(() => {
    api.health()
      .then(res => setHealth(res))
      .catch(() => setHealth({ status: 'error', mode: 'OFFLINE' }));
  }, []);

  return (
    <div className="container">
      <aside className="sidebar">
        <div className="sidebar-header">
          SentinelMesh <span className="version-badge">v1.0</span>
        </div>
        <nav className="nav-links">
          <NavLink to="/" className={({isActive}) => `nav-link ${isActive ? 'active' : ''}`}>Dashboard</NavLink>
          <NavLink to="/chat" className={({isActive}) => `nav-link ${isActive ? 'active' : ''}`}>Chat</NavLink>
          <NavLink to="/compare" className={({isActive}) => `nav-link ${isActive ? 'active' : ''}`}>Compare</NavLink>
          <NavLink to="/forensics" className={({isActive}) => `nav-link ${isActive ? 'active' : ''}`}>Forensics</NavLink>
          <NavLink to="/benchmark" className={({isActive}) => `nav-link ${isActive ? 'active' : ''}`}>Benchmark</NavLink>
        </nav>
        <div className="sidebar-footer">
          Mode: {health.mode}
        </div>
      </aside>
      <main className="main-content">
        <header className="topbar">
          <div className="topbar-title">SentinelMesh Security Console</div>
          <div className="status-indicator">
            <div className={`status-dot ${health.status === 'ok' ? 'healthy' : 'error'}`}></div>
            {health.status === 'ok' ? 'System Online' : 'Backend Unreachable'}
          </div>
        </header>
        <div className="page-content">
          {children}
        </div>
      </main>
    </div>
  );
}
