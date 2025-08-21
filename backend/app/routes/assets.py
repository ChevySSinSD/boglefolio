from fastapi import APIRouter, HTTPException, status, Depends
from sqlmodel import Session, select
from app.models import Asset
from app.database import get_session
from app.schemas import AssetCreate, AssetRead
from typing import List, Sequence
import uuid

router = APIRouter(prefix="/assets", tags=["assets"])

@router.post(path="/", response_model=AssetRead, status_code=status.HTTP_201_CREATED)
def create_asset(asset: AssetCreate, session: Session = Depends(dependency=get_session)) -> AssetRead:
    db_asset: Asset = Asset.model_validate(obj=asset)
    session.add(instance=db_asset)
    session.commit()
    session.refresh(instance=db_asset)
    return AssetRead.model_validate(obj=db_asset)

@router.get(path="/", response_model=List[AssetRead])
def read_assets(session: Session = Depends(dependency=get_session)) -> Sequence[AssetRead]:
    assets: Sequence[Asset] = session.exec(statement=select(Asset)).all()
    return [AssetRead.model_validate(obj=asset) for asset in assets]

@router.get(path="/{asset_id}", response_model=AssetRead)
def read_asset(asset_id: uuid.UUID, session: Session = Depends(dependency=get_session)) -> AssetRead:
    asset: Asset | None = session.get(entity=Asset, ident=asset_id)
    if not asset:
        raise HTTPException(status_code=404, detail="Asset not found")
    return AssetRead.model_validate(obj=asset)

@router.delete(path="/{asset_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_asset(asset_id: uuid.UUID, session: Session = Depends(dependency=get_session)) -> None:
    asset: Asset | None = session.get(entity=Asset, ident=asset_id)
    if not asset:
        raise HTTPException(status_code=404, detail="Asset not found")
    session.delete(instance=asset)
    session.commit()