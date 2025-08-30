from fastapi import APIRouter, HTTPException, status, Depends, UploadFile, File, BackgroundTasks
from sqlmodel import Session, select
from ..models import Transaction
from ..database import get_session
from ..schemas import TransactionCreate, TransactionRead, TransactionUpdate
from ..import_transactions import process_csv_import
from typing import Any, List, Sequence
import uuid
from datetime import datetime
import io
import csv

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
def read_transactions(
    session: Session = Depends(dependency=get_session),
    offset: int = 0,
    limit: int = 100
) -> Sequence[TransactionRead]:
    transactions: Sequence[Transaction] = session.exec(
        statement=select(Transaction).offset(offset=offset).limit(limit=limit)
    ).all()
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

@router.patch(path="/{transaction_id}", response_model=TransactionRead)
def update_transaction(transaction_id: uuid.UUID, transaction_update: TransactionUpdate, session: Session = Depends(get_session)) -> TransactionRead:
    transaction: Transaction | None = session.get(entity=Transaction, ident=transaction_id)
    if not transaction:
        raise HTTPException(status_code=404, detail="Transaction not found")
    transaction_data: dict[str, Any] = transaction_update.model_dump(exclude_unset=True)
    for key, value in transaction_data.items():
        setattr(transaction, key, value)
    session.add(instance=transaction)
    session.commit()
    session.refresh(instance=transaction)
    return TransactionRead.model_validate(obj=transaction)


@router.post(
    "/import-csv",
    status_code=status.HTTP_202_ACCEPTED,
    summary="Import transactions from CSV (async)",
    description=(
        "Upload a CSV file to import transactions asynchronously. Processing happens in the background."
        "The CSV must have the following columns: "
        "`asset_id`, `account_id`, `type`, `quantity`, `price`, `fee`, `date`.\n\n"
        "- `asset_id` and `account_id` must be valid UUIDs of existing assets/accounts.\n"
        "- `type` must match a valid TransactionType (e.g., BUY, SELL).\n"
        "- `quantity`, `price`, and `fee` must be numbers.\n"
        "- `date` must be in ISO format (e.g., 2024-08-22T14:00:00).\n"
        "Duplicate transactions (matching all fields) will be updated instead of inserted."
    ),
)
async def import_transactions_csv(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    session: Session = Depends(get_session)
):
    if not file.filename or not file.filename.endswith(".csv"):
        raise HTTPException(status_code=400, detail="Only CSV files are supported.")
    
    contents = await file.read()  # Async read
    csv_data = io.StringIO(contents.decode("utf-8"))
    reader = csv.DictReader(csv_data)
    
    # Add to background task
    background_tasks.add_task(process_csv_import, reader, session)
    
    return {"message": "CSV import started. Check logs for results."}