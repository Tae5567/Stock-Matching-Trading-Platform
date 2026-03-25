from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, UniqueConstraint
from database import Base
from datetime import datetime

class Position(Base):
    """Tracks each user's current stock holdings and cost basis."""
    __tablename__ = "positions"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    ticker = Column(String(10))
    quantity = Column(Integer, default=0)
    avg_cost = Column(Float, default=0.0)       # average purchase price
    realized_pnl = Column(Float, default=0.0)   # profit/loss from closed positions
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    __table_args__ = (
        UniqueConstraint("user_id", "ticker", name="uq_user_ticker"),
    )