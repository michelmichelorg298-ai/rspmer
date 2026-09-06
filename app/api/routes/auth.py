from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from pydantic import BaseModel, EmailStr
from sqlalchemy.orm import Session

from ...api.deps import get_current_active_user
from ...core.security import create_access_token
from ...database import get_db
from ...models import User
from ...schemas.auth import Token
from ...schemas.user import PasswordChange
from ...services.user_service import authenticate_user, change_user_password

router = APIRouter(tags=["auth"])


class MeResponse(BaseModel):
    id: int
    email: EmailStr
    full_name: str | None
    role: str
    disabled: bool


@router.post("/token", response_model=Token)
def login_for_access_token(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db),
):
    user = authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Email ou mot de passe invalide",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token = create_access_token({"sub": user.email, "role": user.role})
    return {"access_token": access_token, "token_type": "bearer"}


@router.get("/me", response_model=MeResponse)
def read_current_user(current_user: User = Depends(get_current_active_user)):
    return current_user


@router.post("/change-password")
def change_password_route(
    data: PasswordChange,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    if len(data.new_password) < 4:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Le nouveau mot de passe doit comporter au moins 4 caractères",
        )
    success = change_user_password(db, current_user, data.old_password, data.new_password)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Ancien mot de passe incorrect",
        )
    return {"detail": "Mot de passe modifié avec succès"}
