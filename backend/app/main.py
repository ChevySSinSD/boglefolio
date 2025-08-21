from fastapi import FastAPI
from contextlib import asynccontextmanager
from .database import create_db_and_tables

@asynccontextmanager
async def lifespan(app: FastAPI):
    create_db_and_tables()
    yield

app = FastAPI(title="Boglefolio", lifespan=lifespan)

@app.get("/")
def read_root() -> dict[str, str]:
    return {"message": "Welcome to Boglefolio!"}
