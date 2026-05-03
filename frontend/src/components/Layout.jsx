import React from 'react';
import { Outlet, Link, useLocation, useNavigate } from 'react-router-dom';
import { LayoutDashboard, History, Upload, LogOut, FileText } from 'lucide-react';

export default function Layout() {
  const location = useLocation();
  const navigate = useNavigate();

  const handleLogout = () => {
    // Basic mock logout
    navigate('/login');
  };

  const navItems = [
    { path: '/', label: 'Dashboard', icon: LayoutDashboard },
    { path: '/history', label: 'History Store', icon: History },
    { path: '/upload', label: 'New Evaluation', icon: Upload },
    { path: '/demo', label: 'Run Demo', icon: FileText },
  ];

  return (
    <div style={{ display: 'flex', minHeight: '100vh' }}>
      {/* Sidebar */}
      <aside className="glass-panel fade-in delay-100" style={{ 
        width: 280, 
        margin: '20px 0 20px 20px', 
        display: 'flex', 
        flexDirection: 'column',
        borderRadius: 24,
        background: 'rgba(13, 17, 28, 0.75)'
      }}>
        {/* Logo Area */}
        <div style={{ padding: '32px 24px', display: 'flex', alignItems: 'center', gap: 12 }}>
          <div style={{
            width: 40, height: 40, borderRadius: 12,
            background: 'linear-gradient(135deg, var(--accent-blue), var(--accent-purple))',
            display: 'flex', alignItems: 'center', justifyContent: 'center',
            fontWeight: 'bold', fontSize: 20
          }}>
            P
          </div>
          <div>
            <div className="text-gradient" style={{ fontWeight: 800, fontSize: 20, letterSpacing: '-0.5px', fontFamily: 'Outfit' }}>ProcureAI</div>
            <div style={{ fontSize: 13, color: 'var(--accent-blue-glow)', fontWeight: 500 }}>AI Evaluation Hub</div>
          </div>
        </div>

        {/* Nav Links */}
        <nav style={{ flex: 1, padding: '0 16px', display: 'flex', flexDirection: 'column', gap: 8 }}>
          {navItems.map((item) => {
            const active = location.pathname === item.path || (item.path !== '/' && location.pathname.startsWith(item.path));
            const Icon = item.icon;
            return (
              <Link key={item.path} to={item.path} style={{
                textDecoration: 'none',
                display: 'flex', alignItems: 'center', gap: 12,
                padding: '12px 16px', borderRadius: 12,
                color: active ? 'white' : 'var(--text-secondary)',
                background: active ? 'rgba(59, 130, 246, 0.15)' : 'transparent',
                fontWeight: active ? 600 : 500,
                transition: 'all 0.2s',
                borderLeft: active ? '3px solid var(--accent-blue)' : '3px solid transparent'
              }}>
                <Icon size={20} color={active ? 'var(--accent-blue)' : 'var(--text-muted)'} />
                {item.label}
              </Link>
            );
          })}
        </nav>

        {/* User Profile / Logout */}
        <div style={{ padding: 24, borderTop: '1px solid var(--border-subtle)' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: 12, marginBottom: 16 }}>
            <div style={{
              width: 36, height: 36, borderRadius: '50%',
              background: 'var(--bg-input)', display: 'flex',
              alignItems: 'center', justifyContent: 'center'
            }}>
              <span style={{ fontSize: 16 }}>👮‍♂️</span>
            </div>
            <div>
              <div style={{ fontSize: 14, fontWeight: 600 }}>Admin User</div>
              <div style={{ fontSize: 12, color: 'var(--text-muted)' }}>Procurement Dept</div>
            </div>
          </div>
          <button onClick={handleLogout} style={{
            width: '100%', display: 'flex', alignItems: 'center', justifyContent: 'center', gap: 8,
            background: 'rgba(239, 68, 68, 0.1)', color: 'var(--accent-red)',
            border: 'none', padding: '10px', borderRadius: 8,
            cursor: 'pointer', fontWeight: 500, transition: 'all 0.2s'
          }}
          onMouseEnter={(e) => e.currentTarget.style.background = 'rgba(239, 68, 68, 0.2)'}
          onMouseLeave={(e) => e.currentTarget.style.background = 'rgba(239, 68, 68, 0.1)'}
          >
            <LogOut size={16} /> Logout
          </button>
        </div>
      </aside>

      {/* Main Content Area */}
      <main style={{ flex: 1, padding: '20px 40px', overflowY: 'auto' }}>
        <Outlet />
      </main>
    </div>
  );
}
