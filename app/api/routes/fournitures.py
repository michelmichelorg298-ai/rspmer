from typing import List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from ...api.deps import require_role
from ...database import get_db
from ...models import User
from ...schemas.fourniture import FournitureCreate, FournitureResponse, FournitureUpdate
from ...services.fourniture_service import (
    create_fourniture,
    delete_fourniture,
    get_fourniture,
    list_fournitures,
    update_fourniture,
)

router = APIRouter(prefix="/fournitures", tags=["fournitures"])


@router.get("", response_model=List[FournitureResponse])
def read_fournitures(
    current_user: User = Depends(require_role("read")),
    db: Session = Depends(get_db),
):
    return list_fournitures(db)


@router.get("/{fourniture_id}", response_model=FournitureResponse)
def read_fourniture(
    fourniture_id: int,
    current_user: User = Depends(require_role("read")),
    db: Session = Depends(get_db),
):
    obj = get_fourniture(db, fourniture_id)
    if obj is None:
        raise HTTPException(status_code=404, detail="Fourniture introuvable")
    return obj


@router.post("", response_model=FournitureResponse)
def create_fourniture_route(
    data: FournitureCreate,
    current_user: User = Depends(require_role("read_write")),
    db: Session = Depends(get_db),
):
    return create_fourniture(db, data)


@router.put("/{fourniture_id}", response_model=FournitureResponse)
def update_fourniture_route(
    fourniture_id: int,
    data: FournitureUpdate,
    current_user: User = Depends(require_role("read_write")),
    db: Session = Depends(get_db),
):
    updated = update_fourniture(db, fourniture_id, data)
    if updated is None:
        raise HTTPException(status_code=404, detail="Fourniture introuvable")
    return updated


@router.delete("/{fourniture_id}")
def delete_fourniture_route(
    fourniture_id: int,
    current_user: User = Depends(require_role("admin")),
    db: Session = Depends(get_db),
):
    if not delete_fourniture(db, fourniture_id):
        raise HTTPException(status_code=404, detail="Fourniture introuvable")
    return {"detail": "Fourniture supprimée"}
