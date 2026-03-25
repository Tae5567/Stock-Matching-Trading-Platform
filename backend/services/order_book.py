"""
The order book keeps all open buy and sell orders for a ticker, sorted so matching is instant.
"""

from sortedcontainers import SortedList
from dataclasses import dataclass, field
from datetime import datetime
from typing import List, Optional
import redis
import json
import os

r = redis.from_url(os.getenv("REDIS_URL"))

@dataclass(order=True)
class BookEntry:
    """
    A single entry in the order book
    
    Sort key for BIDS (buys):  (-price, timestamp) → highest price first, then oldest first
    Sort key for ASKS (sells): (+price, timestamp) → lowest price first, then oldest first
    
    This implements Price-Time Priority (standard exchange behavior)
    """
    sort_key: tuple = field(compare=True)
    order_id: int = field(compare=False)
    price: float = field(compare=False)
    quantity: int = field(compare=False)
    user_id: int = field(compare=False)
    timestamp: datetime = field(compare=False)

class OrderBook:
    """
    In-memory order book for a single ticker
    Bids and asks are stored in Redis for persistence + speed
    """
    def __init__(self, ticker: str):
        self.ticker = ticker
        self.bids: SortedList = SortedList(key=lambda e: e.sort_key)  # buy orders
        self.asks: SortedList = SortedList(key=lambda e: e.sort_key)  # sell orders

    def add_order(self, order_id: int, side: str, price: float,
                  quantity: int, user_id: int) -> None:
        ts = datetime.utcnow()
        if side == "buy":
            entry = BookEntry(
                sort_key=(-price, ts.timestamp()),   # highest bid first
                order_id=order_id, price=price,
                quantity=quantity, user_id=user_id, timestamp=ts
            )
            self.bids.add(entry)
        else:
            entry = BookEntry(
                sort_key=(price, ts.timestamp()),    # lowest ask first
                order_id=order_id, price=price,
                quantity=quantity, user_id=user_id, timestamp=ts
            )
            self.asks.add(entry)
        self._persist()

    # Highest buy price
    def best_bid(self) -> Optional[BookEntry]:
        return self.bids[0] if self.bids else None

    # Lowest sell price
    def best_ask(self) -> Optional[BookEntry]:
        return self.asks[0] if self.asks else None

    # Difference between best ask and best bid
    def spread(self) -> Optional[float]:
        if self.best_bid() and self.best_ask():
            return round(self.best_ask().price - self.best_bid().price, 4)
        return None

    # Top N levels of the order book for display
    def depth_snapshot(self, levels: int = 10) -> dict:
        return {
            "bids": [{"price": e.price, "qty": e.quantity} for e in list(self.bids)[:levels]],
            "asks": [{"price": e.price, "qty": e.quantity} for e in list(self.asks)[:levels]],
            "spread": self.spread()
        }

    # Snapshot order to book Redis for other processes to read
    def _persist(self):
        snapshot = self.depth_snapshot()
        r.setex(f"orderbook:{self.ticker}", 300, json.dumps(snapshot))

    @classmethod
    # Restore from Redis (on startup / new worker)
    def load(cls, ticker: str) -> "OrderBook":
        book = cls(ticker)
        # In production: rebuild from open orders in Postgres
        return book

# Global registry of live order books
_books: dict = {}

def get_book(ticker: str) -> OrderBook:
    if ticker not in _books:
        _books[ticker] = OrderBook.load(ticker)
    return _books[ticker]
    