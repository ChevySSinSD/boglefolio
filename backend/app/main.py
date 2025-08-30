from typing import Any, AsyncGenerator
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from contextlib import asynccontextmanager
from .database import create_db_and_tables
from .routes.assets import router as assets_router
from .routes.accounts import router as accounts_router
from .routes.users import router as users_router
from .routes.transactions import router as transactions_router
from .routes.frontend import router as frontend_router

@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, Any]:
    create_db_and_tables()
    yield

app = FastAPI(title="Boglefolio", lifespan=lifespan)

# Include API routes with /api prefix
app.include_router(router=assets_router, prefix="/api")
app.include_router(router=accounts_router, prefix="/api")
app.include_router(router=users_router, prefix="/api")
app.include_router(router=transactions_router, prefix="/api")

# Include frontend routes
app.include_router(router=frontend_router)

# API root endpoint
@app.get(path="/api")
def read_api_root() -> dict[str, str]:
    return {"message": "Welcome to Boglefolio API!"}