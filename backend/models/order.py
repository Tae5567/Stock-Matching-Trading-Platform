from sqlalchemy import Column, Integer, String, Float, DateTime, Enum, ForeignKey, Boolean
from database import Base
from datetime import datetime
import enum

class OrderSide(str, enum.Enum):
    BUY = "buy"
    SELL = "sell"

class OrderType(str, enum.Enum):
    MARKET = "market"    # Fill immediately at best available price
    LIMIT = "limit"      # Only fill at this price or better

class OrderStatus(str, enum.Enum):
    OPEN = "open"
    PARTIALLY_FILLED = "partially_filled"
    FILLED = "filled"
    CANCELLED = "cancelled"
    ROUTED = "routed"     # Sent to external broker

class Order(Base):
    __tablename__ = "orders"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), index=True)
    ticker = Column(String(10), index=True)        # e.g. "AAPL", "TSLA"
    side = Column(Enum(OrderSide))                  # buy or sell
    order_type = Column(Enum(OrderType))
    quantity = Column(Integer)                      # number of shares
    filled_quantity = Column(Integer, default=0)
    limit_price = Column(Float, nullable=True)      # None for market orders
    avg_fill_price = Column(Float, nullable=True)   # average execution price
    status = Column(Enum(OrderStatus), default=OrderStatus.OPEN)
    is_urgent = Column(Boolean, default=False)      # priority queue flag
    routed_to = Column(String, nullable=True)       # which broker if externally routed
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)