from fastapi import Depends, HTTPException, status, Request
from fastapi.responses import RedirectResponse
from sqlmodel import Session, select
from .database import get_session
from .models import User
from .auth import get_current_user_jwt

# Dependency for web routes (redirects to login)
async def get_current_user_web(request: Request, session: Session = Depends(get_session)) -> User:
    """
    Dependency for web routes that require authentication.
    Redirects to login page if not authenticated.
    """
    user_session = request.session.get("user")
    if not user_session:
        raise HTTPException(
            status_code=status.HTTP_302_FOUND,
            detail="Not authenticated",
            headers={"Location": "/login"}
        )
    
    # Get user from database
    user = session.exec(select(User).where(User.username == user_session["username"])).first()
    if not user:
        # Clear invalid session
        request.session.clear()
        raise HTTPException(
            status_code=status.HTTP_302_FOUND,
            detail="User not found",
            headers={"Location": "/login"}
        )
    
    return user

# Dependency for API routes (returns 401)
async def get_current_user_api(session: Session = Depends(get_session)) -> User:
    """
    Dependency for API routes that require authentication.
    Returns 401 if not authenticated (for API calls).
    """
    return await get_current_user_jwt(session=session)

# Optional user dependency (doesn't require auth)
async def get_current_user_optional(request: Request, session: Session = Depends(get_session)) -> User | None:
    """
    Dependency that returns user if authenticated, None otherwise.
    Useful for routes that show different content based on auth status.
    """
    user_session = request.session.get("user")
    if not user_session:
        return None
    
    user = session.exec(select(User).where(User.username == user_session["username"])).first()
    return user