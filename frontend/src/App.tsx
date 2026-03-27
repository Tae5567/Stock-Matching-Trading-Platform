import React, { useState } from 'react';
import { LiveTicker } from './components/Ticker';
import { TradingTerminal } from './pages/TradingTerminal';
import { AdminDashboard } from './pages/AdminDashboard';

const NAV = ['Terminal', 'Portfolio', 'Admin'];

function App() {
  const [page, setPage] = useState('Terminal');
  return (
    <div style={{ display: 'flex', flexDirection: 'column', height: '100vh', background: '#020817', color: '#f8fafc' }}>
      {/* Top bar with live prices */}
      <LiveTicker />

      {/* Navigation */}
      <nav style={{ display: 'flex', gap: '0', background: '#0f172a', borderBottom: '1px solid #1e293b' }}>
        <div style={{ padding: '0.6rem 1.25rem', color: '#2563eb', fontFamily: 'monospace', fontWeight: 700, borderRight: '1px solid #1e293b' }}>
          ◆ STOCKMATCH
        </div>
        {NAV.map(n => (
          <button key={n} onClick={() => setPage(n)} style={{
            padding: '0.6rem 1.25rem', background: 'transparent',
            color: page === n ? '#f8fafc' : '#64748b',
            border: 'none', borderBottom: page === n ? '2px solid #2563eb' : '2px solid transparent',
            cursor: 'pointer', fontFamily: 'monospace', fontSize: '0.85rem'
          }}>
            {n}
          </button>
        ))}
      </nav>

      {/* Content */}
      <div style={{ flex: 1, overflow: 'auto' }}>
        {page === 'Terminal' && <TradingTerminal />}
        {page === 'Admin' && <AdminDashboard />}
        {page === 'Portfolio' && (
          <div style={{ padding: '2rem', fontFamily: 'monospace', color: '#64748b' }}>
            Portfolio page — connect to /api/positions/user/:id
          </div>
        )}
      </div>
    </div>
  );
}
export default App;