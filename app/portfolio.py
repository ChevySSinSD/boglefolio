from __future__ import annotations
from dataclasses import dataclass, field
from typing import List, Dict
from .models import Transaction

@dataclass
class Lot:
    qty: float
    price: float  # cost per share
    fees: float = 0.0

@dataclass
class Position:
    ticker: str
    quantity: float = 0.0
    lots: List[Lot] = field(default_factory=list)
    realized_gain: float = 0.0
    basis: float = 0.0  # total cost basis of remaining shares
    market_value: float = 0.0
    unrealized_gain: float = 0.0
    avg_cost: float = 0.0

def _consume_fifo(lots: List[Lot], sell_qty: float, sell_price: float, sell_fees: float) -> float:
    realized = 0.0
    remaining = sell_qty
    while remaining > 1e-12 and lots:
        lot = lots[0]
        take = min(lot.qty, remaining)
        cost = take * lot.price
        proceeds = take * sell_price
        realized += proceeds - cost
        lot.qty -= take
        remaining -= take
        if lot.qty <= 1e-12:
            lots.pop(0)
    realized -= sell_fees
    return realized

def _consume_lifo(lots: List[Lot], sell_qty: float, sell_price: float, sell_fees: float) -> float:
    realized = 0.0
    remaining = sell_qty
    while remaining > 1e-12 and lots:
        lot = lots[-1]
        take = min(lot.qty, remaining)
        cost = take * lot.price
        proceeds = take * sell_price
        realized += proceeds - cost
        lot.qty -= take
        remaining -= take
        if lot.qty <= 1e-12:
            lots.pop()
    realized -= sell_fees
    return realized

def compute_positions(transactions: List[Transaction], prices: Dict[str, float] | None = None, method: str = "FIFO") -> Dict[str, Position]:
    positions: Dict[str, Position] = {}
    prices = prices or {}
    by_ticker: Dict[str, List[Transaction]] = {}
    for tx in transactions:
        by_ticker.setdefault(tx.ticker, []).append(tx)
    for ticker, txs in by_ticker.items():
        txs.sort(key=lambda t: (t.date, t.id))
        pos = Position(ticker=ticker)
        lots: List[Lot] = []
        for tx in txs:
            if tx.type.lower() == "buy":
                lots.append(Lot(qty=tx.quantity, price=tx.price, fees=tx.fees))
            elif tx.type.lower() == "sell":
                if method.upper() == "FIFO":
                    pos.realized_gain += _consume_fifo(lots, tx.quantity, tx.price, tx.fees)
                else:
                    pos.realized_gain += _consume_lifo(lots, tx.quantity, tx.price, tx.fees)
            elif tx.type.lower() == "dividend":
                pos.realized_gain += tx.quantity * tx.price
        pos.quantity = sum(l.qty for l in lots)
        pos.basis = sum(l.qty * l.price for l in lots)
        price = prices.get(ticker, None)
        if price is not None:
            pos.market_value = pos.quantity * price
            pos.unrealized_gain = pos.market_value - pos.basis
        pos.avg_cost = (pos.basis / pos.quantity) if pos.quantity else 0.0
        pos.lots = lots
        positions[ticker] = pos
    return positions
