# Import .env first
from dotenv import load_dotenv
load_dotenv()

from typing import Any, AsyncGenerator
from fastapi import FastAPI, Request, HTTPException
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.exception_handlers import http_exception_handler
from contextlib import asynccontextmanager
from .database import create_db_and_tables
from .routes.assets import router as assets_router
from .routes.accounts import router as accounts_router
from .routes.users import router as users_router
from .routes.transactions import router as transactions_router
from .routes.auth import router as auth_router
from starlette.middleware.sessions import SessionMiddleware
import os

@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, Any]:
    create_db_and_tables()
    yield

app = FastAPI(title="Boglefolio", lifespan=lifespan)
app.add_middleware(
    middleware_class=SessionMiddleware,
    secret_key=os.environ.get("SESSION_SECRET_KEY", default="dev-secret-key")
)

# Mount static files and templates from frontend directory
app.mount("/static", StaticFiles(directory="frontend/static"), name="static")
templates = Jinja2Templates(directory="frontend/templates")

# Custom exception handler for authentication redirects
@app.exception_handler(HTTPException)
async def custom_http_exception_handler(request: Request, exc: HTTPException):
    if exc.status_code == 302 and "Location" in exc.headers:
        return RedirectResponse(url=exc.headers["Location"])
    return await http_exception_handler(request, exc)

app.include_router(router=assets_router)
app.include_router(router=accounts_router)
app.include_router(router=users_router)
app.include_router(router=transactions_router)
app.include_router(router=auth_router)

@app.get("/", response_class=HTMLResponse)
def read_root(request: Request):
    user = request.session.get("user")
    if user:
        return RedirectResponse(url="/dashboard")
    else:
        return RedirectResponse(url="/login")