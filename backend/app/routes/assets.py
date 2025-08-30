from fastapi import APIRouter, HTTPException, status, Depends
from pandas import DataFrame
from datetime import datetime
from sqlmodel import Session, select
from ..models import Asset
from ..database import get_session
from ..schemas import AssetCreate, AssetRead, AssetUpdate, DataSource
from ...services.yahoo import get_yahoo_price, get_yahoo_history
from typing import Any, List, Sequence
import uuid
from enum import Enum
from ..schemas import IntervalEnum

router = APIRouter(prefix="/assets", tags=["assets"])

@router.post(path="/", response_model=AssetRead, status_code=status.HTTP_201_CREATED)
def create_asset(asset: AssetCreate, session: Session = Depends(dependency=get_session)) -> AssetRead:
    # Check for duplicate by symbol (or other unique field)
    existing_asset = session.exec(select(Asset).where(Asset.symbol == asset.symbol)).first()
    if existing_asset:
        raise HTTPException(status_code=409, detail="Asset with this symbol already exists")
    db_asset: Asset = Asset.model_validate(obj=asset)
    session.add(instance=db_asset)
    session.commit()
    session.refresh(instance=db_asset)
    return AssetRead.model_validate(obj=db_asset)

@router.get(path="/", response_model=List[AssetRead])
def read_assets(
    session: Session = Depends(dependency=get_session),
    offset: int = 0,
    limit: int = 100
) -> Sequence[AssetRead]:
    assets: Sequence[Asset] = session.exec(
        statement=select(Asset).offset(offset=offset).limit(limit=limit)
    ).all()
    return [AssetRead.model_validate(obj=asset) for asset in assets]

@router.get(path="/{asset_id}", response_model=AssetRead)
def read_asset(asset_id: uuid.UUID, session: Session = Depends(dependency=get_session)) -> AssetRead:
    asset: Asset | None = session.get(entity=Asset, ident=asset_id)
    if not asset:
        raise HTTPException(status_code=404, detail="Asset not found")
    return AssetRead.model_validate(obj=asset)

@router.get(path="/{asset_id}/price")
def get_asset_price(asset_id: uuid.UUID, session: Session = Depends(dependency=get_session)) -> dict[str, Any]:
    asset: Asset | None = session.get(entity=Asset, ident=asset_id)
    if not asset:
        raise HTTPException(status_code=404, detail="Asset not found")
    if asset.data_source == DataSource.YAHOO:
        price: tuple[float, datetime] | None = get_yahoo_price(asset.symbol)
        if price is None:
            raise HTTPException(status_code=404, detail="Price not found on Yahoo")
        return {"symbol": asset.symbol, "price": price[0], "price_time": price[1]}
    # For manual or other sources, implement your logic here
    raise HTTPException(status_code=400, detail="Manual price entry not implemented yet")

@router.get(path="/{asset_id}/history")
def get_asset_history(
    asset_id: uuid.UUID,
    session: Session = Depends(dependency=get_session),
    start: datetime | None = None,
    end: datetime | None = datetime.now(),
    interval: IntervalEnum | None = IntervalEnum.ONE_DAY
) -> List[dict[str, Any]]:
    asset: Asset | None = session.get(entity=Asset, ident=asset_id)
    if not asset:
        raise HTTPException(status_code=404, detail="Asset not found")
    if asset.data_source == DataSource.YAHOO:
        history: DataFrame = get_yahoo_history(symbol=asset.symbol, start=start, end=end, interval=interval)
        if history is None or history.empty:
            raise HTTPException(status_code=404, detail="History not found on Yahoo")
        return history.reset_index().to_dict(orient="records")
    # For manual or other sources, implement your logic here
    raise HTTPException(status_code=400, detail="Manual price entry not implemented yet")

@router.delete(path="/{asset_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_asset(asset_id: uuid.UUID, session: Session = Depends(dependency=get_session)) -> None:
    asset: Asset | None = session.get(entity=Asset, ident=asset_id)
    if not asset:
        raise HTTPException(status_code=404, detail="Asset not found")
    session.delete(instance=asset)
    session.commit()

@router.patch(path="/{asset_id}", response_model=AssetRead)
def update_asset(asset_id: uuid.UUID, asset_update: AssetUpdate, session: Session = Depends(dependency=get_session)) -> AssetRead:
    asset: Asset | None = session.get(entity=Asset, ident=asset_id)
    if not asset:
        raise HTTPException(status_code=404, detail="Asset not found")
    asset_data: dict[str, Any] = asset_update.model_dump(exclude_unset=True)
    for key, value in asset_data.items():
        setattr(asset, key, value)
    session.add(instance=asset)
    session.commit()
    session.refresh(instance=asset)
    return AssetRead.model_validate(obj=asset)