from fastapi import APIRouter, Request, Form, Depends, HTTPException, status
from fastapi.responses import RedirectResponse, HTMLResponse
from fastapi.templating import Jinja2Templates
from sqlmodel import Session, select
from ..oidc import oauth
from ..auth import authenticate_user, create_access_token, get_password_hash
from ..database import get_session
from ..models import User
from ..dependencies import get_current_user_web
from datetime import timedelta
import os

router = APIRouter(tags=["auth"])
templates = Jinja2Templates(directory="frontend/templates")

# Dashboard route (protected)
@router.get("/dashboard", response_class=HTMLResponse)
async def dashboard(request: Request, current_user: User = Depends(get_current_user_web)):
    return templates.TemplateResponse("dashboard.html", {
        "request": request,
        "user": current_user
    })

# Profile route (protected)
@router.get("/profile", response_class=HTMLResponse) 
async def profile(request: Request, current_user: User = Depends(get_current_user_web)):
    return templates.TemplateResponse("profile.html", {
        "request": request,
        "user": current_user
    })

# Main login page - shows choice between username/password and SSO
@router.get("/login", response_class=HTMLResponse)
async def login_choice(request: Request):
    # Redirect to dashboard if already logged in
    if request.session.get("user"):
        return RedirectResponse(url="/dashboard")
    return templates.TemplateResponse("login_choice.html", {"request": request})

# Username/Password login form
@router.get("/login/form", response_class=HTMLResponse)
async def login_form(request: Request, error: str = None):
    if request.session.get("user"):
        return RedirectResponse(url="/dashboard")
    return templates.TemplateResponse("login.html", {"request": request, "error": error})

@router.post("/login/form")
async def login_submit(
    request: Request,
    username: str = Form(...),
    password: str = Form(...),
    session: Session = Depends(get_session)
):
    user = authenticate_user(session, username, password)
    if not user:
        return templates.TemplateResponse(
            "login.html", 
            {"request": request, "error": "Invalid username or password"}
        )
    
    # Create JWT token
    access_token_expires = timedelta(minutes=30)
    access_token = create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    
    # Store in session for web UI
    request.session["user"] = {"username": user.username, "id": str(user.id)}
    
    # Redirect to dashboard
    response = RedirectResponse(url="/dashboard", status_code=status.HTTP_302_FOUND)
    response.set_cookie(key="access_token", value=f"Bearer {access_token}", httponly=True)
    return response

# Registration form
@router.get("/register", response_class=HTMLResponse)
async def register_form(request: Request, error: str = None, success: str = None):
    if request.session.get("user"):
        return RedirectResponse(url="/dashboard")
    return templates.TemplateResponse("register.html", {
        "request": request, 
        "error": error, 
        "success": success
    })

@router.post("/register")
async def register_submit(
    request: Request,
    username: str = Form(...),
    email: str = Form(...),
    password: str = Form(...),
    confirm_password: str = Form(...),
    session: Session = Depends(get_session)
):
    # Validate passwords match
    if password != confirm_password:
        return templates.TemplateResponse(
            "register.html",
            {"request": request, "error": "Passwords do not match"}
        )
    
    # Check password length
    if len(password) < 8:
        return templates.TemplateResponse(
            "register.html",
            {"request": request, "error": "Password must be at least 8 characters long"}
        )
    
    # Check if user exists
    existing_user = session.exec(select(User).where(User.username == username)).first()
    if existing_user:
        return templates.TemplateResponse(
            "register.html",
            {"request": request, "error": "Username already exists"}
        )
    
    # Check if email exists
    existing_email = session.exec(select(User).where(User.email == email)).first()
    if existing_email:
        return templates.TemplateResponse(
            "register.html",
            {"request": request, "error": "Email already registered"}
        )
    
    try:
        # Create new user
        hashed_password = get_password_hash(password)
        db_user = User(
            username=username,
            email=email,
            password_hash=hashed_password
        )
        session.add(db_user)
        session.commit()
        session.refresh(db_user)
        
        return templates.TemplateResponse(
            "register.html",
            {"request": request, "success": "Account created successfully! You can now login."}
        )
        
    except Exception as e:
        return templates.TemplateResponse(
            "register.html",
            {"request": request, "error": f"Error creating account: {str(e)}"}
        )

# Authelia SSO login
@router.get("/login/sso")
async def oidc_login(request: Request):
    if request.session.get("user"):
        return RedirectResponse(url="/dashboard")
    redirect_uri = "http://192.168.88.50:8000/login/callback"
    print(f"Redirect URI being sent: {redirect_uri}")
    return await oauth.oidc.authorize_redirect(request, redirect_uri)

@router.get("/login/callback")
async def auth_callback(request: Request):
    token = await oauth.oidc.authorize_access_token(request)
    user = await oauth.oidc.parse_id_token(request, token)
    request.session["user"] = dict(user)
    return RedirectResponse(url="/dashboard")

# Logout
@router.post("/logout")
async def logout(request: Request):
    request.session.clear()
    response = RedirectResponse(url="/login")
    response.delete_cookie("access_token")
    return response