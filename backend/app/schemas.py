from pydantic import BaseModel
from enum import Enum

class DataSource(str, Enum):
    YAHOO = "Yahoo"
    MANUAL = "Manual"
    OTHER = "Other"

class AssetCreate(BaseModel):
    symbol: str
    name: str | None = None
    currency: str = "USD"
    data_source: DataSource = DataSource.YAHOO