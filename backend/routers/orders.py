from fastapi import APIRouter, Depends, BackgroundTasks
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional
from database import get_db
from models.order import Order, OrderSide, OrderType
from tasks.celery_tasks import process_order_async

router = APIRouter(prefix="/api/orders", tags=["orders"])

class OrderRequest(BaseModel):
    ticker: str
    side: str           # "buy" or "sell"
    order_type: str     # "market" or "limit"
    quantity: int
    limit_price: Optional[float] = None
    user_id: int
    is_urgent: bool = False

@router.post("/")
def submit_order(req: OrderRequest, db: Session = Depends(get_db)):
    """
    Submit a new buy or sell order
    Order is saved immediately, then matching runs asynchronously via Celery.
    """
    order = Order(
        user_id=req.user_id,
        ticker=req.ticker.upper(),
        side=req.side,
        order_type=req.order_type,
        quantity=req.quantity,
        limit_price=req.limit_price,
        is_urgent=req.is_urgent
    )
    db.add(order)
    db.commit()
    db.refresh(order)

    # Kick off async matching. don't block the API response
    process_order_async.apply_async(args=[order.id], queue="orders")

    return {"order_id": order.id, "status": order.status, "message": "Order submitted"}

@router.get("/{order_id}")
def get_order(order_id: int, db: Session = Depends(get_db)):
    return db.query(Order).filter(Order.id == order_id).first()

@router.get("/user/{user_id}")
def get_user_orders(user_id: int, db: Session = Depends(get_db)):
    return db.query(Order).filter(
        Order.user_id == user_id
    ).order_by(Order.created_at.desc()).limit(50).all()

@router.delete("/{order_id}")
def cancel_order(order_id: int, db: Session = Depends(get_db)):
    from models.order import OrderStatus
    order = db.query(Order).filter(Order.id == order_id).first()
    if order and order.status == OrderStatus.OPEN:
        order.status = OrderStatus.CANCELLED
        db.commit()
    return {"status": "cancelled"}