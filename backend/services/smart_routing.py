import httpx
import os
from typing import Dict

# Mock broker configurations with their typical spreads + fees
BROKERS = {
    "alpha": {
        "url": os.getenv("BROKER_ALPHA_URL", "http://localhost:9001"),
        "fee_rate": 0.004,   # 0.4% commission
        "latency_ms": 12,
    },
    "beta": {
        "url": os.getenv("BROKER_BETA_URL", "http://localhost:9002"),
        "fee_rate": 0.006,   # 0.6% commission (higher but better liquidity)
        "latency_ms": 8,
    },
    "gamma": {
        "url": os.getenv("BROKER_GAMMA_URL", "http://localhost:9003"),
        "fee_rate": 0.003,   # Cheapest but slowest
        "latency_ms": 45,
    }
}

def select_best_broker(ticker: str, side: str, quantity: int, urgency: bool) -> str:
    """
    Smart order routing: pick broker based on:
    - Urgency → prioritize low latency
    - Normal → prioritize low fee
    
    In production: query each broker's live quotes, compare execution quality
    """
    if urgency:
        # Fastest broker for urgent orders
        return min(BROKERS, key=lambda b: BROKERS[b]["latency_ms"])
    else:
        # Cheapest broker for normal orders
        return min(BROKERS, key=lambda b: BROKERS[b]["fee_rate"])

async def route_order(order_id: int, ticker: str, side: str, quantity: int, price: float, urgency: bool) -> Dict:
    """
    Send order to external broker (mock API call)
    Returns execution confirmation or rejection
    """
    broker_name = select_best_broker(ticker, side, quantity, urgency)
    broker = BROKERS[broker_name]

    # Mock broker API call
    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            resp = await client.post(f"{broker['url']}/orders", json={
                "order_id": order_id,
                "ticker": ticker,
                "side": side,
                "quantity": quantity,
                "limit_price": price,
            })
            return {"broker": broker_name, "status": "routed", "response": resp.json()}
    except Exception:
        # Mock success response for development
        return {
            "broker": broker_name,
            "status": "routed",
            "execution_price": price * (0.9998 if side == "buy" else 1.0002),
            "filled_quantity": quantity
        }