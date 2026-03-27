import React, { useEffect, useState, useRef } from 'react';

interface PriceData {
  ticker: string;
  price: number;
  change: number;
  change_pct: number;
  volume: number;
}

export const LiveTicker: React.FC = () => {
  const [prices, setPrices] = useState<Record<string, PriceData>>({});
  const wsRef = useRef<WebSocket | null>(null);

  useEffect(() => {
    // Connect to WebSocket for real-time price updates
    wsRef.current = new WebSocket('ws://localhost:8000/api/market/ws/prices');
    wsRef.current.onmessage = (e) => {
      setPrices(JSON.parse(e.data));
    };
    return () => wsRef.current?.close();
  }, []);

  return (
    <div style={{
      display: 'flex', gap: '0', overflowX: 'auto',
      background: '#0f172a', borderBottom: '1px solid #1e293b'
    }}>
      {Object.values(prices).map(p => (
        <div key={p.ticker} style={{
          padding: '0.5rem 1.25rem',
          borderRight: '1px solid #1e293b',
          minWidth: '130px',
          flexShrink: 0
        }}>
          <div style={{ color: '#94a3b8', fontSize: '0.7rem', fontFamily: 'monospace' }}>
            {p.ticker}
          </div>
          <div style={{ color: '#f8fafc', fontSize: '0.95rem', fontWeight: 600, fontFamily: 'monospace' }}>
            ${p.price.toFixed(2)}
          </div>
          <div style={{
            fontSize: '0.7rem', fontFamily: 'monospace',
            color: p.change >= 0 ? '#4ade80' : '#f87171'
          }}>
            {p.change >= 0 ? '+' : ''}{p.change.toFixed(2)} ({p.change_pct.toFixed(2)}%)
          </div>
        </div>
      ))}
    </div>
  );
};