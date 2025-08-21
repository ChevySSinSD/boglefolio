from fastapi import APIRouter, HTTPException, status, Depends
from sqlmodel import Session, select
from app.models import Account
from app.database import get_session
from app.schemas import AccountCreate, AccountRead
from typing import List, Sequence
import uuid

router = APIRouter(prefix="/accounts", tags=["accounts"])

@router.post(path="/", response_model=AccountRead, status_code=status.HTTP_201_CREATED)
def create_account(account: AccountCreate, session: Session = Depends(dependency=get_session)) -> AccountRead:
    db_account: Account = Account.model_validate(obj=account)
    session.add(instance=db_account)
    session.commit()
    session.refresh(instance=db_account)
    return AccountRead.model_validate(obj=db_account)

@router.get(path="/", response_model=List[AccountRead])
def read_accounts(session: Session = Depends(dependency=get_session)) -> Sequence[AccountRead]:
    accounts: Sequence[Account] = session.exec(statement=select(Account)).all()
    return [AccountRead.model_validate(obj=account) for account in accounts]

@router.get(path="/{account_id}", response_model=AccountRead)
def read_account(account_id: uuid.UUID, session: Session = Depends(dependency=get_session)) -> AccountRead:
    account: Account | None = session.get(entity=Account, ident=account_id)
    if not account:
        raise HTTPException(status_code=404, detail="Account not found")
    return AccountRead.model_validate(obj=account)

@router.delete(path="/{account_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_account(account_id: uuid.UUID, session: Session = Depends(dependency=get_session)) -> None:
    account: Account | None = session.get(entity=Account, ident=account_id)
    if not account:
        raise HTTPException(status_code=404, detail="Account not found")
    session.delete(instance=account)
    session.commit()