from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func
from database import get_db
from models.trade import Trade
from models.order import Order, OrderStatus
from models.invoice import Invoice

router = APIRouter(prefix="/api/admin", tags=["admin"])

@router.get("/metrics")
def get_metrics(db: Session = Depends(get_db)):
    total_trades = db.query(func.count(Trade.id)).scalar()
    total_volume = db.query(func.sum(Trade.trade_value)).scalar() or 0
    total_commission = db.query(func.sum(Invoice.commission)).scalar() or 0
    open_orders = db.query(func.count(Order.id)).filter(
        Order.status == OrderStatus.OPEN
    ).scalar()
    trades_today = db.query(func.count(Trade.id)).filter(
        func.date(Trade.executed_at) == func.current_date()
    ).scalar()

    return {
        "total_trades": total_trades,
        "trades_today": trades_today,
        "total_volume_usd": round(total_volume, 2),
        "platform_commission_usd": round(total_commission, 2),
        "open_orders": open_orders,
    }

@router.get("/trades/recent")
def recent_trades(limit: int = 100, db: Session = Depends(get_db)):
    return db.query(Trade).order_by(Trade.executed_at.desc()).limit(limit).all()

@router.get("/trades/by-ticker/{ticker}")
def trades_by_ticker(ticker: str, db: Session = Depends(get_db)):
    return db.query(Trade).filter(
        Trade.ticker == ticker.upper()
    ).order_by(Trade.executed_at.desc()).limit(50).all()