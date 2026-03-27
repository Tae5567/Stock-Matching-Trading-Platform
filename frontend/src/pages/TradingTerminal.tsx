import React, { useState, useEffect } from 'react';
import { submitOrder, getOrderBook, getUserOrders } from '../api/client';

interface OrderBookLevel { price: number; qty: number; }

export const TradingTerminal: React.FC = () => {
  const [ticker, setTicker] = useState('AAPL');
  const [side, setSide] = useState<'buy' | 'sell'>('buy');
  const [orderType, setOrderType] = useState<'market' | 'limit'>('limit');
  const [quantity, setQuantity] = useState('');
  const [limitPrice, setLimitPrice] = useState('');
  const [orderBook, setOrderBook] = useState<{ bids: OrderBookLevel[]; asks: OrderBookLevel[]; spread: number | null }>({ bids: [], asks: [], spread: null });
  const [myOrders, setMyOrders] = useState<any[]>([]);
  const [message, setMessage] = useState('');

  const USER_ID = 1; // In production: from auth context

  useEffect(() => {
    const fetchBook = () => getOrderBook(ticker).then(r => setOrderBook(r.data));
    fetchBook();
    const interval = setInterval(fetchBook, 2000);
    return () => clearInterval(interval);
  }, [ticker]);

  useEffect(() => {
    getUserOrders(USER_ID).then(r => setMyOrders(r.data));
  }, []);

  const handleSubmit = async () => {
    if (!quantity) return;
    try {
      const res = await submitOrder({
        ticker, side, order_type: orderType,
        quantity: parseInt(quantity),
        limit_price: limitPrice ? parseFloat(limitPrice) : undefined,
        user_id: USER_ID
      });
      setMessage(`✓ Order #${res.data.order_id} submitted`);
      getUserOrders(USER_ID).then(r => setMyOrders(r.data));
    } catch {
      setMessage('✗ Order failed');
    }
  };

  const col = (c: string) => ({ color: c });
  const green = '#4ade80'; const red = '#f87171';

  return (
    <div style={{ display: 'grid', gridTemplateColumns: '1fr 280px 1fr', gap: '1rem', padding: '1rem', height: '100%' }}>

      {/* ORDER BOOK */}
      <div style={{ background: '#0f172a', borderRadius: '8px', padding: '1rem', border: '1px solid #1e293b' }}>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1rem' }}>
          <h3 style={{ color: '#f8fafc', margin: 0, fontFamily: 'monospace' }}>Order Book</h3>
          {orderBook.spread !== null && (
            <span style={{ color: '#94a3b8', fontSize: '0.75rem', fontFamily: 'monospace' }}>
              Spread: ${orderBook.spread.toFixed(4)}
            </span>
          )}
        </div>
        <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '0.25rem', fontSize: '0.78rem', fontFamily: 'monospace' }}>
          <div style={{ color: '#64748b' }}>Price</div>
          <div style={{ color: '#64748b', textAlign: 'right' }}>Qty</div>
          {/* Asks (sells) — displayed top, red */}
          {[...orderBook.asks].reverse().map((a, i) => (
            <React.Fragment key={i}>
              <div style={col(red)}>${a.price.toFixed(2)}</div>
              <div style={{ color: '#94a3b8', textAlign: 'right' }}>{a.qty.toLocaleString()}</div>
            </React.Fragment>
          ))}
          <div style={{ gridColumn: '1/-1', borderTop: '1px solid #334155', margin: '0.25rem 0' }} />
          {/* Bids (buys) — green */}
          {orderBook.bids.map((b, i) => (
            <React.Fragment key={i}>
              <div style={col(green)}>${b.price.toFixed(2)}</div>
              <div style={{ color: '#94a3b8', textAlign: 'right' }}>{b.qty.toLocaleString()}</div>
            </React.Fragment>
          ))}
        </div>
      </div>

      {/* ORDER FORM */}
      <div style={{ background: '#0f172a', borderRadius: '8px', padding: '1.25rem', border: '1px solid #1e293b' }}>
        <h3 style={{ color: '#f8fafc', marginTop: 0, fontFamily: 'monospace' }}>Place Order</h3>

        {/* Ticker selector */}
        <select value={ticker} onChange={e => setTicker(e.target.value)}
          style={{ width: '100%', padding: '0.5rem', marginBottom: '0.75rem', background: '#1e293b', color: '#f8fafc', border: '1px solid #334155', borderRadius: '4px', fontFamily: 'monospace', fontSize: '0.9rem' }}>
          {['AAPL','TSLA','MSFT','GOOGL','AMZN','NVDA','META'].map(t => (
            <option key={t} value={t}>{t}</option>
          ))}
        </select>

        {/* Buy / Sell toggle */}
        <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', marginBottom: '0.75rem' }}>
          {(['buy', 'sell'] as const).map(s => (
            <button key={s} onClick={() => setSide(s)} style={{
              padding: '0.6rem', border: 'none', cursor: 'pointer', fontWeight: 700,
              borderRadius: s === 'buy' ? '4px 0 0 4px' : '0 4px 4px 0',
              background: side === s ? (s === 'buy' ? '#16a34a' : '#dc2626') : '#1e293b',
              color: side === s ? 'white' : '#64748b', fontFamily: 'monospace',
              textTransform: 'uppercase', letterSpacing: '0.05em'
            }}>
              {s}
            </button>
          ))}
        </div>

        {/* Order type */}
        <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', marginBottom: '0.75rem' }}>
          {(['market', 'limit'] as const).map(t => (
            <button key={t} onClick={() => setOrderType(t)} style={{
              padding: '0.4rem', border: '1px solid #334155', cursor: 'pointer',
              borderRadius: t === 'market' ? '4px 0 0 4px' : '0 4px 4px 0',
              background: orderType === t ? '#2563eb' : '#1e293b',
              color: orderType === t ? 'white' : '#64748b',
              fontFamily: 'monospace', fontSize: '0.8rem', textTransform: 'uppercase'
            }}>
              {t}
            </button>
          ))}
        </div>

        {/* Quantity */}
        <input type="number" placeholder="Quantity (shares)" value={quantity}
          onChange={e => setQuantity(e.target.value)}
          style={{ width: '100%', padding: '0.5rem', marginBottom: '0.5rem', background: '#1e293b', color: '#f8fafc', border: '1px solid #334155', borderRadius: '4px', fontFamily: 'monospace', boxSizing: 'border-box' }} />

        {/* Limit price */}
        {orderType === 'limit' && (
          <input type="number" step="0.01" placeholder="Limit Price ($)" value={limitPrice}
            onChange={e => setLimitPrice(e.target.value)}
            style={{ width: '100%', padding: '0.5rem', marginBottom: '0.75rem', background: '#1e293b', color: '#f8fafc', border: '1px solid #334155', borderRadius: '4px', fontFamily: 'monospace', boxSizing: 'border-box' }} />
        )}

        <button onClick={handleSubmit} style={{
          width: '100%', padding: '0.75rem', border: 'none', cursor: 'pointer',
          background: side === 'buy' ? '#16a34a' : '#dc2626',
          color: 'white', fontWeight: 700, borderRadius: '4px',
          fontFamily: 'monospace', fontSize: '0.95rem', textTransform: 'uppercase', letterSpacing: '0.1em'
        }}>
          {side === 'buy' ? '▲' : '▼'} {side.toUpperCase()} {ticker}
        </button>

        {message && (
          <div style={{ marginTop: '0.75rem', padding: '0.5rem', background: '#1e293b', borderRadius: '4px', color: message.startsWith('✓') ? green : red, fontFamily: 'monospace', fontSize: '0.8rem' }}>
            {message}
          </div>
        )}
      </div>

      {/* MY ORDERS */}
      <div style={{ background: '#0f172a', borderRadius: '8px', padding: '1rem', border: '1px solid #1e293b', overflowY: 'auto' }}>
        <h3 style={{ color: '#f8fafc', marginTop: 0, fontFamily: 'monospace' }}>My Orders</h3>
        {myOrders.map((o: any) => (
          <div key={o.id} style={{ padding: '0.6rem', marginBottom: '0.4rem', background: '#1e293b', borderRadius: '4px', fontSize: '0.78rem', fontFamily: 'monospace' }}>
            <div style={{ display: 'flex', justifyContent: 'space-between' }}>
              <span style={{ color: o.side === 'buy' ? green : red, fontWeight: 700 }}>
                {o.side.toUpperCase()} {o.ticker}
              </span>
              <span style={{ color: '#94a3b8' }}>{o.status}</span>
            </div>
            <div style={{ color: '#64748b', marginTop: '0.2rem' }}>
              {o.filled_quantity}/{o.quantity} shares
              {o.limit_price ? ` @ $${o.limit_price}` : ' (MKT)'}
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};