from fastapi import APIRouter, Request, Depends, Form, HTTPException
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
from sqlmodel import Session, select
from typing import Optional
from datetime import datetime
import uuid

from ..database import get_session
from ..models import User, Asset, Account, Transaction
from ..schemas import UserCreate, AssetCreate, AccountCreate, TransactionCreate, TransactionType

router = APIRouter(tags=["frontend"])
templates = Jinja2Templates(directory="frontend/templates")

@router.get("/", response_class=HTMLResponse)
async def dashboard(request: Request, session: Session = Depends(get_session)):
    """Dashboard homepage showing overview stats."""
    # Get counts for stats
    users_count = len(session.exec(select(User)).all())
    assets_count = len(session.exec(select(Asset)).all())
    accounts_count = len(session.exec(select(Account)).all())
    transactions_count = len(session.exec(select(Transaction)).all())
    
    # Get recent transactions
    recent_transactions = session.exec(
        select(Transaction).order_by(Transaction.date.desc()).limit(5)
    ).all()
    
    context = {
        "request": request,
        "users_count": users_count,
        "assets_count": assets_count,
        "accounts_count": accounts_count,
        "transactions_count": transactions_count,
        "recent_transactions": recent_transactions,
    }
    return templates.TemplateResponse("dashboard.html", context)

@router.get("/users", response_class=HTMLResponse)
async def users_list(request: Request, session: Session = Depends(get_session)):
    """Users management page."""
    users = session.exec(select(User)).all()
    context = {"request": request, "users": users}
    return templates.TemplateResponse("users/list.html", context)

@router.post("/users", response_class=HTMLResponse)
async def create_user(
    request: Request,
    username: str = Form(...),
    email: Optional[str] = Form(None),
    session: Session = Depends(get_session)
):
    """Create a new user via form submission."""
    try:
        user_data = UserCreate(username=username, email=email)
        db_user = User.model_validate(user_data)
        session.add(db_user)
        session.commit()
        session.refresh(db_user)
        
        # Return updated users list
        users = session.exec(select(User)).all()
        context = {"request": request, "users": users}
        return templates.TemplateResponse("users/list.html", context)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/assets", response_class=HTMLResponse)
async def assets_list(request: Request, session: Session = Depends(get_session)):
    """Assets management page."""
    assets = session.exec(select(Asset)).all()
    context = {"request": request, "assets": assets}
    return templates.TemplateResponse("assets/list.html", context)

@router.post("/assets", response_class=HTMLResponse)
async def create_asset(
    request: Request,
    symbol: str = Form(...),
    name: Optional[str] = Form(None),
    currency: str = Form("USD"),
    session: Session = Depends(get_session)
):
    """Create a new asset via form submission."""
    try:
        # Check for duplicate symbol
        existing_asset = session.exec(select(Asset).where(Asset.symbol == symbol)).first()
        if existing_asset:
            raise HTTPException(status_code=409, detail="Asset with this symbol already exists")
            
        asset_data = AssetCreate(symbol=symbol, name=name, currency=currency)
        db_asset = Asset.model_validate(asset_data)
        session.add(db_asset)
        session.commit()
        session.refresh(db_asset)
        
        # Return updated assets list
        assets = session.exec(select(Asset)).all()
        context = {"request": request, "assets": assets}
        return templates.TemplateResponse("assets/list.html", context)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/accounts", response_class=HTMLResponse)
async def accounts_list(request: Request, session: Session = Depends(get_session)):
    """Accounts management page."""
    accounts = session.exec(select(Account)).all()
    users = session.exec(select(User)).all()
    context = {"request": request, "accounts": accounts, "users": users}
    return templates.TemplateResponse("accounts/list.html", context)

@router.post("/accounts", response_class=HTMLResponse)
async def create_account(
    request: Request,
    name: Optional[str] = Form(None),
    user_id: str = Form(...),
    balance: float = Form(0.0),
    session: Session = Depends(get_session)
):
    """Create a new account via form submission."""
    try:
        account_data = AccountCreate(
            name=name, 
            user_id=uuid.UUID(user_id), 
            balance=balance
        )
        db_account = Account.model_validate(account_data)
        session.add(db_account)
        session.commit()
        session.refresh(db_account)
        
        # Return updated accounts list
        accounts = session.exec(select(Account)).all()
        users = session.exec(select(User)).all()
        context = {"request": request, "accounts": accounts, "users": users}
        return templates.TemplateResponse("accounts/list.html", context)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/transactions", response_class=HTMLResponse)
async def transactions_list(request: Request, session: Session = Depends(get_session)):
    """Transactions management page."""
    transactions = session.exec(select(Transaction).order_by(Transaction.date.desc())).all()
    assets = session.exec(select(Asset)).all()
    accounts = session.exec(select(Account)).all()
    context = {"request": request, "transactions": transactions, "assets": assets, "accounts": accounts}
    return templates.TemplateResponse("transactions/list.html", context)

@router.post("/transactions", response_class=HTMLResponse)
async def create_transaction(
    request: Request,
    asset_id: str = Form(...),
    account_id: str = Form(...),
    type: str = Form(...),
    quantity: float = Form(...),
    price: float = Form(...),
    fee: float = Form(0.0),
    date: Optional[str] = Form(None),
    session: Session = Depends(get_session)
):
    """Create a new transaction via form submission."""
    try:
        # Parse date if provided
        transaction_date = None
        if date:
            transaction_date = datetime.fromisoformat(date.replace('T', ' '))
        
        transaction_data = TransactionCreate(
            asset_id=uuid.UUID(asset_id),
            account_id=uuid.UUID(account_id),
            type=TransactionType(type),
            quantity=quantity,
            price=price,
            fee=fee,
            date=transaction_date
        )
        
        # Create transaction (similar to existing API logic)
        data = transaction_data.model_dump()
        if data.get("date") is None:
            data["date"] = datetime.now()
        
        db_transaction = Transaction.model_validate(data)
        session.add(db_transaction)
        session.commit()
        session.refresh(db_transaction)
        
        # Return updated transactions list
        transactions = session.exec(select(Transaction).order_by(Transaction.date.desc())).all()
        assets = session.exec(select(Asset)).all()
        accounts = session.exec(select(Account)).all()
        context = {"request": request, "transactions": transactions, "assets": assets, "accounts": accounts}
        return templates.TemplateResponse("transactions/list.html", context)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))