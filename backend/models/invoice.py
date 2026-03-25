from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Boolean
from database import Base
from datetime import datetime

class Invoice(Base):
    __tablename__ = "invoices"

    id = Column(Integer, primary_key=True)
    trade_id = Column(Integer, ForeignKey("trades.id"))
    user_id = Column(Integer, ForeignKey("users.id"))
    invoice_number = Column(String, unique=True)
    trade_value = Column(Float)
    commission = Column(Float)      # platform brokerage fee
    sec_fee = Column(Float)         # regulatory fee (sell orders only)
    tax_amount = Column(Float)      # capital gains tax if applicable
    total_charge = Column(Float)
    is_paid = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)