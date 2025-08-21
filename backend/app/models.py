from sqlmodel import SQLModel, Field, Relationship
import uuid
from datetime import datetime
from app.schemas import DataSource, TransactionType

class Asset(SQLModel, table=True):
    """Table of assets held by users. One entry for each symbol/ticker and the source of pricing data

    Args:
        symbol (str): Ticker symbol of the asset.
        name (str, optional): Name of the asset.
        currency (str): Asset currency (ISO 4217 currency code). Defaults to USD.
        data_source (str, optional)): Data source for pricing data (Yahoo, manual, etc).
    """
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True, index=True)
    symbol: str = Field(max_length=10, index=True, unique=True, description="Ticker symbol of the asset")
    name: str | None = Field(default=None, max_length=100)
    currency: str = Field(default="USD", max_length=3)
    transactions: list["Transaction"] = Relationship(back_populates="asset")
    data_source: DataSource = Field(default=DataSource.YAHOO, max_length=20)

class Account(SQLModel, table=True):
    """Table of investment accounts.

    Args:
        id (uuid.UUID): Unique identifier for the account.
        name (str, optional): Name of the account.
        user_id (uuid.UUID): ID of the user who owns the account.
        balance (float): Current balance of the account.
    """
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True, index=True)
    name: str | None = Field(default=None, max_length=100)
    user_id: uuid.UUID = Field(foreign_key="user.id")
    user: "User" = Relationship(back_populates="accounts")
    balance: float | None = Field(default=0.0)
    transactions: list["Transaction"] = Relationship(back_populates="account")

class Transaction(SQLModel, table=True):
    """Table of transactions

    Args:
        id (uuid.UUID): Unique identifier for the transaction.
        asset_id (uuid.UUID): ID of the asset being transacted.
        asset (Asset): Link to asset in asset table
        account_id (uuid.UUID): ID of the account transaction is associated with.
        account (Account): Link to account in account table
        type (TransactionType): Transaction type (buy, sell, dividend, etc)
        quantity (float): Quantity (number of shares/units) of the asset being transacted.
        price (float): Price per unit of the asset.
        fee (float): Transaction fee.
        date (datetime): Date and time of the transaction.
    """
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True, index=True)
    asset_id: uuid.UUID = Field(foreign_key="asset.id", index=True)
    asset: Asset | None = Relationship(back_populates="transactions")
    account_id: uuid.UUID = Field(foreign_key="account.id", index=True)
    account: Account | None = Relationship(back_populates="transactions")
    type: TransactionType = Field(default=TransactionType.BUY, max_length=20)
    quantity: float = Field(default=0, ge=0)
    price: float = Field(default=0, ge=0)
    fee: float = Field(default=0, ge=0)
    date: datetime = Field(default_factory=datetime.now, index=True)

class User(SQLModel, table=True):
    """Table of users

    Args:
        id (uuid.UUID): Unique identifier for the user.
        username (str): Username of the user.
        email (str): Email address of the user.
        accounts (list[Account]): Link to accounts table for all accounts owned by this user.
    """
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True, index=True)
    username: str = Field(max_length=50, unique=True, index=True)
    email: str | None = Field(default=None, max_length=100, unique=True)
    accounts: list[Account] = Relationship(back_populates="user")