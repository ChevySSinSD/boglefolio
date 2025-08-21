from sqlalchemy import Engine
from sqlmodel import SQLModel, create_engine

DATABASE_URL = "sqlite:///./boglefolio.db"
engine: Engine = create_engine(url=DATABASE_URL, echo=True)

def create_db_and_tables() -> None:
    SQLModel.metadata.create_all(bind=engine)
