from fastapi import APIRouter, HTTPException, status, Depends
from sqlmodel import Session, select
from app.models import User
from app.database import get_session
from app.schemas import UserCreate, UserRead, UserUpdate
from typing import Any, List, Sequence
import uuid

router = APIRouter(prefix="/users", tags=["users"])

@router.post(path="/", response_model=UserRead, status_code=status.HTTP_201_CREATED)
def create_user(user: UserCreate, session: Session = Depends(dependency=get_session)) -> UserRead:
    db_user: User = User.model_validate(obj=user)
    session.add(instance=db_user)
    session.commit()
    session.refresh(instance=db_user)
    return UserRead.model_validate(obj=db_user)

@router.get(path="/", response_model=List[UserRead])
def read_users(session: Session = Depends(dependency=get_session)) -> Sequence[UserRead]:
    users: Sequence[User] = session.exec(statement=select(User)).all()
    return [UserRead.model_validate(obj=user) for user in users]

@router.get(path="/{user_id}", response_model=UserRead)
def read_user(user_id: uuid.UUID, session: Session = Depends(dependency=get_session)) -> UserRead:
    user: User | None = session.get(entity=User, ident=user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return UserRead.model_validate(obj=user)

@router.delete(path="/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_user(user_id: uuid.UUID, session: Session = Depends(dependency=get_session)) -> None:
    user: User | None = session.get(entity=User, ident=user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    session.delete(instance=user)
    session.commit()

@router.patch(path="/{user_id}", response_model=UserRead)
def update_user(user_id: uuid.UUID, user_update: UserUpdate, session: Session = Depends(dependency=get_session)) -> UserRead:
    user: User | None = session.get(entity=User, ident=user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    user_data: dict[str, Any] = user_update.model_dump(exclude_unset=True)
    for key, value in user_data.items():
        setattr(user, key, value)
    session.add(instance=user)
    session.commit()
    session.refresh(instance=user)
    return UserRead.model_validate(obj=user)