from typing import List, Optional

from sqlalchemy.orm import Session

from ..core.security import get_password_hash, verify_password
from ..models import User


def get_user(db: Session, email: str) -> Optional[User]:
    return db.query(User).filter(User.email == email).first()


def get_user_by_id(db: Session, user_id: int) -> Optional[User]:
    return db.query(User).filter(User.id == user_id).first()


def list_users(db: Session) -> List[User]:
    return db.query(User).order_by(User.id.asc()).all()


def create_user(
    db: Session,
    email: str,
    password: str,
    full_name: str,
    role: str = "read",
) -> User:
    user = User(
        email=email,
        full_name=full_name,
        hashed_password=get_password_hash(password),
        role=role,
        disabled=False,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


def delete_user(db: Session, user_id: int) -> bool:
    user = get_user_by_id(db, user_id)
    if not user:
        return False
    db.delete(user)
    db.commit()
    return True


def change_user_password(db: Session, user: User, old_password: str, new_password: str) -> bool:
    if not verify_password(old_password, user.hashed_password):
        return False
    user.hashed_password = get_password_hash(new_password)
    db.commit()
    db.refresh(user)
    return True


def authenticate_user(db: Session, email: str, password: str) -> Optional[User]:
    user = get_user(db, email)
    if not user or not verify_password(password, user.hashed_password):
        return None
    return user


def ensure_default_users(db: Session) -> None:
    default_users = [
        {
            "email": "reader@gmail.com",
            "password": "readerpass",
            "full_name": "Lecture seule",
            "role": "read",
        },
        {
            "email": "writer@gmail.com",
            "password": "writerpass",
            "full_name": "Lecture / écriture",
            "role": "read_write",
        },
        {
            "email": "directeur@gmail.com",
            "password": "directeurpass",
            "full_name": "Directeur Général",
            "role": "directeur",
        },
        {
            "email": "admin@gmail.com",
            "password": "adminpass",
            "full_name": "Administrateur",
            "role": "admin",
        },
    ]
    for user_data in default_users:
        if not get_user(db, user_data["email"]):
            create_user(
                db,
                email=user_data["email"],
                password=user_data["password"],
                full_name=user_data["full_name"],
                role=user_data["role"],
            )
