import axios from 'axios';

const api = axios.create({ baseURL: 'http://localhost:8000/api' });

// Market Data
export const getAllPrices = () => api.get('/market/prices/all');
export const getOrderBook = (ticker: string) => api.get(`/market/orderbook/${ticker}`);

// Orders
export const submitOrder = (payload: {
  ticker: string; side: string; order_type: string;
  quantity: number; limit_price?: number; user_id: number; is_urgent?: boolean;
}) => api.post('/orders/', payload);

export const getUserOrders = (userId: number) => api.get(`/orders/user/${userId}`);
export const cancelOrder = (orderId: number) => api.delete(`/orders/${orderId}`);

// Admin
export const getAdminMetrics = () => api.get('/admin/metrics');
export const getRecentTrades = () => api.get('/admin/trades/recent');

export default api;