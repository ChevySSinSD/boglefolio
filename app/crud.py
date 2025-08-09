
from sqlmodel import Session, select

from .models import Snapshot, TickerPrice, Transaction


def create_transaction(session: Session, tx: Transaction) -> Transaction:
    session.add(tx)
    session.commit()
    session.refresh(tx)
    return tx

def get_transactions_for_account(session: Session, account_id: str) -> list[Transaction]:
    return session.exec(
        select(Transaction).where(Transaction.account_id == account_id).order_by(Transaction.date, Transaction.id)
    ).all()

def create_snapshot(session: Session, snapshot: Snapshot) -> Snapshot:
    session.add(snapshot)
    session.commit()
    session.refresh(snapshot)
    return snapshot

def upsert_price(session: Session, ticker: str, as_of, price: float) -> TickerPrice:
    row = session.exec(select(TickerPrice).where(TickerPrice.ticker==ticker, TickerPrice.as_of==as_of)).first()
    if row:
        row.price = price
    else:
        row = TickerPrice(ticker=ticker, as_of=as_of, price=price)
        session.add(row)
    session.commit()
    session.refresh(row)
    return row

def latest_prices(session: Session) -> dict:
    tickers = session.exec(select(TickerPrice.ticker).distinct()).all()
    out = {}
    for t in tickers:
        r = session.exec(
            select(TickerPrice).where(TickerPrice.ticker==t).order_by(TickerPrice.as_of.desc())
        ).first()
        if r:
            out[t] = r.price
    return out
