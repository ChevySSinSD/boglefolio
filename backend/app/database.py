from typing import Any, Generator
from sqlalchemy import Engine
from sqlmodel import SQLModel, Session, create_engine

DATABASE_URL = "sqlite:///backend/boglefolio.db"
engine: Engine = create_engine(url=DATABASE_URL, echo=True)

def create_db_and_tables() -> None:
    SQLModel.metadata.create_all(bind=engine)

def get_session() -> Generator[Session, Any, None]:
    with Session(bind=engine) as session:
        yield session