import csv
import uuid
from datetime import datetime
from sqlmodel import Session, select
from .models import Transaction, TransactionType, Account, Asset
from typing import List
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger: logging.Logger = logging.getLogger(name=__name__)

def process_csv_import(reader: csv.DictReader, session: Session) -> None:
    """
    Import transactions from a CSV file. If a transaction with the same account_id, asset_id, type, quantity, price, fee, and date exists, update it.
    """
    created = 0
    updated = 0
    skipped = 0
    errors: List[str] = []
    
    batch_size = 100  # Process in chunks
    batch: List[int] = []
    
    for row_num, row in enumerate(iterable=reader, start=2):
        try:
            # Parse fields
            asset_id = uuid.UUID(row["asset_id"])
            account_id = uuid.UUID(row["account_id"])
            type_ = TransactionType(row["type"])
            quantity = float(row["quantity"])
            price = float(row["price"])
            fee = float(row.get("fee", 0))
            date = datetime.fromisoformat(row["date"])
            
            # Validate existence
            if not session.get(Account, account_id):
                errors.append(f"Row {row_num}: Account {account_id} not found.")
                skipped += 1
                continue
            if not session.get(Asset, asset_id):
                errors.append(f"Row {row_num}: Asset {asset_id} not found.")
                skipped += 1
                continue
            
            # Check for duplicate
            statement = select(Transaction).where(
                Transaction.account_id == account_id,
                Transaction.asset_id == asset_id,
                Transaction.type == type_,
                Transaction.quantity == quantity,
                Transaction.price == price,
                Transaction.fee == fee,
                Transaction.date == date,
            )
            existing = session.exec(statement).first()
            
            if existing:
                existing.price = price
                existing.quantity = quantity
                existing.fee = fee
                session.add(existing)
                updated += 1
            else:
                transaction = Transaction(
                    asset_id=asset_id,
                    account_id=account_id,
                    type=type_,
                    quantity=quantity,
                    price=price,
                    fee=fee,
                    date=date,
                )
                session.add(transaction)
                created += 1
            
            batch.append(row_num)
            if len(batch) >= batch_size:
                session.commit()
                logger.info(f"Committed batch of {len(batch)} rows.")
                batch = []
        
        except Exception as e:
            errors.append(f"Row {row_num}: {str(e)}")
            skipped += 1
            logger.error(f"Error on row {row_num}: {e}")
            # Removed session.rollback() to avoid undoing previous commits
    
    # Commit remaining batch
    if batch:
        session.commit()
        logger.info(f"Committed final batch of {len(batch)} rows.")
    
    # Log summary
    logger.info(f"Import complete: {created} created, {updated} updated, {skipped} skipped.")
    if errors:
        logger.warning(f"Errors: {errors}")
    
    # Optional: Send notification (e.g., email) here