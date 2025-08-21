from fastapi import APIRouter, HTTPException, status, Depends
from sqlmodel import Session, select
from app.models import Transaction
from app.database import get_session
from app.schemas import TransactionCreate, TransactionRead
from typing import Any, List, Sequence
import uuid
from datetime import datetime

router = APIRouter(prefix="/transactions", tags=["transactions"])

@router.post(path="/", response_model=TransactionRead, status_code=status.HTTP_201_CREATED)
def create_transaction(transaction: TransactionCreate, session: Session = Depends(dependency=get_session)) -> TransactionRead:
    data: dict[str, Any] = transaction.model_dump()
    if data.get("date") is None:
        data["date"] = datetime.now()
    db_transaction: Transaction = Transaction.model_validate(obj=data)
    session.add(instance=db_transaction)
    session.commit()
    session.refresh(instance=db_transaction)
    return TransactionRead.model_validate(obj=db_transaction)

@router.get(path="/", response_model=List[TransactionRead])
def read_transactions(session: Session = Depends(dependency=get_session)) -> Sequence[TransactionRead]:
    transactions: Sequence[Transaction] = session.exec(statement=select(Transaction)).all()
    return [TransactionRead.model_validate(obj=transaction) for transaction in transactions]

@router.get(path="/{transaction_id}", response_model=TransactionRead)
def read_transaction(transaction_id: uuid.UUID, session: Session = Depends(dependency=get_session)) -> TransactionRead:
    transaction: Transaction | None = session.get(entity=Transaction, ident=transaction_id)
    if not transaction:
        raise HTTPException(status_code=404, detail="Transaction not found")
    return TransactionRead.model_validate(obj=transaction)

@router.delete(path="/{transaction_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_transaction(transaction_id: uuid.UUID, session: Session = Depends(dependency=get_session)) -> None:
    transaction: Transaction | None = session.get(entity=Transaction, ident=transaction_id)
    if not transaction:
        raise HTTPException(status_code=404, detail="Transaction not found")
    session.delete(instance=transaction)
    session.commit()