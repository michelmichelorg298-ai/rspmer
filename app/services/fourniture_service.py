from typing import List, Optional

from sqlalchemy.orm import Session

from ..models import Fourniture
from ..schemas.fourniture import FournitureCreate, FournitureUpdate
from .product_service import adjust_stock, get_or_create_product_by_name


def list_fournitures(db: Session) -> List[Fourniture]:
    return db.query(Fourniture).order_by(Fourniture.date_obtenu.desc(), Fourniture.id.desc()).all()


def get_fourniture(db: Session, fourniture_id: int) -> Optional[Fourniture]:
    return db.query(Fourniture).filter(Fourniture.id == fourniture_id).first()


def create_fourniture(db: Session, data: FournitureCreate) -> Fourniture:
    payload = data.model_dump()
    nom_texte = payload.get("nom_produit_texte") or ""
    product_id = payload.get("product_id")

    if not product_id and nom_texte:
        prod = get_or_create_product_by_name(
            db, nom_texte, initial_stock=0.0, prix_achat_ref=payload.get("prix_par_kg")
        )
        payload["product_id"] = prod.id

    obj = Fourniture(**payload)
    db.add(obj)
    if obj.product_id and obj.kilo_produit:
        adjust_stock(db, obj.product_id, +float(obj.kilo_produit))
    db.commit()
    db.refresh(obj)
    return obj


def update_fourniture(
    db: Session, fourniture_id: int, data: FournitureUpdate
) -> Optional[Fourniture]:
    existing = get_fourniture(db, fourniture_id)
    if existing is None:
        return None
    old_product_id = existing.product_id
    old_kilo = existing.kilo_produit or 0.0
    new_data = data.model_dump(exclude_unset=True)
    new_product_id = new_data.get("product_id", old_product_id)
    new_kilo = new_data.get("kilo_produit", old_kilo)
    if old_product_id and old_kilo:
        adjust_stock(db, old_product_id, -float(old_kilo))
    if new_product_id and new_kilo:
        adjust_stock(db, new_product_id, +float(new_kilo))
    for k, v in new_data.items():
        setattr(existing, k, v)
    db.commit()
    db.refresh(existing)
    return existing


def delete_fourniture(db: Session, fourniture_id: int) -> bool:
    existing = get_fourniture(db, fourniture_id)
    if existing is None:
        return False
    if existing.product_id and existing.kilo_produit:
        adjust_stock(db, existing.product_id, -float(existing.kilo_produit))
    db.delete(existing)
    db.commit()
    return True
