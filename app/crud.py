from sqlmodel import Session, select
from .models import Transaction, Snapshot, Account, User

def create_transaction(session: Session, tx: Transaction):
    session.add(tx)
    session.commit()
    session.refresh(tx)
    return tx

def get_transactions_for_account(session: Session, account_id: str):
    return session.exec(
        select(Transaction).where(Transaction.account_id == account_id).order_by(Transaction.date)
    ).all()

def create_snapshot(session: Session, snapshot: Snapshot):
    session.add(snapshot)
    session.commit()
    session.refresh(snapshot)
    return snapshot
