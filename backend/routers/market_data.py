from fastapi import APIRouter
from fastapi.websockets import WebSocket
import redis
import json
import asyncio
import os

router = APIRouter(prefix="/api/market", tags=["market-data"])
r = redis.from_url(os.getenv("REDIS_URL"))

@router.get("/price/{ticker}")
def get_price(ticker: str):
    """Get latest cached price for a ticker."""
    data = r.get(f"price:{ticker.upper()}")
    return json.loads(data) if data else {"error": "No data"}

@router.get("/orderbook/{ticker}")
def get_orderbook(ticker: str):
    """Get current order book depth snapshot."""
    data = r.get(f"orderbook:{ticker.upper()}")
    return json.loads(data) if data else {"bids": [], "asks": [], "spread": None}

@router.get("/prices/all")
def get_all_prices():
    """Get prices for all tracked tickers."""
    tickers = ["AAPL", "TSLA", "MSFT", "GOOGL", "AMZN", "NVDA", "META"]
    result = {}
    for t in tickers:
        data = r.get(f"price:{t}")
        if data:
            result[t] = json.loads(data)
    return result

@router.websocket("/ws/prices")
async def websocket_prices(websocket: WebSocket):
    """
    WebSocket endpoint: pushes price updates to connected clients every second.
    Frontend subscribes to this for the live ticker.
    """
    await websocket.accept()
    tickers = ["AAPL", "TSLA", "MSFT", "GOOGL", "AMZN", "NVDA", "META"]
    try:
        while True:
            prices = {}
            for t in tickers:
                data = r.get(f"price:{t}")
                if data:
                    prices[t] = json.loads(data)
            await websocket.send_json(prices)
            await asyncio.sleep(1)
    except Exception:
        pass