from typing import List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from ...api.deps import require_role
from ...database import get_db
from ...models import User
from ...schemas.vente import VenteCreate, VenteResponse, VenteUpdate
from ...services.vente_service import (
    create_vente,
    delete_vente,
    get_vente,
    list_ventes,
    update_vente,
)

router = APIRouter(prefix="/ventes", tags=["ventes"])


@router.get("", response_model=List[VenteResponse])
def read_ventes(
    current_user: User = Depends(require_role("read")),
    db: Session = Depends(get_db),
):
    return list_ventes(db)


@router.get("/{vente_id}", response_model=VenteResponse)
def read_vente(
    vente_id: int,
    current_user: User = Depends(require_role("read")),
    db: Session = Depends(get_db),
):
    obj = get_vente(db, vente_id)
    if obj is None:
        raise HTTPException(status_code=404, detail="Vente introuvable")
    return obj


@router.post("", response_model=VenteResponse)
def create_vente_route(
    data: VenteCreate,
    current_user: User = Depends(require_role("read_write")),
    db: Session = Depends(get_db),
):
    return create_vente(db, data)


@router.put("/{vente_id}", response_model=VenteResponse)
def update_vente_route(
    vente_id: int,
    data: VenteUpdate,
    current_user: User = Depends(require_role("read_write")),
    db: Session = Depends(get_db),
):
    updated = update_vente(db, vente_id, data)
    if updated is None:
        raise HTTPException(status_code=404, detail="Vente introuvable")
    return updated


@router.delete("/{vente_id}")
def delete_vente_route(
    vente_id: int,
    current_user: User = Depends(require_role("admin")),
    db: Session = Depends(get_db),
):
    if not delete_vente(db, vente_id):
        raise HTTPException(status_code=404, detail="Vente introuvable")
    return {"detail": "Vente supprimée"}
