from pydantic import BaseModel
from enum import Enum
import uuid
from datetime import datetime
from typing import Optional

class DataSource(str, Enum):
    YAHOO = "Yahoo"
    MANUAL = "Manual"
    OTHER = "Other"

class TransactionType(str, Enum):
    BUY = "buy"
    SELL = "sell"
    DIVIDEND = "dividend"
    TRANSFER = "transfer"

class AssetCreate(BaseModel):
    symbol: str
    name: str | None = None
    currency: str = "USD"
    data_source: DataSource = DataSource.YAHOO
    
class AssetRead(BaseModel):
    id: uuid.UUID
    symbol: str
    name: str | None = None
    currency: str
    data_source: DataSource

    class Config:
        from_attributes = True

class AssetUpdate(BaseModel):
    symbol: str | None = None
    name: str | None = None
    currency: str | None = None
    data_source: DataSource | None = None
    
class AccountCreate(BaseModel):
    name: str | None = None
    user_id: uuid.UUID
    balance: float | None = None

class AccountRead(BaseModel):
    id: uuid.UUID
    name: str | None = None
    user_id: uuid.UUID
    balance: float

    class Config:
        from_attributes = True
        
class AccountUpdate(BaseModel):
    name: str | None = None
    user_id: uuid.UUID | None = None
    balance: float | None = None

class UserCreate(BaseModel):
    username: str
    email: str | None = None

class UserRead(BaseModel):
    id: uuid.UUID
    username: str
    email: str | None = None

    class Config:
        from_attributes = True

class UserUpdate(BaseModel):
    username: str | None = None
    email: str | None = None
    
class TransactionCreate(BaseModel):
    asset_id: uuid.UUID
    account_id: uuid.UUID
    type: TransactionType
    quantity: float
    price: float
    date: Optional[datetime] = None

class TransactionRead(BaseModel):
    id: uuid.UUID
    asset_id: uuid.UUID
    account_id: uuid.UUID
    type: str
    quantity: float
    price: float
    fee: float
    date: datetime

    class Config:
        from_attributes = True

class TransactionUpdate(BaseModel):
    asset_id: uuid.UUID | None = None
    account_id: uuid.UUID | None = None
    type: TransactionType | None = None
    quantity: float | None = None
    price: float | None = None
    fee: float | None = None
    date: datetime | None = None