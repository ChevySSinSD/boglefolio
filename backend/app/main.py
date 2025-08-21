from fastapi import FastAPI
from contextlib import asynccontextmanager
from .database import create_db_and_tables
from app.routes.assets import router as assets_router
from app.routes.accounts import router as accounts_router
from app.routes.users import router as users_router
from app.routes.transactions import router as transactions_router

@asynccontextmanager
async def lifespan(app: FastAPI):
    create_db_and_tables()
    yield

app = FastAPI(title="Boglefolio", lifespan=lifespan)
app.include_router(router=assets_router)
app.include_router(router=accounts_router)
app.include_router(router=users_router)
app.include_router(router=transactions_router)

@app.get(path="/")
def read_root() -> dict[str, str]:
    return {"message": "Welcome to Boglefolio!"}