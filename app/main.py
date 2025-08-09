from datetime import datetime
from fastapi import FastAPI, Request, Form, UploadFile, File
from fastapi.responses import HTMLResponse, StreamingResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from sqlmodel import SQLModel, create_engine, Session, select
from .models import Account, Transaction, Snapshot
from .crud import create_transaction, get_transactions_for_account, latest_prices
from .portfolio import compute_positions
import os, csv, io

## Create Database Engine
# https://fastapi.tiangolo.com/tutorial/sql-databases/#create-an-engine
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./db.sqlite")
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})

## Define Database Table Creation Function (to be called on startup) 
# https://fastapi.tiangolo.com/tutorial/sql-databases/#create-the-tables
def create_db_and_tables():
    SQLModel.metadata.create_all(engine)
    with Session(engine) as session:
        acc = session.exec(select(Account)).first()
        if not acc:
            from .seed import seed
            seed()

## Create FastAPI App and Create Database Tables on Startup
app = FastAPI(title="BogleFolio", on_startup=[create_db_and_tables])

templates = Jinja2Templates(directory="app/templates")
# app.mount("/static", StaticFiles(directory="app/static"), name="static")

def fmt_currency(v: float, symbol: str = "$"):
    try:
        return f"{symbol}{v:,.2f}"
    except Exception:
        return f"{symbol}{v}"

templates.env.filters["currency"] = fmt_currency

@app.get("/", response_class=HTMLResponse)
def index(request: Request):
    with Session(engine) as session:
        account = session.exec(select(Account)).first()
        if not account:
            return templates.TemplateResponse("index.html", {"request": request, "account_id": None, "snapshots": [], "transactions": [], "positions": {}, "method": "FIFO"})
        snapshots = session.exec(select(Snapshot).where(Snapshot.account_id == account.id).order_by(Snapshot.date)).all()
        transactions = get_transactions_for_account(session, account.id)
        prices = latest_prices(session)
        positions = compute_positions(transactions, prices=prices, method="FIFO")
    return templates.TemplateResponse(
        "index.html",
        {
            "request": request,
            "account_id": account.id,
            "snapshots": snapshots,
            "transactions": transactions,
            "positions": positions,
            "method": "FIFO"
        }
    )

@app.post("/accounts/{account_id}/transactions", response_class=HTMLResponse)
def add_transaction(request: Request, account_id: str, date: str = Form(...), ticker: str = Form(...),
                    quantity: float = Form(...), price: float = Form(...), fees: float = Form(0.0),
                    type: str = Form("buy"), notes: str = Form(None)):
    date_obj = datetime.strptime(date, "%Y-%m-%d").date()
    tx = Transaction(account_id=account_id, date=date_obj, ticker=ticker.upper(),
                     quantity=quantity, price=price, fees=fees, type=type, notes=notes)
    with Session(engine) as session:
        tx = create_transaction(session, tx)
        txs = get_transactions_for_account(session, account_id)
    return templates.TemplateResponse("partials/portfolio_table.html", {"request": request, "transactions": txs})

@app.get("/api/accounts/{account_id}/snapshots")
def snapshots_json(account_id: str):
    with Session(engine) as session:
        snaps = session.exec(select(Snapshot).where(Snapshot.account_id == account_id).order_by(Snapshot.date)).all()
    return [{"date": s.date.isoformat(), "value": s.total_value} for s in snaps]

@app.get("/api/holdings/{account_id}")
def holdings_json(account_id: str, method: str = "FIFO"):
    with Session(engine) as session:
        txs = get_transactions_for_account(session, account_id)
        positions = compute_positions(txs, prices=latest_prices(session), method=method)
    out = []
    for p in positions.values():
        out.append({
            "ticker": p.ticker,
            "quantity": p.quantity,
            "avg_cost": p.avg_cost,
            "basis": p.basis,
            "market_value": p.market_value,
            "unrealized_gain": p.unrealized_gain,
            "realized_gain": p.realized_gain,
        })
    return out

@app.get("/export/transactions.csv")
def export_transactions():
    with Session(engine) as session:
        rows = session.exec(select(Transaction).order_by(Transaction.date)).all()
    buf = io.StringIO()
    w = csv.writer(buf)
    w.writerow(["id","account_id","date","ticker","quantity","price","fees","type","notes"])
    for r in rows:
        w.writerow([r.id, r.account_id, r.date.isoformat(), r.ticker, r.quantity, r.price, r.fees, r.type, r.notes or ""])
    buf.seek(0)
    return StreamingResponse(iter([buf.getvalue()]), media_type="text/csv", headers={"Content-Disposition":"attachment; filename=transactions.csv"})

@app.get("/export/snapshots.csv")
def export_snapshots():
    with Session(engine) as session:
        rows = session.exec(select(Snapshot).order_by(Snapshot.date)).all()
    buf = io.StringIO()
    w = csv.writer(buf)
    w.writerow(["id","account_id","date","total_value"])
    for r in rows:
        w.writerow([r.id, r.account_id, r.date.isoformat(), r.total_value])
    buf.seek(0)
    return StreamingResponse(iter([buf.getvalue()]), media_type="text/csv", headers={"Content-Disposition":"attachment; filename=snapshots.csv"})

@app.post("/import/csv/{account_id}", response_class=HTMLResponse)
async def import_csv(request: Request, account_id: str, file: UploadFile = File(...)):
    content = await file.read()
    text = content.decode("utf-8")
    reader = csv.DictReader(io.StringIO(text))
    to_add = []
    for row in reader:
        try:
            d = datetime.strptime(row["date"], "%Y-%m-%d").date()
            tx = Transaction(
                account_id=account_id,
                date=d,
                ticker=row["ticker"].upper(),
                quantity=float(row["quantity"]),
                price=float(row["price"]),
                fees=float(row.get("fees") or 0.0),
                type=row.get("type","buy"),
                notes=row.get("notes")
            )
            to_add.append(tx)
        except Exception:
            continue
    with Session(engine) as session:
        for tx in to_add:
            session.add(tx)
        session.commit()
        txs = get_transactions_for_account(session, account_id)
    return templates.TemplateResponse("partials/portfolio_table.html", {"request": request, "transactions": txs})
