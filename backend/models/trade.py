from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey
from database import Base
from datetime import datetime

class Trade(Base):
    """
    A Trade is created every time two orders match.
    One buy order + one sell order = one Trade record.
    """
    __tablename__ = "trades"

    id = Column(Integer, primary_key=True, index=True)
    ticker = Column(String(10), index=True)
    buy_order_id = Column(Integer, ForeignKey("orders.id"))
    sell_order_id = Column(Integer, ForeignKey("orders.id"))
    buyer_id = Column(Integer, ForeignKey("users.id"))
    seller_id = Column(Integer, ForeignKey("users.id"))
    quantity = Column(Integer)          # shares exchanged
    price = Column(Float)               # execution price
    trade_value = Column(Float)         # quantity × price
    executed_at = Column(DateTime, default=datetime.utcnow, index=True)