from pydantic import BaseModel
from enum import Enum
import uuid

class DataSource(str, Enum):
    YAHOO = "Yahoo"
    MANUAL = "Manual"
    OTHER = "Other"

class AssetCreate(BaseModel):
    symbol: str
    name: str | None = None
    currency: str = "USD"
    data_source: DataSource = DataSource.YAHOO

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