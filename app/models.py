import uuid
from datetime import date
from typing import Optional

from sqlmodel import Field, SQLModel


def uuid_gen() -> str:
    return str(uuid.uuid4())

class User(SQLModel, table=True):
    id: str = Field(default_factory=uuid_gen, primary_key=True, index=True)
    username: str = Field(index=True, unique=True)
    display_name: Optional[str] = None
    email: Optional[str] = None

class Account(SQLModel, table=True):
    id: str = Field(default_factory=uuid_gen, primary_key=True, index=True)
    user_id: str = Field(foreign_key="user.id")
    name: str
    currency: str = Field(default="USD")

class Transaction(SQLModel, table=True):
    id: str = Field(default_factory=uuid_gen, primary_key=True, index=True)
    account_id: str = Field(foreign_key="account.id", index=True)
    date: date
    ticker: str = Field(index=True)
    quantity: float
    price: float
    fees: float = 0.0
    type: str  # 'buy' / 'sell' / 'dividend' / 'cash'
    notes: Optional[str] = None

class Snapshot(SQLModel, table=True):
    id: str = Field(default_factory=uuid_gen, primary_key=True, index=True)
    account_id: str = Field(foreign_key="account.id", index=True)
    date: date
    total_value: float

class TickerPrice(SQLModel, table=True):
    id: str = Field(default_factory=uuid_gen, primary_key=True)
    ticker: str = Field(index=True)
    as_of: date
    price: float
