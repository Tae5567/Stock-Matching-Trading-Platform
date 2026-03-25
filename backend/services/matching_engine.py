from typing import List, Tuple, Optional
from dataclasses import dataclass
from services.order_book import get_book, BookEntry
from models.order import Order, OrderSide, OrderType, OrderStatus
from models.trade import Trade
from sqlalchemy.orm import Session
from datetime import datetime

@dataclass
class MatchResult:
    trade_quantity: int
    execution_price: float
    buy_order_id: int
    sell_order_id: int
    buyer_id: int
    seller_id: int

def match_order(new_order: Order, db: Session) -> List[MatchResult]:
    """
    Core matching function. Called whenever a new order arrives.
    
    How it works:
    1. Get the live order book for this ticker
    2. If new order is a BUY:  check if best ASK price ≤ our limit price
    3. If new order is a SELL: check if best BID price ≥ our limit price
    4. If crossable: execute trade, reduce quantities, repeat until filled or no match
    5. Any remaining unfilled quantity goes into the book
    
    This is Price-Time Priority matching (same as NYSE/NASDAQ).
    """
    book = get_book(new_order.ticker)
    trades = []
    remaining_qty = new_order.quantity - new_order.filled_quantity

    while remaining_qty > 0:
        if new_order.side == OrderSide.BUY:
            opposite = book.best_ask()
            if not opposite:
                break  # No sellers available
            can_execute = (
                new_order.order_type == OrderType.MARKET or
                new_order.limit_price >= opposite.price
            )
        else:  # SELL
            opposite = book.best_bid()
            if not opposite:
                break  # No buyers available
            can_execute = (
                new_order.order_type == OrderType.MARKET or
                new_order.limit_price <= opposite.price
            )

        if not can_execute:
            break  # Price doesn't cross — add to book and wait

        # Determine fill quantity (partial fills allowed)
        fill_qty = min(remaining_qty, opposite.quantity)
        exec_price = opposite.price  # Price of the resting order (standard rule)

        # Record the match
        trade_value = fill_qty * exec_price
        if new_order.side == OrderSide.BUY:
            result = MatchResult(
                trade_quantity=fill_qty,
                execution_price=exec_price,
                buy_order_id=new_order.id,
                sell_order_id=opposite.order_id,
                buyer_id=new_order.user_id,
                seller_id=opposite.user_id
            )
        else:
            result = MatchResult(
                trade_quantity=fill_qty,
                execution_price=exec_price,
                buy_order_id=opposite.order_id,
                sell_order_id=new_order.id,
                buyer_id=opposite.user_id,
                seller_id=new_order.user_id
            )
        trades.append(result)

        # Update quantities
        remaining_qty -= fill_qty
        opposite.quantity -= fill_qty

        # Remove fully-filled resting order from book
        if opposite.quantity == 0:
            if new_order.side == OrderSide.BUY:
                book.asks.remove(opposite)
            else:
                book.bids.remove(opposite)

        # Persist trades to DB
        _record_trade(result, new_order.ticker, db)

    # Update the incoming order's fill status
    filled = new_order.quantity - remaining_qty
    new_order.filled_quantity = filled
    new_order.avg_fill_price = trades[0].execution_price if trades else None

    if filled == 0:
        new_order.status = OrderStatus.OPEN
        # Add unfilled order to book
        book.add_order(new_order.id, new_order.side.value,
                       new_order.limit_price or 0, remaining_qty, new_order.user_id)
    elif filled < new_order.quantity:
        new_order.status = OrderStatus.PARTIALLY_FILLED
        book.add_order(new_order.id, new_order.side.value,
                       new_order.limit_price or 0, remaining_qty, new_order.user_id)
    else:
        new_order.status = OrderStatus.FILLED

    db.commit()
    return trades


def _record_trade(result: MatchResult, ticker: str, db: Session):
    trade = Trade(
        ticker=ticker,
        buy_order_id=result.buy_order_id,
        sell_order_id=result.sell_order_id,
        buyer_id=result.buyer_id,
        seller_id=result.seller_id,
        quantity=result.trade_quantity,
        price=result.execution_price,
        trade_value=result.trade_quantity * result.execution_price,
        executed_at=datetime.utcnow()
    )
    db.add(trade)
    db.flush()   # get trade.id without full commit
    return trade