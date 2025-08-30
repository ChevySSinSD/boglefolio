import csv
import uuid
from datetime import datetime
from sqlmodel import Session, select
from .models import Transaction, TransactionType, Account, Asset
from fastapi import HTTPException

def import_transactions_from_csv(csv_path: str, session: Session) -> dict[str, int | list[str]]:
    """
    Import transactions from a CSV file. If a transaction with the same account_id, asset_id, type, quantity, price, fee, and date exists, update it.
    """
    updated = 0
    created = 0
    skipped = 0
    errors: list[str] = []

    with open(csv_path, newline="") as csvfile:
        reader: csv.DictReader[str] = csv.DictReader(csvfile)
        for row_num, row in enumerate(reader, start=2):  # start=2 for header row
            try:
                # Parse fields from CSV
                asset_id = uuid.UUID(row["asset_id"])
                account_id = uuid.UUID(row["account_id"])
                type_ = TransactionType(row["type"])
                quantity = float(row["quantity"])
                price = float(row["price"])
                fee = float(row.get("fee", 0))
                date: datetime = datetime.fromisoformat(row["date"])
            except (ValueError, KeyError) as e:
                msg = f"Row {row_num}: Parse error: {e} | Row: {row}"
                print(msg)
                errors.append(msg)
                skipped += 1
                continue

            # Check that asset and account exist
            if not session.get(Account, account_id):
                msg = f"Row {row_num}: account_id {account_id} does not exist."
                print(msg)
                errors.append(msg)
                skipped += 1
                continue
            if not session.get(Asset, asset_id):
                msg = f"Row {row_num}: asset_id {asset_id} does not exist."
                print(msg)
                errors.append(msg)
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
                # Update existing transaction (customize fields as needed)
                existing.price = price
                existing.quantity = quantity
                existing.fee = fee
                session.add(instance=existing)
                updated += 1
            else:
                # Create new transaction
                transaction = Transaction(
                    asset_id=asset_id,
                    account_id=account_id,
                    type=type_,
                    quantity=quantity,
                    price=price,
                    fee=fee,
                    date=date,
                )
                session.add(instance=transaction)
                created += 1

        session.commit()
    result = {
        "created": created,
        "updated": updated,
        "skipped": skipped,
        "errors": errors
    }
    if result["created"] == 0 and result["updated"] == 0:
        raise HTTPException(
            status_code=400,
            detail={"message": "No transactions imported.", "errors": result["errors"]}
        )
    return result  # HTTP 200 if at least one success