from sqlmodel import SQLModel, Field
from typing import Optional

class Investment(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str
    amount: float
    date: str  # ISO format date
