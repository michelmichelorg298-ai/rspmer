from typing import List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from ...api.deps import require_role
from ...database import get_db
from ...models import User
from ...schemas.commande_retour import (
    CommandeRetourCreate,
    CommandeRetourResponse,
    CommandeRetourUpdate,
)
from ...services.commande_retour_service import (
    create_commande_retour,
    delete_commande_retour,
    get_commande_retour,
    list_commandes_retour,
    update_commande_retour,
)

router = APIRouter(prefix="/commandes-retour", tags=["commandes-retour"])


@router.get("", response_model=List[CommandeRetourResponse])
def read_commandes_retour(
    current_user: User = Depends(require_role("read")),
    db: Session = Depends(get_db),
):
    return list_commandes_retour(db)


@router.get("/{retour_id}", response_model=CommandeRetourResponse)
def read_commande_retour(
    retour_id: int,
    current_user: User = Depends(require_role("read")),
    db: Session = Depends(get_db),
):
    obj = get_commande_retour(db, retour_id)
    if obj is None:
        raise HTTPException(status_code=404, detail="Commande retour introuvable")
    return obj


@router.post("", response_model=CommandeRetourResponse)
def create_commande_retour_route(
    data: CommandeRetourCreate,
    current_user: User = Depends(require_role("read_write")),
    db: Session = Depends(get_db),
):
    return create_commande_retour(db, data)


@router.put("/{retour_id}", response_model=CommandeRetourResponse)
def update_commande_retour_route(
    retour_id: int,
    data: CommandeRetourUpdate,
    current_user: User = Depends(require_role("read_write")),
    db: Session = Depends(get_db),
):
    updated = update_commande_retour(db, retour_id, data)
    if updated is None:
        raise HTTPException(status_code=404, detail="Commande retour introuvable")
    return updated


@router.delete("/{retour_id}")
def delete_commande_retour_route(
    retour_id: int,
    current_user: User = Depends(require_role("admin")),
    db: Session = Depends(get_db),
):
    if not delete_commande_retour(db, retour_id):
        raise HTTPException(status_code=404, detail="Commande retour introuvable")
    return {"detail": "Commande retour supprimée"}
