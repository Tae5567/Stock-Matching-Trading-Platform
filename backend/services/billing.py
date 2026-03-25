import os
import uuid
from datetime import datetime
from sqlalchemy.orm import Session
from models.invoice import Invoice
from models.trade import Trade

COMMISSION_RATE = float(os.getenv("COMMISSION_PER_TRADE", 0.005))
SEC_FEE_RATE = float(os.getenv("SEC_FEE_RATE", 0.0000278))
CGT_RATE = float(os.getenv("CAPITAL_GAINS_TAX_RATE", 0.15))

def generate_invoice_number() -> str:
    return f"TRD-{datetime.utcnow().strftime('%Y%m%d')}-{uuid.uuid4().hex[:6].upper()}"

def bill_trade(trade: Trade, user_id: int, side: str,cost_basis: float, db: Session) -> Invoice:
    """
    Generate invoice for one side of a trade.
    
    Charges:
    - Commission: 0.5% of trade value (both sides pay)
    - SEC Fee: 0.00278% of trade value (sell side only — US regulation)
    - Capital Gains Tax: 15% of profit (sell side, if profit > 0)
    """
    commission = round(trade.trade_value * COMMISSION_RATE, 2)
    sec_fee = round(trade.trade_value * SEC_FEE_RATE, 2) if side == "sell" else 0.0

    # CGT only on sell side where there's a gain
    gain = trade.trade_value - (cost_basis * trade.quantity) if side == "sell" else 0
    tax = round(gain * CGT_RATE, 2) if gain > 0 else 0.0

    total = round(commission + sec_fee + tax, 2)

    invoice = Invoice(
        trade_id=trade.id,
        user_id=user_id,
        invoice_number=generate_invoice_number(),
        trade_value=trade.trade_value,
        commission=commission,
        sec_fee=sec_fee,
        tax_amount=tax,
        total_charge=total
    )
    db.add(invoice)
    db.commit()
    db.refresh(invoice)
    return invoice