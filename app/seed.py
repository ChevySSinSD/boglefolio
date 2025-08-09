import uuid
from datetime import date
from sqlmodel import Session, SQLModel, create_engine, select
from .models import User, Account, Transaction, Snapshot

DATABASE_URL = "sqlite:///./db.sqlite"
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})

def seed():
    SQLModel.metadata.create_all(engine)

    with Session(engine) as session:
        if session.exec(select(User)).first():
            return

        user = User(
            id=str(uuid.uuid4()),
            username="demo",
            display_name="Demo User",
            email="demo@example.com"
        )
        account = Account(
            id=str(uuid.uuid4()),
            user_id=user.id,
            name="Bogle Portfolio",
            currency="USD"
        )
        tx1 = Transaction(
            id=str(uuid.uuid4()),
            account_id=account.id,
            date=date(2025, 1, 15),
            ticker="VTI",
            quantity=10,
            price=230.50,
            type="buy",
            fees=0.0
        )
        tx2 = Transaction(
            id=str(uuid.uuid4()),
            account_id=account.id,
            date=date(2025, 3, 10),
            ticker="VXUS",
            quantity=5,
            price=55.20,
            type="buy",
            fees=0.0
        )
        snap1 = Snapshot(
            id=str(uuid.uuid4()),
            account_id=account.id,
            date=date(2025, 1, 15),
            total_value=2305.00
        )
        snap2 = Snapshot(
            id=str(uuid.uuid4()),
            account_id=account.id,
            date=date(2025, 3, 10),
            total_value=2576.00
        )

        session.add_all([user, account, tx1, tx2, snap1, snap2])
        session.commit()

if __name__ == "__main__":
    seed()
