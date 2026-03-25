from celery import Celery #type: ignore
from celery.schedules import crontab #type: ignore
import os

celery_app = Celery(
    "stock_platform",
    broker=os.getenv("CELERY_BROKER_URL"),
    backend=os.getenv("CELERY_RESULT_BACKEND")
)

celery_app.conf.task_queues = {
    "orders": {},        # High priority — order matching
    "settlements": {},   # End-of-day settlement
}

celery_app.conf.beat_schedule = {
    # Refresh mock market data every 5 seconds
    "refresh-market-data": {
        "task": "tasks.celery_tasks.refresh_market_prices",
        "schedule": 5.0,
    },
    # End-of-day settlement at 4:00 PM EST
    "eod-settlement": {
        "task": "tasks.celery_tasks.run_eod_settlement",
        "schedule": crontab(hour=21, minute=0),  # 21:00 UTC = 4 PM EST
    }
}

@celery_app.task(queue="orders")
def process_order_async(order_id: int):
    """
    Run matching engine for a new order asynchronously.
    Called immediately when order arrives; doesn't block the HTTP response.
    """
    from database import SessionLocal
    from models.order import Order
    from services.matching_engine import match_order

    db = SessionLocal()
    order = db.query(Order).filter(Order.id == order_id).first()
    if order:
        trades = match_order(order, db)
        return {"order_id": order_id, "trades_executed": len(trades)}
    db.close()

@celery_app.task(queue="settlements")
def run_eod_settlement():
    """
    End-of-day: cancel all unfilled day orders, compute daily P&L summary.
    """
    from database import SessionLocal
    from models.order import Order, OrderStatus
    from datetime import date

    db = SessionLocal()
    today_open = db.query(Order).filter(
        Order.status == OrderStatus.OPEN,
        Order.created_at >= date.today()
    ).all()
    for o in today_open:
        o.status = OrderStatus.CANCELLED
    db.commit()
    db.close()
    return {"cancelled_orders": len(today_open)}

@celery_app.task
def refresh_market_prices():
    """
    In production: pull from market data provider (Polygon.io, Alpaca).
    Here: generate mock OHLCV data and cache in Redis.
    """
    import redis
    import json
    import random

    r = redis.from_url(os.getenv("REDIS_URL"))
    tickers = ["AAPL", "TSLA", "MSFT", "GOOGL", "AMZN", "NVDA", "META"]
    base_prices = {"AAPL": 185, "TSLA": 245, "MSFT": 415,
                   "GOOGL": 175, "AMZN": 195, "NVDA": 875, "META": 520}

    for ticker in tickers:
        base = base_prices[ticker]
        price = round(base * (1 + random.uniform(-0.002, 0.002)), 2)
        r.setex(f"price:{ticker}", 10, json.dumps({
            "ticker": ticker,
            "price": price,
            "change": round(random.uniform(-5, 5), 2),
            "change_pct": round(random.uniform(-2, 2), 4),
            "volume": random.randint(1_000_000, 50_000_000)
        }))