from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from ...api.deps import require_role
from ...database import get_db
from ...models import User
from ...schemas.user import UserCreate, UserResponse
from ...services.user_service import (
    create_user,
    delete_user,
    get_user,
    get_user_by_id,
    list_users,
)

router = APIRouter(prefix="/users", tags=["users"])


@router.get("", response_model=List[UserResponse])
def read_users_route(
    current_user: User = Depends(require_role("admin")),
    db: Session = Depends(get_db),
):
    return list_users(db)


@router.post("", response_model=UserResponse)
def create_user_route(
    data: UserCreate,
    current_user: User = Depends(require_role("admin")),
    db: Session = Depends(get_db),
):
    existing = get_user(db, data.email)
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Un utilisateur avec cet email existe déjà",
        )
    return create_user(
        db,
        email=data.email,
        password=data.password,
        full_name=data.full_name or "",
        role=data.role,
    )


@router.delete("/{user_id}")
def delete_user_route(
    user_id: int,
    current_user: User = Depends(require_role("admin")),
    db: Session = Depends(get_db),
):
    if current_user.id == user_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Vous ne pouvez pas supprimer votre propre compte",
        )
    target = get_user_by_id(db, user_id)
    if not target:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Utilisateur introuvable",
        )
    delete_user(db, user_id)
    return {"detail": "Utilisateur supprimé avec succès"}
