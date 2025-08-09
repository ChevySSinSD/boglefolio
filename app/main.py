from datetime import datetime
from fastapi import FastAPI, Request, Form
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from sqlmodel import SQLModel, create_engine, Session, select
from .models import Account, Transaction, Snapshot
from .crud import create_transaction, get_transactions_for_account
import os

## Create Database Engine
# https://fastapi.tiangolo.com/tutorial/sql-databases/#create-an-engine
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./db.sqlite")
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})

## Define Database Table Creation Function (to be called on startup) 
# https://fastapi.tiangolo.com/tutorial/sql-databases/#create-the-tables
def create_db_and_tables():
    SQLModel.metadata.create_all(engine)

## Create FastAPI App and Create Database Tables on Startup
app = FastAPI(title="BogleFolio", on_startup=[create_db_and_tables])

templates = Jinja2Templates(directory="app/templates")
# app.mount("/static", StaticFiles(directory="app/static"), name="static")

@app.get("/", response_class=HTMLResponse)
def index(request: Request):
    with Session(engine) as session:
        account = session.exec(select(Account)).first()
        snapshots = session.exec(select(Snapshot).where(Snapshot.account_id == account.id).order_by(Snapshot.date)).all()
        transactions = get_transactions_for_account(session, account.id)
    return templates.TemplateResponse(
        "index.html",
        {
            "request": request,
            "account_id": account.id,
            "snapshots": snapshots,
            "transactions": transactions
        }
    )

@app.post("/accounts/{account_id}/transactions", response_class=HTMLResponse)
def add_transaction(request: Request, account_id: str, date: str = Form(...), ticker: str = Form(...),
                    quantity: float = Form(...), price: float = Form(...), fees: float = Form(0.0),
                    notes: str = Form(None)):
    # Convert date string to datetime.date
    date_obj = datetime.strptime(date, "%Y-%m-%d").date()
    tx = Transaction(account_id=account_id, date=date_obj, ticker=ticker.upper(),
                     quantity=quantity, price=price, fees=fees, type="buy", notes=notes)
    with Session(engine) as session:
        tx = create_transaction(session, tx)
        txs = get_transactions_for_account(session, account_id)
    return templates.TemplateResponse("partials/portfolio_table.html", {"request": request, "transactions": txs})

@app.get("/api/accounts/{account_id}/snapshots")
def snapshots_json(account_id: str):
    with Session(engine) as session:
        snaps = session.exec(
            select(Snapshot).where(Snapshot.account_id == account_id).order_by(Snapshot.date)
        ).all()
    return [{"date": s.date.isoformat(), "value": s.total_value} for s in snaps]
