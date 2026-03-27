import React, { useEffect, useState } from 'react';
import { AreaChart, Area, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts';
import { getAdminMetrics, getRecentTrades } from '../api/client';

export const AdminDashboard: React.FC = () => {
  const [metrics, setMetrics] = useState<any>(null);
  const [trades, setTrades] = useState<any[]>([]);

  useEffect(() => {
    const refresh = () => {
      getAdminMetrics().then(r => setMetrics(r.data));
      getRecentTrades().then(r => setTrades(r.data));
    };
    refresh();
    const i = setInterval(refresh, 10000);
    return () => clearInterval(i);
  }, []);

  const chartData = trades.slice(0, 20).reverse().map((t, i) => ({
    name: `#${t.id}`, price: t.price, volume: t.trade_value
  }));

  if (!metrics) return <div style={{ color: '#94a3b8', padding: '2rem', fontFamily: 'monospace' }}>Loading...</div>;

  return (
    <div style={{ padding: '1.5rem', color: '#f8fafc' }}>
      <h2 style={{ fontFamily: 'monospace', marginBottom: '1.5rem' }}>Admin Dashboard</h2>

      {/* KPIs */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(5, 1fr)', gap: '0.75rem', marginBottom: '1.5rem' }}>
        {[
          { label: 'Total Trades', val: metrics.total_trades },
          { label: 'Today', val: metrics.trades_today },
          { label: 'Total Volume', val: `$${(metrics.total_volume_usd / 1e6).toFixed(1)}M` },
          { label: 'Commission', val: `$${metrics.platform_commission_usd.toFixed(0)}` },
          { label: 'Open Orders', val: metrics.open_orders },
        ].map(({ label, val }) => (
          <div key={label} style={{ background: '#1e293b', padding: '1rem', borderRadius: '8px', border: '1px solid #334155' }}>
            <div style={{ color: '#64748b', fontSize: '0.7rem', fontFamily: 'monospace', marginBottom: '0.4rem' }}>{label}</div>
            <div style={{ fontSize: '1.4rem', fontWeight: 700, fontFamily: 'monospace' }}>{val}</div>
          </div>
        ))}
      </div>

      {/* Trade price chart */}
      <div style={{ background: '#1e293b', padding: '1rem', borderRadius: '8px', border: '1px solid #334155', marginBottom: '1.5rem' }}>
        <h4 style={{ margin: '0 0 1rem', color: '#94a3b8', fontFamily: 'monospace' }}>Recent Trade Prices</h4>
        <ResponsiveContainer width="100%" height={200}>
          <AreaChart data={chartData}>
            <defs>
              <linearGradient id="pGrad" x1="0" y1="0" x2="0" y2="1">
                <stop offset="5%" stopColor="#2563eb" stopOpacity={0.4} />
                <stop offset="95%" stopColor="#2563eb" stopOpacity={0} />
              </linearGradient>
            </defs>
            <CartesianGrid strokeDasharray="3 3" stroke="#334155" />
            <XAxis dataKey="name" stroke="#64748b" tick={{ fontSize: 10, fontFamily: 'monospace' }} />
            <YAxis stroke="#64748b" tick={{ fontSize: 10, fontFamily: 'monospace' }} />
            <Tooltip contentStyle={{ background: '#0f172a', border: '1px solid #334155', fontFamily: 'monospace', fontSize: '0.75rem' }} />
            <Area type="monotone" dataKey="price" stroke="#2563eb" fill="url(#pGrad)" strokeWidth={2} />
          </AreaChart>
        </ResponsiveContainer>
      </div>

      {/* Trade history */}
      <div style={{ background: '#1e293b', borderRadius: '8px', border: '1px solid #334155', overflow: 'hidden' }}>
        <div style={{ padding: '0.75rem 1rem', borderBottom: '1px solid #334155' }}>
          <h4 style={{ margin: 0, color: '#94a3b8', fontFamily: 'monospace' }}>Trade History</h4>
        </div>
        <table style={{ width: '100%', borderCollapse: 'collapse', fontFamily: 'monospace', fontSize: '0.78rem' }}>
          <thead>
            <tr style={{ background: '#0f172a' }}>
              {['ID','Ticker','Qty','Price','Value','Time'].map(h => (
                <th key={h} style={{ padding: '0.5rem 0.75rem', color: '#64748b', textAlign: 'left', fontWeight: 500 }}>{h}</th>
              ))}
            </tr>
          </thead>
          <tbody>
            {trades.slice(0, 30).map((t: any) => (
              <tr key={t.id} style={{ borderTop: '1px solid #0f172a' }}>
                <td style={{ padding: '0.4rem 0.75rem', color: '#475569' }}>#{t.id}</td>
                <td style={{ color: '#f8fafc', fontWeight: 600 }}>{t.ticker}</td>
                <td style={{ color: '#94a3b8' }}>{t.quantity}</td>
                <td style={{ color: '#4ade80' }}>${t.price.toFixed(2)}</td>
                <td style={{ color: '#94a3b8' }}>${t.trade_value.toFixed(0)}</td>
                <td style={{ color: '#475569', fontSize: '0.7rem' }}>{new Date(t.executed_at).toLocaleTimeString()}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
};